"""
Conversation memory for Cori RAG++ system.
This module provides a memory for storing and retrieving conversation events.
"""

import os
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid

from .models.event import Event
from .condenser.condenser import Condenser, RecentEventsCondenser

class ConversationMemory:
    """
    Conversation memory for storing and retrieving conversation events.
    """
    
    def __init__(
        self,
        memory_dir: str = "memory",
        condenser: Optional[Condenser] = None
    ):
        """
        Initialize the conversation memory.
        
        Args:
            memory_dir: Directory for storing memory files
            condenser: Condenser for condensing events
        """
        self.memory_dir = memory_dir
        self.condenser = condenser or RecentEventsCondenser(max_events=50)
        
        # Create memory directory if it doesn't exist
        os.makedirs(memory_dir, exist_ok=True)
        
        # Create sessions directory if it doesn't exist
        self.sessions_dir = os.path.join(memory_dir, "sessions")
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        # Create condensed directory if it doesn't exist
        self.condensed_dir = os.path.join(memory_dir, "condensed")
        os.makedirs(self.condensed_dir, exist_ok=True)
    
    def add_event(self, event: Event, session_id: str) -> None:
        """
        Add an event to the memory.
        
        Args:
            event: Event to add
            session_id: ID of the session
        """
        # Create session directory if it doesn't exist
        session_dir = os.path.join(self.sessions_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Create event file
        event_file = os.path.join(session_dir, f"{event.id}.json")
        
        # Write event to file
        with open(event_file, "w") as f:
            json.dump(event.to_dict(), f, indent=2)
    
    def get_event(self, event_id: str, session_id: str) -> Optional[Event]:
        """
        Get an event from the memory.
        
        Args:
            event_id: ID of the event
            session_id: ID of the session
            
        Returns:
            Event or None if not found
        """
        # Create event file path
        event_file = os.path.join(self.sessions_dir, session_id, f"{event_id}.json")
        
        # Check if event file exists
        if not os.path.exists(event_file):
            return None
        
        # Read event file
        with open(event_file, "r") as f:
            event_data = json.load(f)
        
        # Create event from data
        return Event.from_dict(event_data)
    
    def get_events(self, session_id: str) -> List[Event]:
        """
        Get all events for a session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            List of events
        """
        # Create session directory path
        session_dir = os.path.join(self.sessions_dir, session_id)
        
        # Check if session directory exists
        if not os.path.exists(session_dir):
            return []
        
        # Get event files
        event_files = []
        for file in os.listdir(session_dir):
            if file.endswith(".json"):
                event_files.append(os.path.join(session_dir, file))
        
        # Read event files
        events = []
        for file in event_files:
            with open(file, "r") as f:
                event_data = json.load(f)
            
            events.append(Event.from_dict(event_data))
        
        # Sort events by timestamp
        events.sort(key=lambda event: event.timestamp)
        
        return events
    
    def get_condensed_events(self, session_id: str) -> List[Event]:
        """
        Get condensed events for a session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            List of condensed events
        """
        # Get all events
        events = self.get_events(session_id)
        
        # Condense events
        condensed_events = self.condenser.condense(events)
        
        return condensed_events
    
    def save_condensed_events(self, session_id: str) -> None:
        """
        Save condensed events for a session.
        
        Args:
            session_id: ID of the session
        """
        # Get condensed events
        condensed_events = self.get_condensed_events(session_id)
        
        # Create condensed directory for session
        session_condensed_dir = os.path.join(self.condensed_dir, session_id)
        os.makedirs(session_condensed_dir, exist_ok=True)
        
        # Create condensed file
        condensed_file = os.path.join(
            session_condensed_dir,
            f"{datetime.utcnow().isoformat()}.json"
        )
        
        # Write condensed events to file
        with open(condensed_file, "w") as f:
            json.dump(
                [event.to_dict() for event in condensed_events],
                f,
                indent=2
            )
    
    def get_latest_condensed_events(self, session_id: str) -> List[Event]:
        """
        Get the latest condensed events for a session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            List of condensed events
        """
        # Create condensed directory for session
        session_condensed_dir = os.path.join(self.condensed_dir, session_id)
        
        # Check if condensed directory exists
        if not os.path.exists(session_condensed_dir):
            return self.get_condensed_events(session_id)
        
        # Get condensed files
        condensed_files = []
        for file in os.listdir(session_condensed_dir):
            if file.endswith(".json"):
                condensed_files.append(os.path.join(session_condensed_dir, file))
        
        # If no condensed files, condense events
        if not condensed_files:
            return self.get_condensed_events(session_id)
        
        # Get latest condensed file
        latest_condensed_file = max(condensed_files, key=os.path.getctime)
        
        # Read condensed file
        with open(latest_condensed_file, "r") as f:
            condensed_data = json.load(f)
        
        # Create events from data
        condensed_events = [Event.from_dict(event_data) for event_data in condensed_data]
        
        return condensed_events
    
    def get_events_since(self, session_id: str, timestamp: str) -> List[Event]:
        """
        Get events for a session since a timestamp.
        
        Args:
            session_id: ID of the session
            timestamp: Timestamp to get events since
            
        Returns:
            List of events
        """
        # Get all events
        events = self.get_events(session_id)
        
        # Filter events by timestamp
        filtered_events = [event for event in events if event.timestamp > timestamp]
        
        return filtered_events
    
    def get_events_by_role(self, session_id: str, role: str) -> List[Event]:
        """
        Get events for a session by role.
        
        Args:
            session_id: ID of the session
            role: Role to filter events by
            
        Returns:
            List of events
        """
        # Get all events
        events = self.get_events(session_id)
        
        # Filter events by role
        filtered_events = [event for event in events if event.role == role]
        
        return filtered_events
    
    def delete_event(self, event_id: str, session_id: str) -> None:
        """
        Delete an event from the memory.
        
        Args:
            event_id: ID of the event
            session_id: ID of the session
        """
        # Create event file path
        event_file = os.path.join(self.sessions_dir, session_id, f"{event_id}.json")
        
        # Check if event file exists
        if not os.path.exists(event_file):
            return
        
        # Delete event file
        os.remove(event_file)
    
    def delete_session(self, session_id: str) -> None:
        """
        Delete a session from the memory.
        
        Args:
            session_id: ID of the session
        """
        # Create session directory path
        session_dir = os.path.join(self.sessions_dir, session_id)
        
        # Check if session directory exists
        if not os.path.exists(session_dir):
            return
        
        # Delete session directory
        for file in os.listdir(session_dir):
            os.remove(os.path.join(session_dir, file))
        
        os.rmdir(session_dir)
        
        # Delete condensed directory for session
        session_condensed_dir = os.path.join(self.condensed_dir, session_id)
        
        if os.path.exists(session_condensed_dir):
            for file in os.listdir(session_condensed_dir):
                os.remove(os.path.join(session_condensed_dir, file))
            
            os.rmdir(session_condensed_dir)
    
    def get_session_ids(self) -> List[str]:
        """
        Get all session IDs.
        
        Returns:
            List of session IDs
        """
        # Get session directories
        session_ids = []
        for dir in os.listdir(self.sessions_dir):
            if os.path.isdir(os.path.join(self.sessions_dir, dir)):
                session_ids.append(dir)
        
        return session_ids
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get information about a session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Session information
        """
        # Get events
        events = self.get_events(session_id)
        
        # Get session information
        return {
            "id": session_id,
            "event_count": len(events),
            "first_event": events[0].timestamp if events else None,
            "last_event": events[-1].timestamp if events else None
        }
