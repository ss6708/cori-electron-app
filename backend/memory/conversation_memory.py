"""
Conversation memory for Cori RAG++ system.
Provides mechanisms for storing and retrieving conversation events.
"""

from typing import Dict, List, Any, Optional, Union
import os
import json
import threading
import logging
from datetime import datetime

from .models.event import Event

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationMemory:
    """
    Conversation memory for storing and retrieving conversation events.
    Provides thread-safe operations for concurrent access.
    """
    
    def __init__(self, storage_dir: str = "memory/conversations"):
        """
        Initialize conversation memory.
        
        Args:
            storage_dir: Directory to store conversation data
        """
        self.storage_dir = storage_dir
        self.events: Dict[str, List[Event]] = {}
        self._lock = threading.Lock()
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        logger.info(f"ConversationMemory initialized with storage directory: {storage_dir}")
    
    def add_event(self, session_id: str, event: Event) -> None:
        """
        Add an event to the conversation memory.
        
        Args:
            session_id: Session ID
            event: Event to add
        """
        with self._lock:
            if session_id not in self.events:
                self.events[session_id] = []
            
            self.events[session_id].append(event)
            logger.debug(f"Added event to session {session_id}: {event.id}")
    
    def add_events(self, session_id: str, events: List[Event]) -> None:
        """
        Add multiple events to the conversation memory.
        
        Args:
            session_id: Session ID
            events: Events to add
        """
        with self._lock:
            if session_id not in self.events:
                self.events[session_id] = []
            
            self.events[session_id].extend(events)
            logger.debug(f"Added {len(events)} events to session {session_id}")
    
    def get_events(self, session_id: str, limit: Optional[int] = None) -> List[Event]:
        """
        Get events for a session.
        
        Args:
            session_id: Session ID
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        with self._lock:
            if session_id not in self.events:
                return []
            
            events = self.events[session_id]
            
            if limit:
                events = events[-limit:]
            
            return events
    
    def clear_events(self, session_id: str) -> None:
        """
        Clear events for a session.
        
        Args:
            session_id: Session ID
        """
        with self._lock:
            if session_id in self.events:
                self.events[session_id] = []
                logger.debug(f"Cleared events for session {session_id}")
    
    def save_events(self, session_id: str) -> bool:
        """
        Save events for a session to disk.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            if session_id not in self.events:
                logger.warning(f"No events to save for session {session_id}")
                return False
            
            session_dir = os.path.join(self.storage_dir, session_id)
            os.makedirs(session_dir, exist_ok=True)
            
            try:
                events_data = [event.to_dict() for event in self.events[session_id]]
                
                with open(os.path.join(session_dir, "events.json"), 'w') as f:
                    json.dump(events_data, f, indent=2)
                
                logger.info(f"Saved {len(events_data)} events for session {session_id}")
                return True
            except Exception as e:
                logger.error(f"Error saving events for session {session_id}: {e}")
                return False
    
    def load_events(self, session_id: str) -> bool:
        """
        Load events for a session from disk.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if successful, False otherwise
        """
        session_dir = os.path.join(self.storage_dir, session_id)
        
        if not os.path.exists(session_dir):
            logger.warning(f"No saved events found for session {session_id}")
            return False
        
        events_path = os.path.join(session_dir, "events.json")
        
        if not os.path.exists(events_path):
            logger.warning(f"No events file found for session {session_id}")
            return False
        
        try:
            with open(events_path, 'r') as f:
                events_data = json.load(f)
            
            with self._lock:
                self.events[session_id] = [Event.from_dict(data) for data in events_data]
            
            logger.info(f"Loaded {len(self.events[session_id])} events for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error loading events for session {session_id}: {e}")
            return False
    
    def get_session_ids(self) -> List[str]:
        """
        Get all session IDs.
        
        Returns:
            List of session IDs
        """
        with self._lock:
            return list(self.events.keys())
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if successful, False otherwise
        """
        session_dir = os.path.join(self.storage_dir, session_id)
        
        if not os.path.exists(session_dir):
            logger.warning(f"No saved events found for session {session_id}")
            return False
        
        try:
            import shutil
            shutil.rmtree(session_dir)
            
            with self._lock:
                if session_id in self.events:
                    del self.events[session_id]
            
            logger.info(f"Deleted session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False
