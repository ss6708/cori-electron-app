"""
Event adapter for Cori RAG++ system.
Provides adapters for converting between core Event and RAG++ Event models.
"""

from typing import Dict, Any, Optional, List, Union
import logging
import threading
import uuid
from datetime import datetime

# Import core Event class
from backend.core.event_system import Event as CoreEvent

# Import Memory Event class
from backend.memory.models.event import Event as MemoryEvent

# Import RAG++ Event classes
from backend.memory.models.rag.event import (
    Event as RAGEvent,
    FinancialModelingEvent,
    UserMessageEvent,
    AssistantMessageEvent,
    SystemMessageEvent,
    ToolCallEvent
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventAdapter:
    """
    Adapter for converting between core Event, Memory Event, and RAG Event models.
    Provides methods to convert between different event models.
    Thread-safe for concurrent operations.
    """
    
    def __init__(self):
        """
        Initialize the event adapter.
        """
        self._lock = threading.Lock()
        logger.info("EventAdapter initialized")
    
    def core_to_memory(self, core_event: CoreEvent) -> MemoryEvent:
        """
        Convert a core Event to a memory Event.
        
        Args:
            core_event: Core Event instance
            
        Returns:
            Memory Event instance
        """
        with self._lock:
            # Extract data from core event
            event_data = core_event.data if isinstance(core_event.data, dict) else {}
            
            # Create memory event
            memory_event = MemoryEvent(
                id=core_event.id,
                role=event_data.get("role", "system"),
                content=event_data.get("content", ""),
                timestamp=core_event.timestamp,
                metadata=event_data.get("metadata", {})
            )
            
            return memory_event
    
    def memory_to_core(self, memory_event: MemoryEvent) -> CoreEvent:
        """
        Convert a memory Event to a core Event.
        
        Args:
            memory_event: Memory Event instance
            
        Returns:
            Core Event instance
        """
        with self._lock:
            # Create event data
            event_data = {
                "role": memory_event.role,
                "content": memory_event.content,
                "metadata": memory_event.metadata
            }
            
            # Create core event
            core_event = CoreEvent(
                event_type="message",
                data=event_data
            )
            
            # Set id and timestamp
            core_event.id = memory_event.id
            core_event.timestamp = memory_event.timestamp
            
            return core_event
    
    def memory_to_rag(self, memory_event: MemoryEvent, user_id: str, session_id: str) -> RAGEvent:
        """
        Convert a memory Event to a RAG Event.
        
        Args:
            memory_event: Memory Event instance
            user_id: User ID
            session_id: Session ID
            
        Returns:
            RAG Event instance
        """
        with self._lock:
            # Determine event type based on role
            if memory_event.role == "user":
                rag_event = UserMessageEvent(
                    id=memory_event.id,
                    user_id=user_id,
                    session_id=session_id,
                    content=memory_event.content,
                    context=memory_event.metadata.get("context", {})
                )
            elif memory_event.role == "assistant":
                rag_event = AssistantMessageEvent(
                    id=memory_event.id,
                    user_id=user_id,
                    session_id=session_id,
                    content=memory_event.content,
                    context=memory_event.metadata.get("context", {})
                )
            else:
                rag_event = SystemMessageEvent(
                    id=memory_event.id,
                    user_id=user_id,
                    session_id=session_id,
                    content=memory_event.content,
                    context=memory_event.metadata.get("context", {})
                )
            
            # Set timestamp if available
            if hasattr(memory_event, "timestamp") and memory_event.timestamp:
                try:
                    # Convert ISO format to datetime
                    if isinstance(memory_event.timestamp, str):
                        rag_event.timestamp = datetime.fromisoformat(memory_event.timestamp.rstrip("Z"))
                except ValueError:
                    # Use current time if conversion fails
                    pass
            
            # Set domain if available in metadata
            if "domain" in memory_event.metadata:
                rag_event.domain = memory_event.metadata["domain"]
            
            return rag_event
    
    def rag_to_memory(self, rag_event: RAGEvent) -> MemoryEvent:
        """
        Convert a RAG Event to a memory Event.
        
        Args:
            rag_event: RAG Event instance
            
        Returns:
            Memory Event instance
        """
        with self._lock:
            # Determine role based on event type
            if isinstance(rag_event, UserMessageEvent):
                role = "user"
            elif isinstance(rag_event, AssistantMessageEvent):
                role = "assistant"
            else:
                role = "system"
            
            # Create metadata
            metadata = {
                "user_id": rag_event.user_id,
                "session_id": rag_event.session_id,
                "context": rag_event.context if hasattr(rag_event, "context") else {}
            }
            
            # Add domain if available
            if hasattr(rag_event, "domain"):
                metadata["domain"] = rag_event.domain
            
            # Create memory event
            memory_event = MemoryEvent(
                id=rag_event.id,
                role=role,
                content=rag_event.content if hasattr(rag_event, "content") else "",
                timestamp=rag_event.timestamp.isoformat() + "Z",
                metadata=metadata
            )
            
            return memory_event
    
    def batch_core_to_memory(self, core_events: List[CoreEvent]) -> List[MemoryEvent]:
        """
        Convert a list of core Events to memory Events.
        
        Args:
            core_events: List of core Event instances
            
        Returns:
            List of memory Event instances
        """
        return [self.core_to_memory(event) for event in core_events]
    
    def batch_memory_to_core(self, memory_events: List[MemoryEvent]) -> List[CoreEvent]:
        """
        Convert a list of memory Events to core Events.
        
        Args:
            memory_events: List of memory Event instances
            
        Returns:
            List of core Event instances
        """
        return [self.memory_to_core(event) for event in memory_events]
    
    def batch_memory_to_rag(self, memory_events: List[MemoryEvent], user_id: str, session_id: str) -> List[RAGEvent]:
        """
        Convert a list of memory Events to RAG Events.
        
        Args:
            memory_events: List of memory Event instances
            user_id: User ID
            session_id: Session ID
            
        Returns:
            List of RAG Event instances
        """
        return [self.memory_to_rag(event, user_id, session_id) for event in memory_events]
    
    def batch_rag_to_memory(self, rag_events: List[RAGEvent]) -> List[MemoryEvent]:
        """
        Convert a list of RAG Events to memory Events.
        
        Args:
            rag_events: List of RAG Event instances
            
        Returns:
            List of memory Event instances
        """
        return [self.rag_to_memory(event) for event in rag_events]
    
    def register_rag_event_types(self) -> List[str]:
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
