"""
Example demonstrating how to integrate the three-tier memory architecture
with the existing backend server.
"""

import os
import sys
from typing import Dict, List, Any, Optional
import uuid

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_services import OpenAIHandler
from memory.memory_manager import MemoryManager
from memory.rag_enhanced_openai import RAGEnhancedOpenAIHandler
from models import Message

class MemoryEnhancedServer:
    """
    Example class showing how to integrate the memory system with the existing server.
    This is not a complete server implementation, just a demonstration of the integration.
    """
    
    def __init__(self):
        """Initialize the memory-enhanced server."""
        # Initialize the standard OpenAI handler
        self.openai_handler = OpenAIHandler()
        
        # Dictionary to store memory managers for each session
        self.memory_managers: Dict[str, MemoryManager] = {}
        
        # Dictionary to store RAG-enhanced OpenAI handlers for each session
        self.rag_handlers: Dict[str, RAGEnhancedOpenAIHandler] = {}
        
        # Base path for vector database
        self.db_base_path = os.path.join(os.getcwd(), "data", "vector_db")
        
        # Ensure data directory exists
        os.makedirs(self.db_base_path, exist_ok=True)
    
    def _get_or_create_memory_manager(self, session_id: str, user_id: str) -> MemoryManager:
        """
        Get or create a memory manager for the session.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            Memory manager for the session
        """
        if session_id not in self.memory_managers:
            # Create a new memory manager
            db_path = os.path.join(self.db_base_path, session_id)
            
            memory_manager = MemoryManager(
                session_id=session_id,
                user_id=user_id,
                db_path=db_path,
                openai_handler=self.openai_handler
            )
            
            self.memory_managers[session_id] = memory_manager
        
        return self.memory_managers[session_id]
    
    def _get_or_create_rag_handler(self, session_id: str, user_id: str) -> RAGEnhancedOpenAIHandler:
        """
        Get or create a RAG-enhanced OpenAI handler for the session.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            RAG-enhanced OpenAI handler for the session
        """
        if session_id not in self.rag_handlers:
            # Get or create memory manager
            memory_manager = self._get_or_create_memory_manager(session_id, user_id)
            
            # Create RAG-enhanced OpenAI handler
            rag_handler = RAGEnhancedOpenAIHandler(
                memory_manager=memory_manager,
                model_name="gpt-4o"
            )
            
            self.rag_handlers[session_id] = rag_handler
        
        return self.rag_handlers[session_id]
    
    def handle_chat_request(
        self,
        messages: List[Dict[str, str]],
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        use_rag: bool = True,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle a chat request with memory enhancement.
        
        Args:
            messages: List of messages representing the conversation history
            session_id: Optional session identifier (generated if not provided)
            user_id: Optional user identifier (default: "anonymous")
            use_rag: Whether to use RAG enhancement
            domain: Optional domain for the query
            
        Returns:
            The assistant's response
        """
        # Generate session ID if not provided
        session_id = session_id or str(uuid.uuid4())
        user_id = user_id or "anonymous"
        
        # Get the user's query (last message)
        user_query = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else ""
        
        if use_rag:
            # Get or create RAG handler
            rag_handler = self._get_or_create_rag_handler(session_id, user_id)
            
            # Get memory manager
            memory_manager = self._get_or_create_memory_manager(session_id, user_id)
            
            # Add user message to memory
            memory_manager.add_user_message(user_query, domain=domain)
            
            # Get RAG-enhanced response
            response = rag_handler.get_rag_enhanced_completion(
                messages=messages,
                user_query=user_query,
                domain=domain
            )
            
            return response
        else:
            # Use standard OpenAI handler
            # Convert messages to Message objects
            message_objects = [Message.from_dict(msg) for msg in messages]
            
            # Get response from OpenAI
            response = self.openai_handler.get_completion(message_objects)
            
            # Get memory manager
            memory_manager = self._get_or_create_memory_manager(session_id, user_id)
            
            # Add user message to memory
            memory_manager.add_user_message(user_query, domain=domain)
            
            # Add assistant message to memory
            memory_manager.add_assistant_message(
                content=response.content,
                thinking_time=response.thinking_time,
                domain=domain
            )
            
            return response.to_dict()
    
    def clear_session_memory(self, session_id: str) -> bool:
        """
        Clear the memory for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if memory was cleared, False if session not found
        """
        if session_id in self.memory_managers:
            self.memory_managers[session_id].clear_conversation()
            return True
        
        return False
    
    def add_knowledge_document(
        self,
        text: str,
        metadata: Dict[str, Any],
        domain: str = "general",
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Add a knowledge document to the long-term memory.
        
        Args:
            text: Document text
            metadata: Document metadata
            domain: Document domain
            session_id: Optional session identifier (generated if not provided)
            user_id: Optional user identifier (default: "anonymous")
            
        Returns:
            Document ID if added, None if error
        """
        # Generate session ID if not provided
        session_id = session_id or str(uuid.uuid4())
        user_id = user_id or "anonymous"
        
        # Get memory manager
        memory_manager = self._get_or_create_memory_manager(session_id, user_id)
        
        try:
            # Add document to long-term memory
            doc_id = memory_manager.add_knowledge_document(
                text=text,
                metadata=metadata,
                domain=domain
            )
            
            return doc_id
        except Exception as e:
            print(f"Error adding knowledge document: {e}")
            return None

# Example usage
def example_usage():
    """Example usage of the memory-enhanced server."""
    # Create server
    server = MemoryEnhancedServer()
    
    # Add knowledge document
    doc_id = server.add_knowledge_document(
        text="LBO models typically use debt-to-EBITDA ratios of 4-6x for senior debt.",
        metadata={
            "type": "financial_knowledge",
            "domain": "lbo",
            "topic": "debt_sizing"
        },
        domain="lbo"
    )
    
    print(f"Added knowledge document with ID: {doc_id}")
    
    # Create a session
    session_id = str(uuid.uuid4())
    user_id = "example_user"
    
    # Send a chat request
    messages = [
        {"role": "user", "content": "How much senior debt should I use in my LBO model?"}
    ]
    
    response = server.handle_chat_request(
        messages=messages,
        session_id=session_id,
        user_id=user_id,
        use_rag=True,
        domain="lbo"
    )
    
    print(f"Response: {response['content']}")
    
    # Send a follow-up request
    messages.append({"role": "assistant", "content": response['content']})
    messages.append({"role": "user", "content": "What about mezzanine debt?"})
    
    response = server.handle_chat_request(
        messages=messages,
        session_id=session_id,
        user_id=user_id,
        use_rag=True,
        domain="lbo"
    )
    
    print(f"Response: {response['content']}")
    
    # Clear session memory
    server.clear_session_memory(session_id)
    print(f"Cleared memory for session: {session_id}")

if __name__ == "__main__":
    example_usage()
