"""
Base condenser classes for Cori RAG++ system.
Condensers are responsible for reducing the size of the event history
while preserving important information.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from ..models.event import Event

class Condenser(ABC):
    """
    Abstract base class for all condensers.
    Condensers are responsible for reducing the size of the event history
    while preserving important information.
    """
    
    def __init__(self, max_size: int = 100, keep_first: int = 1):
        """
        Initialize the condenser.
        
        Args:
            max_size: Maximum number of events to keep
            keep_first: Number of initial events to always keep
        """
        self.max_size = max_size
        self.keep_first = keep_first
        self._metadata_batch: Dict[str, Any] = {}
    
    @abstractmethod
    def condense(self, events: List[Event]) -> List[Event]:
        """
        Condense a sequence of events into a potentially smaller list.
        
        Args:
            events: List of events to condense
            
        Returns:
            Condensed list of events
        """
        pass
    
    def should_condense(self, events: List[Event]) -> bool:
        """
        Determine if condensation should be applied.
        
        Args:
            events: List of events to check
            
        Returns:
            True if condensation should be applied, False otherwise
        """
        return len(events) > self.max_size
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the condenser.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self._metadata_batch[key] = value
    
    def get_metadata(self, key: str) -> Optional[Any]:
        """
        Get metadata from the condenser.
        
        Args:
            key: Metadata key
            
        Returns:
            Metadata value or None if not found
        """
        return self._metadata_batch.get(key)
    
    def clear_metadata(self) -> None:
        """Clear all metadata."""
        self._metadata_batch = {}


class RollingCondenser(Condenser):
    """
    Base class for condensers that apply to rolling history.
    This type of condenser preserves the first N events and the most recent M events,
    and applies condensation to the middle section.
    """
    
    def __init__(self, max_size: int = 100, keep_first: int = 1, keep_last: int = 10):
        """
        Initialize the rolling condenser.
        
        Args:
            max_size: Maximum number of events to keep
            keep_first: Number of initial events to always keep
            keep_last: Number of recent events to always keep
        """
        super().__init__(max_size, keep_first)
        self.keep_last = keep_last
    
    def condense(self, events: List[Event]) -> List[Event]:
        """
        Condense a sequence of events into a potentially smaller list.
        
        Args:
            events: List of events to condense
            
        Returns:
            Condensed list of events
        """
        if not self.should_condense(events):
            return events
        
        # Keep the first N events
        first_events = events[:self.keep_first]
        
        # Keep the last M events
        last_events = events[-self.keep_last:] if self.keep_last > 0 else []
        
        # Condense the middle section
        middle_events = events[self.keep_first:-self.keep_last] if self.keep_last > 0 else events[self.keep_first:]
        condensed_middle = self._condense_middle(middle_events)
        
        # Combine the sections
        return first_events + condensed_middle + last_events
    
    @abstractmethod
    def _condense_middle(self, events: List[Event]) -> List[Event]:
        """
        Condense the middle section of events.
        
        Args:
            events: List of events to condense
            
        Returns:
            Condensed list of events
        """
        pass


class RecentEventsCondenser(RollingCondenser):
    """
    A simple condenser that keeps only the most recent events.
    This is the most basic form of condensation.
    """
    
    def _condense_middle(self, events: List[Event]) -> List[Event]:
        """
        Condense the middle section by keeping only the most recent events.
        
        Args:
            events: List of events to condense
            
        Returns:
            Condensed list of events
        """
        # Calculate how many events to keep from the middle section
        middle_size = self.max_size - self.keep_first - self.keep_last
        
        # If middle_size is negative or zero, return an empty list
        if middle_size <= 0:
            return []
        
        # Keep only the most recent events from the middle section
        return events[-middle_size:]
