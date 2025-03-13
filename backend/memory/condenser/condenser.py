"""
Condenser module for Cori RAG++ system.
Condensers are responsible for reducing the size of the event history
while preserving important information.
"""

from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod

from ..models.event import Event

class Condenser(ABC):
    """
    Abstract base class for condensers.
    Condensers are responsible for reducing the size of the event history
    while preserving important information.
    """
    
    @abstractmethod
    def condense(self, events: List[Event]) -> List[Event]:
        """
        Condense a list of events.
        
        Args:
            events: List of events to condense
            
        Returns:
            Condensed list of events
        """
        pass

class RollingCondenser(Condenser):
    """
    Rolling condenser that keeps a fixed number of events.
    """
    
    def __init__(self, max_events: int = 100):
        """
        Initialize the rolling condenser.
        
        Args:
            max_events: Maximum number of events to keep
        """
        self.max_events = max_events
    
    def condense(self, events: List[Event]) -> List[Event]:
        """
        Condense a list of events by keeping only the most recent events.
        
        Args:
            events: List of events to condense
            
        Returns:
            Condensed list of events
        """
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda event: event.timestamp)
        
        # Keep only the most recent events
        if len(sorted_events) > self.max_events:
            return sorted_events[-self.max_events:]
        
        return sorted_events

class RecentEventsCondenser(Condenser):
    """
    Recent events condenser that keeps a fixed number of events
    and adds a summary event at the beginning.
    """
    
    def __init__(self, max_events: int = 50):
        """
        Initialize the recent events condenser.
        
        Args:
            max_events: Maximum number of events to keep
        """
        self.max_events = max_events
    
    def condense(self, events: List[Event]) -> List[Event]:
        """
        Condense a list of events by keeping only the most recent events
        and adding a summary event at the beginning.
        
        Args:
            events: List of events to condense
            
        Returns:
            Condensed list of events
        """
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda event: event.timestamp)
        
        # If there are fewer events than the maximum, return all events
        if len(sorted_events) <= self.max_events:
            return sorted_events
        
        # Create a summary event
        summary_event = Event(
            role="system",
            content=f"This conversation has {len(sorted_events)} messages. "
                    f"The following are the most recent {self.max_events} messages.",
            metadata={"type": "summary", "event_count": len(sorted_events)}
        )
        
        # Keep only the most recent events
        recent_events = sorted_events[-self.max_events:]
        
        # Add the summary event at the beginning
        return [summary_event] + recent_events
