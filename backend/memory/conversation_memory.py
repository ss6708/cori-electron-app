"""
Conversation memory for Cori RAG++ system.
Provides storage and retrieval of conversation events.
"""

from typing import Dict, List, Any, Optional, Union
import os
import json
import threading
import logging
import uuid
from datetime import datetime

# Import models
from backend.memory.models.event import Event, CondensationEvent
from backend.memory.condenser.condenser import Condenser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationMemory:
    """
    Conversation memory for storing and retrieving conversation events.
    Provides methods for adding, retrieving, and managing conversation events.
    Thread-safe for concurrent operations.
    """
    
    def __init__(self, session_id: Optional[str] = None, user_id: Optional[str] = None, 
                 storage_dir: Optional[str] = None, condensers: Optional[List[Condenser]] = None):
        """
        Initialize the conversation memory.
        
        Args:
            session_id: Optional session ID
            user_id: Optional user ID
            storage_dir: Optional directory for storing conversation data
            condensers: Optional list of condensers to apply to the event history
        """
        self.session_id = session_id
        self.user_id = user_id
        self.storage_dir = storage_dir or os.path.join(os.getcwd(), "memory", "conversations")
        self.condensers = condensers or []
        self._condensed_events: Dict[str, List[Event]] = {}
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize events dictionary
        self.events: Dict[str, List[Event]] = {}
        
        # Thread safety
        self._lock = threading.Lock()
        
        logger.info("ConversationMemory initialized")
    
    def add_event(self, session_id: str, event: Event) -> bool:
        """
        Add an event to the conversation memory.
        
        Args:
            session_id: Session ID
            event: Event to add
            
        Returns:
            bool: True if successfully added, False otherwise
        """
        with self._lock:
            if session_id not in self.events:
                self.events[session_id] = []
            
            self.events[session_id].append(event)
            
            # Reset condensed events cache for this session
            if session_id in self._condensed_events:
                del self._condensed_events[session_id]
                
            logger.debug(f"Added event to session {session_id}: {event.id}")
            return True
    
    def add_events(self, session_id: str, events: List[Event]) -> bool:
        """
        Add multiple events to the conversation memory.
        
        Args:
            session_id: Session ID
            events: Events to add
            
        Returns:
            bool: True if successfully added, False otherwise
        """
        with self._lock:
            if session_id not in self.events:
                self.events[session_id] = []
            
            self.events[session_id].extend(events)
            
            # Reset condensed events cache for this session
            if session_id in self._condensed_events:
                del self._condensed_events[session_id]
                
            logger.debug(f"Added {len(events)} events to session {session_id}")
            return True
    
    def get_events(self, session_id: str) -> List[Event]:
        """
        Get events from the conversation memory.
        
        Args:
            session_id: Session ID
            
        Returns:
            List[Event]: List of events
        """
        return self.events.get(session_id, [])
    
    def clear_events(self, session_id: str) -> bool:
        """
        Clear events from the conversation memory.
        
        Args:
            session_id: Session ID
            
        Returns:
            bool: True if successfully cleared, False otherwise
        """
        with self._lock:
            if session_id in self.events:
                self.events[session_id] = []
                
                # Reset condensed events cache for this session
                if session_id in self._condensed_events:
                    del self._condensed_events[session_id]
                    
                logger.debug(f"Cleared events for session {session_id}")
                return True
            return False
    
    def save_events(self, session_id: str) -> bool:
        """
        Save events to storage.
        
        Args:
            session_id: Session ID
            
        Returns:
            bool: True if successfully saved, False otherwise
        """
        with self._lock:
            if session_id not in self.events:
                logger.warning(f"No events to save for session {session_id}")
                return False
            
            try:
                # Create session directory if it doesn't exist
                session_dir = os.path.join(self.storage_dir, session_id)
                os.makedirs(session_dir, exist_ok=True)
                
                # Save events to file
                events_file = os.path.join(session_dir, "events.json")
                with open(events_file, "w") as f:
                    events_data = [event.to_dict() for event in self.events[session_id]]
                    json.dump(events_data, f, indent=2)
                
                logger.info(f"Saved {len(self.events[session_id])} events for session {session_id}")
                return True
            except Exception as e:
                logger.error(f"Error saving events for session {session_id}: {e}")
                return False
    
    def load_events(self, session_id: str) -> bool:
        """
        Load events from storage.
        
        Args:
            session_id: Session ID
            
        Returns:
            bool: True if successfully loaded, False otherwise
        """
        with self._lock:
            try:
                # Check if session directory exists
                session_dir = os.path.join(self.storage_dir, session_id)
                if not os.path.exists(session_dir):
                    logger.warning(f"No session directory found for session {session_id}")
                    return False
                
                # Load events from file
                events_file = os.path.join(session_dir, "events.json")
                if not os.path.exists(events_file):
                    logger.warning(f"No events file found for session {session_id}")
                    return False
                
                with open(events_file, "r") as f:
                    events_data = json.load(f)
                    self.events[session_id] = [Event.from_dict(event_data) for event_data in events_data]
                
                # Reset condensed events cache for this session
                if session_id in self._condensed_events:
                    del self._condensed_events[session_id]
                    
                logger.info(f"Loaded {len(self.events[session_id])} events for session {session_id}")
                return True
            except Exception as e:
                logger.error(f"Error loading events for session {session_id}: {e}")
                return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete session data.
        
        Args:
            session_id: Session ID
            
        Returns:
            bool: True if successfully deleted, False otherwise
        """
        with self._lock:
            # Clear events from memory
            if session_id in self.events:
                del self.events[session_id]
            
            # Clear condensed events cache for this session
            if session_id in self._condensed_events:
                del self._condensed_events[session_id]
            
            try:
                # Delete session directory if it exists
                session_dir = os.path.join(self.storage_dir, session_id)
                if os.path.exists(session_dir):
                    import shutil
                    shutil.rmtree(session_dir)
                
                logger.info(f"Deleted session data for session {session_id}")
                return True
            except Exception as e:
                logger.error(f"Error deleting session data for session {session_id}: {e}")
                return False
    
    # Legacy methods for backward compatibility
    
    def _apply_condensers(self, session_id: str) -> None:
        """
        Apply all condensers to the event history for a session.
        
        Args:
            session_id: Session ID
        """
        if not self.condensers or session_id not in self.events:
            return
            
        events = self.events[session_id].copy()
        for condenser in self.condensers:
            events = condenser.condense(events)
        
        # Store the condensed events
        self._condensed_events[session_id] = events
    
    def condensed_events(self, session_id: str) -> List[Event]:
        """
        Get the condensed event history for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of events after applying condensers
        """
        if session_id not in self._condensed_events or self._condensed_events[session_id] is None:
            self._apply_condensers(session_id)
        
        return self._condensed_events.get(session_id, []) if session_id in self._condensed_events else self.events.get(session_id, [])
    
    def to_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Convert the condensed event history for a session to a list of messages for the LLM.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of messages in the format expected by the LLM
        """
        messages = []
        for event in self.condensed_events(session_id):
            # Convert event to message format
            try:
                if hasattr(event, 'to_message') and callable(getattr(event, 'to_message')):
                    message = getattr(event, 'to_message')()
                    if message:
                        messages.append(message)
                else:
                    # Fallback for events without to_message method
                    messages.append({
                        "role": event.role,
                        "content": event.content
                    })
            except Exception as e:
                logger.warning(f"Error converting event to message: {e}")
                # Ensure we have a fallback
                messages.append({
                    "role": getattr(event, 'role', 'system'),
                    "content": getattr(event, 'content', str(event))
                })
        
        return messages
    
    def create_condensation_event(self, session_id: str, content: str, event_ids: List[str]) -> CondensationEvent:
        """
        Create a condensation event summarizing multiple events.
        
        Args:
            session_id: Session ID
            content: The condensed content
            event_ids: IDs of the events being condensed
            
        Returns:
            A new CondensationEvent
        """
        return CondensationEvent(
            id=str(uuid.uuid4()),
            content=content,
            timestamp=datetime.utcnow().isoformat() + "Z",
            user_id=self.user_id or "default_user",
            session_id=session_id,
            original_event_ids=event_ids
        )
    
    def get_events_by_domain(self, session_id: str, domain: str) -> List[Event]:
        """
        Get events filtered by domain for a session.
        
        Args:
            session_id: Session ID
            domain: The domain to filter by
            
        Returns:
            List of events in the specified domain
        """
        events = self.get_events(session_id)
        return [
            event for event in events 
            if hasattr(event, 'domain') and getattr(event, 'domain') == domain
        ]
    
    def get_recent_events(self, session_id: str, count: int = 10) -> List[Event]:
        """
        Get the most recent events for a session.
        
        Args:
            session_id: Session ID
            count: Number of events to return
            
        Returns:
            List of the most recent events
        """
        events = self.get_events(session_id)
        return events[-count:] if events else []
