from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime

from .models.event import Event, CondensationEvent
from .condenser.condenser import Condenser

class ConversationMemory:
    """
    Manages the conversation memory for a session, including event tracking and condensation.
    This is the first tier of the three-tier memory architecture.
    """
    
    def __init__(self, session_id: str, user_id: str, condensers: List[Condenser] = None):
        """
        Initialize conversation memory.
        
        Args:
            session_id: Unique identifier for the session
            user_id: Identifier for the user
            condensers: List of condensers to apply to the event history
        """
        self.session_id = session_id
        self.user_id = user_id
        self.events: List[Event] = []
        self.condensers = condensers or []
        self._condensed_events: Optional[List[Event]] = None
    
    def add_event(self, event: Event) -> None:
        """
        Add an event to the conversation history.
        
        Args:
            event: The event to add
        """
        self.events.append(event)
        self._condensed_events = None  # Reset condensed events cache
        self._apply_condensers()
    
    def _apply_condensers(self) -> None:
        """Apply all condensers to the event history."""
        if not self.condensers:
            return
            
        events = self.events.copy()
        for condenser in self.condensers:
            events = condenser.condense(events)
        
        self._condensed_events = events
    
    def condensed_events(self) -> List[Event]:
        """
        Get the condensed event history.
        
        Returns:
            List of events after applying condensers
        """
        if self._condensed_events is None:
            self._apply_condensers()
        
        return self._condensed_events or self.events
    
    def to_messages(self) -> List[Dict[str, Any]]:
        """
        Convert the condensed event history to a list of messages for the LLM.
        
        Returns:
            List of messages in the format expected by the LLM
        """
        messages = []
        for event in self.condensed_events():
            # Check if the event has a to_message method
            if hasattr(event, 'to_message') and callable(event.to_message):
                message = event.to_message()
                if message:
                    messages.append(message)
        
        return messages
    
    def clear(self) -> None:
        """Clear all events from the conversation memory."""
        self.events = []
        self._condensed_events = None
    
    def create_condensation_event(self, content: str, event_ids: List[str]) -> CondensationEvent:
        """
        Create a condensation event summarizing multiple events.
        
        Args:
            content: The condensed content
            event_ids: IDs of the events being condensed
            
        Returns:
            A new CondensationEvent
        """
        return CondensationEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_id=self.user_id,
            session_id=self.session_id,
            content=content,
            original_event_ids=event_ids
        )
    
    def get_events_by_domain(self, domain: str) -> List[Event]:
        """
        Get events filtered by domain.
        
        Args:
            domain: The domain to filter by
            
        Returns:
            List of events in the specified domain
        """
        return [
            event for event in self.events 
            if hasattr(event, 'domain') and getattr(event, 'domain') == domain
        ]
    
    def get_recent_events(self, count: int = 10) -> List[Event]:
        """
        Get the most recent events.
        
        Args:
            count: Number of events to return
            
        Returns:
            List of the most recent events
        """
        return self.events[-count:] if self.events else []
