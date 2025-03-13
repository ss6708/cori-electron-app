"""
Message adapter for Cori RAG++ system.
Provides adapters for converting between core Message and RAG++ message formats.
"""

from typing import Dict, Any, Optional, List, Union
import logging
import threading

# Import core Message class
from backend.models.message import Message as CoreMessage

# Import RAG++ Event class
from backend.memory.models.event import Event as RAGEvent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageAdapter:
    """
    Adapter for converting between core Message and RAG++ message formats.
    Provides methods to convert from core Message to RAG++ Event and vice versa.
    Thread-safe for concurrent operations.
    """
    
    def __init__(self):
        """Initialize the message adapter with a thread lock for thread safety."""
        self._lock = threading.Lock()
    
    def core_to_rag(self, core_message: CoreMessage) -> RAGEvent:
        """
        Convert a core Message to a RAG++ Event.
        
        Args:
            core_message: Core Message to convert
            
        Returns:
            Converted RAG++ Event
        """
        with self._lock:
            # Create metadata from core Message properties
            metadata = {}
            if core_message.thinking_time is not None:
                metadata["thinking_time"] = core_message.thinking_time
            
            metadata["displayed"] = core_message.displayed
            
            # Create a RAG++ Event with the core Message data
            rag_event = RAGEvent(
                role=core_message.role,
                content=core_message.content,
                timestamp=core_message.timestamp,
                metadata=metadata
            )
            
            logger.debug(f"Converted core Message to RAG++ Event: {core_message.role} -> {rag_event.id}")
            return rag_event
    
    def rag_to_core(self, rag_event: RAGEvent) -> CoreMessage:
        """
        Convert a RAG++ Event to a core Message.
        
        Args:
            rag_event: RAG++ Event to convert
            
        Returns:
            Converted core Message
        """
        with self._lock:
            # Extract metadata from RAG++ Event
            metadata = rag_event.metadata or {}
            thinking_time = metadata.get("thinking_time")
            displayed = metadata.get("displayed", True)
            
            # Create a core Message with the RAG++ Event data
            core_message = CoreMessage(
                role=rag_event.role,
                content=rag_event.content,
                timestamp=rag_event.timestamp,
                displayed=displayed,
                thinking_time=thinking_time
            )
            
            logger.debug(f"Converted RAG++ Event to core Message: {rag_event.id} -> {core_message.role}")
            return core_message
    
    def core_to_rag_batch(self, core_messages: List[CoreMessage]) -> List[RAGEvent]:
        """
        Convert a batch of core Messages to RAG++ Events.
        
        Args:
            core_messages: List of core Messages to convert
            
        Returns:
            List of converted RAG++ Events
        """
        with self._lock:
            return [self.core_to_rag(message) for message in core_messages]
    
    def rag_to_core_batch(self, rag_events: List[RAGEvent]) -> List[CoreMessage]:
        """
        Convert a batch of RAG++ Events to core Messages.
        
        Args:
            rag_events: List of RAG++ Events to convert
            
        Returns:
            List of converted core Messages
        """
        with self._lock:
            return [self.rag_to_core(event) for event in rag_events]
    
    def openai_format_to_rag(self, openai_message: Dict[str, str]) -> RAGEvent:
        """
        Convert an OpenAI format message to a RAG++ Event.
        
        Args:
            openai_message: OpenAI format message to convert
            
        Returns:
            Converted RAG++ Event
        """
        with self._lock:
            # Create a RAG++ Event with the OpenAI format message data
            rag_event = RAGEvent(
                role=openai_message.get("role", "user"),
                content=openai_message.get("content", "")
            )
            
            logger.debug(f"Converted OpenAI format message to RAG++ Event: {openai_message.get('role')} -> {rag_event.id}")
            return rag_event
    
    def rag_to_openai_format(self, rag_event: RAGEvent) -> Dict[str, str]:
        """
        Convert a RAG++ Event to an OpenAI format message.
        
        Args:
            rag_event: RAG++ Event to convert
            
        Returns:
            Converted OpenAI format message
        """
        with self._lock:
            # Create an OpenAI format message with the RAG++ Event data
            openai_message = {
                "role": rag_event.role,
                "content": rag_event.content
            }
            
            logger.debug(f"Converted RAG++ Event to OpenAI format message: {rag_event.id} -> {openai_message['role']}")
            return openai_message
    
    def openai_format_to_core(self, openai_message: Dict[str, str]) -> CoreMessage:
        """
        Convert an OpenAI format message to a core Message.
        
        Args:
            openai_message: OpenAI format message to convert
            
        Returns:
            Converted core Message
        """
        with self._lock:
            # Create a core Message with the OpenAI format message data
            core_message = CoreMessage(
                role=openai_message.get("role", "user"),
                content=openai_message.get("content", "")
            )
            
            logger.debug(f"Converted OpenAI format message to core Message: {openai_message.get('role')}")
            return core_message
