"""
Event system for Cori backend.
Provides a pub/sub mechanism for decoupling components.
"""
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime
import json
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Event:
    """Base event class for the event system."""
    def __init__(self, event_type: str, data: Any = None):
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now().isoformat()
        self.id = None  # Will be set by EventBus when added
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "id": self.id,
            "type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create an Event instance from a dictionary."""
        event = cls(data["type"], data["data"])
        event.timestamp = data["timestamp"]
        event.id = data["id"]
        return event

class EventBus:
    """
    Event bus for pub/sub communication between components.
    Provides event history and filtering capabilities.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._history: List[Event] = []
        self._next_id = 0
        self._lock = threading.Lock()
        logger.info("EventBus initialized")
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type of events to subscribe to
            callback: Function to call when an event of this type is published
        """
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to event type: {event_type}")
    
    def unsubscribe(self, event_type: str, callback: Callable) -> bool:
        """
        Unsubscribe from events of a specific type.
        
        Args:
            event_type: Type of events to unsubscribe from
            callback: Function to remove from subscribers
            
        Returns:
            bool: True if successfully unsubscribed, False otherwise
        """
        with self._lock:
            if event_type in self._subscribers and callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
                logger.debug(f"Unsubscribed from event type: {event_type}")
                return True
        return False
    
    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        with self._lock:
            # Assign ID and add to history
            event.id = self._next_id
            self._next_id += 1
            self._history.append(event)
            
            # Notify subscribers
            if event.event_type in self._subscribers:
                for callback in self._subscribers[event.event_type]:
                    try:
                        callback(event)
                    except Exception as e:
                        logger.error(f"Error in event callback: {e}")
        
        logger.debug(f"Published event: {event.event_type} (ID: {event.id})")
    
    def get_history(self, event_type: Optional[str] = None, start_id: int = 0, 
                   end_id: Optional[int] = None, limit: Optional[int] = None) -> List[Event]:
        """
        Get event history with optional filtering.
        
        Args:
            event_type: Optional filter by event type
            start_id: Get events with ID >= start_id
            end_id: Get events with ID <= end_id
            limit: Maximum number of events to return
            
        Returns:
            List of events matching the criteria
        """
        with self._lock:
            # Filter by ID range
            filtered = [e for e in self._history if e.id >= start_id]
            if end_id is not None:
                filtered = [e for e in filtered if e.id <= end_id]
            
            # Filter by event type
            if event_type:
                filtered = [e for e in filtered if e.event_type == event_type]
            
            # Apply limit
            if limit:
                filtered = filtered[-limit:]
            
            return filtered
    
    def clear_history(self) -> None:
        """Clear the event history."""
        with self._lock:
            self._history = []
            logger.info("Event history cleared")
    
    def save_history(self, file_path: str) -> None:
        """
        Save event history to a file.
        
        Args:
            file_path: Path to save the history to
        """
        with self._lock:
            history_data = [event.to_dict() for event in self._history]
            
        try:
            with open(file_path, 'w') as f:
                json.dump(history_data, f, indent=2)
            logger.info(f"Event history saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving event history: {e}")
    
    def load_history(self, file_path: str) -> bool:
        """
        Load event history from a file.
        
        Args:
            file_path: Path to load the history from
            
        Returns:
            bool: True if successfully loaded, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                history_data = json.load(f)
            
            with self._lock:
                self._history = [Event.from_dict(data) for data in history_data]
                if self._history:
                    self._next_id = max(event.id for event in self._history) + 1
                else:
                    self._next_id = 0
            
            logger.info(f"Event history loaded from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading event history: {e}")
            return False

# Create a global event bus instance
event_bus = EventBus()
