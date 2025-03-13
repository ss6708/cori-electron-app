from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime

from ..models.event import Event, CondensationEvent

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
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add information to the current metadata batch.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self._metadata_batch[key] = value
    
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

class RollingCondenser(Condenser):
    """
    Base class for condensers that apply to rolling history.
    Keeps track of the condensation state between calls.
    """
    
    def __init__(self, max_size: int = 100, keep_first: int = 1):
        """
        Initialize the rolling condenser.
        
        Args:
            max_size: Maximum number of events to keep
            keep_first: Number of initial events to always keep
        """
        super().__init__(max_size, keep_first)
        self._condensation = []
        self._last_history_length = 0
    
    def condensed_history(self, events: List[Event]) -> List[Event]:
        """
        Apply condensation to the rolling history.
        
        Args:
            events: Current event history
            
        Returns:
            Condensed event history
        """
        # If history has been reset, reset our tracking
        if len(events) < self._last_history_length:
            self._condensation = []
            self._last_history_length = 0
        
        # Process only new events
        new_events = events[self._last_history_length:]
        results = self.condense(self._condensation + new_events)
        
        # Update state
        self._condensation = results
        self._last_history_length = len(events)
        
        return results

class RecentEventsCondenser(RollingCondenser):
    """
    Simple condenser that keeps a fixed number of recent events.
    Always keeps the first N events and the most recent M events.
    """
    
    def condense(self, events: List[Event]) -> List[Event]:
        """
        Keep only the most recent events, plus the initial events.
        
        Args:
            events: List of events to condense
            
        Returns:
            Condensed list of events
        """
        if len(events) <= self.max_size:
            return events
        
        # Keep initial events
        head = events[:self.keep_first]
        
        # Keep recent events
        tail_size = self.max_size - len(head)
        tail = events[-tail_size:] if tail_size > 0 else []
        
        return head + tail

class FinancialDomainCondenser(RollingCondenser):
    """
    Base condenser for financial domain contexts.
    Preserves critical financial modeling information while condensing history.
    """
    
    def identify_critical_events(self, events: List[Event]) -> List[Event]:
        """
        Identify domain-specific critical events to preserve.
        
        Args:
            events: List of events to analyze
            
        Returns:
            List of critical events to preserve
        """
        # This method should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement this method")
    
    def condense(self, events: List[Event]) -> List[Event]:
        """
        Preserve critical financial modeling information while condensing history.
        
        Args:
            events: List of events to condense
            
        Returns:
            Condensed list of events
        """
        if len(events) <= self.max_size:
            return events
        
        # Keep initial user requirements
        head = events[:self.keep_first]
        
        # Identify domain-specific critical events
        critical_events = self.identify_critical_events(events[self.keep_first:])
        
        # Keep recent interactions with remaining slots
        remaining_slots = self.max_size - len(head) - len(critical_events)
        tail = events[-remaining_slots:] if remaining_slots > 0 else []
        
        return head + critical_events + tail

class LBOModelingCondenser(FinancialDomainCondenser):
    """
    Condenser specialized for LBO modeling contexts.
    Preserves transaction structure, debt terms, and exit assumptions.
    """
    
    def identify_critical_events(self, events: List[Event]) -> List[Event]:
        """
        Identify critical LBO modeling events to preserve.
        
        Args:
            events: List of events to analyze
            
        Returns:
            List of critical events to preserve
        """
        # Group events by type
        transaction_events = []
        debt_events = []
        exit_events = []
        operational_events = []
        
        for event in events:
            if hasattr(event, 'domain') and getattr(event, 'domain') == 'lbo':
                if hasattr(event, 'action_type'):
                    action_type = getattr(event, 'action_type')
                    if action_type == 'transaction_structure':
                        transaction_events.append(event)
                    elif action_type == 'debt_sizing':
                        debt_events.append(event)
                    elif action_type == 'exit_analysis':
                        exit_events.append(event)
                    elif action_type == 'operational_projections':
                        operational_events.append(event)
        
        # Keep the most recent of each critical event type
        critical_events = []
        if transaction_events:
            critical_events.append(transaction_events[-1])
        if debt_events:
            critical_events.append(debt_events[-1])
        if exit_events:
            critical_events.append(exit_events[-1])
        if operational_events:
            critical_events.append(operational_events[-1])
        
        return critical_events
