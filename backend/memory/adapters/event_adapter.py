"""
Event adapter for Cori RAG++ system.
Provides adapters for converting between core Event and RAG++ Event models.
"""

from typing import Dict, Any, Optional, List, Union
import logging

# Import core Event class
from backend.core.event_system import Event as CoreEvent

# Import RAG++ Event class
from backend.memory.models.event import Event as RAGEvent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventAdapter:
    """
    Adapter for converting between core Event and RAG++ Event models.
    Provides methods to convert from RAG++ Event to core Event and vice versa.
    """
    
    @staticmethod
    def rag_to_core(rag_event: RAGEvent) -> CoreEvent:
        """
        Convert a RAG++ Event to a core Event.
        
        Args:
            rag_event: RAG++ Event to convert
            
        Returns:
            Converted core Event
        """
        # Create a core Event with the RAG++ Event data
        core_event = CoreEvent(
            event_type="conversation",
            data={
                "role": rag_event.role,
                "content": rag_event.content,
                "metadata": rag_event.metadata,
                "original_id": rag_event.id,
                "original_timestamp": rag_event.timestamp
            }
        )
        
        logger.debug(f"Converted RAG++ Event to core Event: {rag_event.id} -> {core_event.event_type}")
        return core_event
    
    @staticmethod
    def core_to_rag(core_event: CoreEvent) -> Optional[RAGEvent]:
        """
        Convert a core Event to a RAG++ Event if possible.
        
        Args:
            core_event: Core Event to convert
            
        Returns:
            Converted RAG++ Event or None if conversion is not possible
        """
        # Check if the core Event is a conversation event
        if core_event.event_type != "conversation" or not isinstance(core_event.data, dict):
            logger.debug(f"Cannot convert core Event to RAG++ Event: {core_event.event_type}")
            return None
        
        # Extract data from the core Event
        data = core_event.data
        
        # Create a RAG++ Event with the core Event data
        rag_event = RAGEvent(
            id=data.get("original_id"),
            role=data.get("role", "system"),
            content=data.get("content", ""),
            timestamp=data.get("original_timestamp"),
            metadata=data.get("metadata", {})
        )
        
        logger.debug(f"Converted core Event to RAG++ Event: {core_event.event_type} -> {rag_event.id}")
        return rag_event
    
    @staticmethod
    def rag_to_core_batch(rag_events: List[RAGEvent]) -> List[CoreEvent]:
        """
        Convert a batch of RAG++ Events to core Events.
        
        Args:
            rag_events: List of RAG++ Events to convert
            
        Returns:
            List of converted core Events
        """
        return [EventAdapter.rag_to_core(event) for event in rag_events]
    
    @staticmethod
    def core_to_rag_batch(core_events: List[CoreEvent]) -> List[RAGEvent]:
        """
        Convert a batch of core Events to RAG++ Events.
        
        Args:
            core_events: List of core Events to convert
            
        Returns:
            List of converted RAG++ Events (excluding any that couldn't be converted)
        """
        rag_events = []
        for event in core_events:
            rag_event = EventAdapter.core_to_rag(event)
            if rag_event:
                rag_events.append(rag_event)
        return rag_events
    
    @staticmethod
    def register_rag_event_types() -> List[str]:
        """
        Register standard event types for RAG++ operations.
        
        Returns:
            List of registered event types
        """
        # Define standard event types for RAG++ operations
        rag_event_types = [
            "rag_knowledge_retrieved",
            "rag_memory_condensed",
            "rag_context_injected",
            "rag_domain_detected",
            "rag_user_preference_updated",
            "rag_feedback_received",
            "rag_conversation_started",
            "rag_conversation_ended",
            "rag_financial_knowledge_updated"
        ]
        
        logger.info(f"Registered {len(rag_event_types)} RAG++ event types")
        return rag_event_types
