from typing import Dict, List, Optional, Any, Tuple
import uuid
import os
from datetime import datetime

from .conversation_memory import ConversationMemory
from .long_term_memory import LongTermMemory
from .condenser.condenser import Condenser, RecentEventsCondenser
from .condenser.impl.llm_summarizing_condenser import LLMSummarizingCondenser
from .models.event import Event, UserMessageEvent, AssistantMessageEvent
from .utils.embedding_model import EmbeddingModel

class MemoryManager:
    """
    Manages the three-tier memory architecture for Cori.
    Coordinates between conversation memory, condensers, and long-term memory.
    """
    
    def __init__(
        self,
        session_id: str,
        user_id: str,
        db_path: Optional[str] = None,
        openai_handler = None
    ):
        """
        Initialize the memory manager.
        
        Args:
            session_id: Unique identifier for the session
            user_id: Identifier for the user
            db_path: Path to the ChromaDB database
            openai_handler: Handler for OpenAI API interactions
        """
        self.session_id = session_id
        self.user_id = user_id
        
        # Initialize embedding model
        self.embedding_model = EmbeddingModel()
        
        # Set up condensers
        self.condensers = [
            RecentEventsCondenser(max_size=100, keep_first=2)
        ]
        
        # Add LLM summarizing condenser if OpenAI handler is provided
        if openai_handler:
            self.condensers.append(
                LLMSummarizingCondenser(
                    llm_client=openai_handler,
                    max_size=50,
                    keep_first=2
                )
            )
        
        # Initialize conversation memory
        self.conversation_memory = ConversationMemory(
            session_id=session_id,
            user_id=user_id,
            condensers=self.condensers
        )
        
        # Initialize long-term memory if db_path is provided
        self.long_term_memory = None
        if db_path:
            self.long_term_memory = LongTermMemory(
                db_path=db_path or os.path.join(os.getcwd(), "data", "vector_db"),
                embedding_model=self.embedding_model,
                session_id=session_id,
                user_id=user_id
            )
    
    def add_user_message(self, content: str, domain: Optional[str] = None) -> str:
        """
        Add a user message to memory.
        
        Args:
            content: Message content
            domain: Optional domain for the message
            
        Returns:
            Event ID
        """
        event_id = str(uuid.uuid4())
        
        event = UserMessageEvent(
            id=event_id,
            timestamp=datetime.now(),
            user_id=self.user_id,
            session_id=self.session_id,
            content=content,
            domain=domain or "general"
        )
        
        self.add_event(event)
        
        return event_id
    
    def add_assistant_message(
        self,
        content: str,
        thinking_time: Optional[int] = None,
        domain: Optional[str] = None
    ) -> str:
        """
        Add an assistant message to memory.
        
        Args:
            content: Message content
            thinking_time: Optional thinking time in seconds
            domain: Optional domain for the message
            
        Returns:
            Event ID
        """
        event_id = str(uuid.uuid4())
        
        event = AssistantMessageEvent(
            id=event_id,
            timestamp=datetime.now(),
            user_id=self.user_id,
            session_id=self.session_id,
            content=content,
            thinking_time=thinking_time,
            domain=domain or "general"
        )
        
        self.add_event(event)
        
        return event_id
    
    def add_event(self, event: Event) -> None:
        """
        Add an event to memory.
        
        Args:
            event: The event to add
        """
        # Add to conversation memory
        self.conversation_memory.add_event(event)
        
        # Add to long-term memory if available
        if self.long_term_memory:
            self.long_term_memory.add_event(event)
    
    def get_conversation_messages(self) -> List[Dict[str, Any]]:
        """
        Get the conversation messages for the LLM.
        
        Returns:
            List of messages in the format expected by the LLM
        """
        return self.conversation_memory.to_messages()
    
    def search_knowledge(
        self,
        query: str,
        domain: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant knowledge.
        
        Args:
            query: The search query
            domain: Optional domain to search in
            filters: Optional metadata filters
            k: Number of results to return
            
        Returns:
            List of search results
        """
        if not self.long_term_memory:
            return []
        
        return self.long_term_memory.search(
            query=query,
            domain=domain,
            filters=filters,
            k=k
        )
    
    def add_knowledge_document(
        self,
        text: str,
        metadata: Dict[str, Any],
        domain: str = "general"
    ) -> str:
        """
        Add a knowledge document to long-term memory.
        
        Args:
            text: The document text
            metadata: Document metadata
            domain: The domain for the document
            
        Returns:
            Document ID
        """
        if not self.long_term_memory:
            raise ValueError("Long-term memory is not initialized")
        
        return self.long_term_memory.add_document(
            text=text,
            metadata=metadata,
            domain=domain
        )
    
    def clear_conversation(self) -> None:
        """Clear the conversation memory."""
        self.conversation_memory.clear()
    
    def get_domain_specific_events(self, domain: str) -> List[Event]:
        """
        Get events for a specific domain.
        
        Args:
            domain: The domain to filter by
            
        Returns:
            List of events in the specified domain
        """
        return self.conversation_memory.get_events_by_domain(domain)
    
    def get_recent_events(self, count: int = 10) -> List[Event]:
        """
        Get the most recent events.
        
        Args:
            count: Number of events to return
            
        Returns:
            List of the most recent events
        """
        return self.conversation_memory.get_recent_events(count)
