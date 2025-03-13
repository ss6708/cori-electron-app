"""
Event system for Cori backend.
Provides a global event bus for publishing and subscribing to events.
"""

from typing import Dict, List, Any, Optional, Union, Callable
import threading
import logging
import uuid
from datetime import datetime


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Event:
    """
    Event class for the event system.
    Represents an event with a type and data.
    """
    
    def __init__(self, event_type: str, data: Any = None):
        """
        Initialize an event.
        
        Args:
            event_type: Type of the event
            data: Data associated with the event
        """
        self.id = str(uuid.uuid4())
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dictionary representation of the event
        """
        return {
            "id": self.id,
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """
        Create an event from a dictionary.
        
        Args:
            data: Dictionary representation of the event
            
        Returns:
            Event instance
        """
        event = cls(
            event_type=data.get("event_type", "unknown"),
            data=data.get("data")
        )
        event.id = data.get("id", str(uuid.uuid4()))
        event.timestamp = data.get("timestamp", datetime.now().isoformat())

        return event

class EventBus:
    """
    Event bus for publishing and subscribing to events.
    Provides thread-safe operations for concurrent access.
    """
    
    def __init__(self):
        """Initialize the event bus."""
        self.subscribers: Dict[str, List[Callable]] = {}
        self.history: List[Event] = []
        self.max_history_size = 1000
        self._lock = threading.Lock()
        logger.info("EventBus initialized")
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """

        Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when an event of this type is published
        """
        with self._lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            
            if callback not in self.subscribers[event_type]:
                self.subscribers[event_type].append(callback)
                logger.debug(f"Subscribed to event type: {event_type}")
    
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Function to remove from the subscribers
        """
        with self._lock:
            if event_type in self.subscribers and callback in self.subscribers[event_type]:
                self.subscribers[event_type].remove(callback)
                logger.debug(f"Unsubscribed from event type: {event_type}")
    
    def publish(self, event: Event) -> None:
        """
        Publish an event.
        
        Args:
            event: Event to publish
        """
        with self._lock:

            # Add event to history
            self.history.append(event)
            
            # Trim history if it exceeds the maximum size
            if len(self.history) > self.max_history_size:
                self.history = self.history[-self.max_history_size:]
            
            # Get subscribers for this event type
            subscribers = self.subscribers.get(event.event_type, [])
            
            # Get subscribers for all events
            all_subscribers = self.subscribers.get("*", [])
            
            # Combine subscribers
            all_subscribers = subscribers + all_subscribers
        
        # Call subscribers outside the lock to avoid deadlocks
        for callback in all_subscribers:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event subscriber: {e}")
    
    def get_history(self, event_type: Optional[str] = None, limit: Optional[int] = None) -> List[Event]:
        """
        Get event history.
        
        Args:
            event_type: Optional event type to filter by
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        with self._lock:
            if event_type:
                events = [event for event in self.history if event.event_type == event_type]
            else:
                events = self.history.copy()
            
            if limit:
                events = events[-limit:]
            
            return events
    
    def clear_history(self) -> None:
        """Clear event history."""
        with self._lock:
            self.history = []
            logger.debug("Event history cleared")

# Global event bus instance
event_bus = EventBus()
