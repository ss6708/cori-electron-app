"""
Server integration for Cori RAG++ system.
Provides utilities for integrating RAG++ components with the server.
"""

from typing import Dict, List, Any, Optional, Union
import os
import threading
import logging
from datetime import datetime

# Import core classes
from backend.core.event_system import event_bus, Event as CoreEvent
from backend.core.state_management import AgentStateController, AgentState
from backend.models.message import Message as CoreMessage

# Import RAG++ classes
from backend.memory.conversation_memory import ConversationMemory
from backend.memory.long_term_memory import LongTermMemory
from backend.memory.knowledge.knowledge_retriever import KnowledgeRetriever
from backend.memory.knowledge.financial_domain_detector import FinancialDomainDetector
from backend.memory.knowledge.financial_knowledge_base import FinancialKnowledgeBase
from backend.memory.rag_enhanced_openai import RAGEnhancedOpenAIHandler
from backend.memory.user_preference_store import UserPreferenceStore

# Import adapters
from backend.memory.adapters.event_adapter import EventAdapter
from backend.memory.adapters.message_adapter import MessageAdapter
from backend.memory.adapters.session_adapter import SessionAdapter
from backend.memory.adapters.state_adapter import StateAwareRAGHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGServerIntegration:
    """
    Server integration for RAG++ components.
    Provides methods for initializing and integrating RAG++ components with the server.
    """
    
    def __init__(
        self,
        state_controller: AgentStateController,
        storage_dir: str = "memory",
        rag_enabled: bool = True
    ):
        """
        Initialize the server integration.
        
        Args:
            state_controller: Core AgentStateController instance
            storage_dir: Directory to store RAG++ data
            rag_enabled: Whether RAG enhancement is enabled
        """
        self.state_controller = state_controller
        self.storage_dir = storage_dir
        self.rag_enabled = rag_enabled
        
        # Initialize components
        self.conversation_memory = None
        self.long_term_memory = None
        self.knowledge_base = None
        self.knowledge_retriever = None
        self.domain_detector = None
        self.user_preference_store = None
        self.rag_handler = None
        self.state_aware_handler = None
        
        # Initialize adapters
        self.event_adapter = None
        self.message_adapter = None
        self.session_adapter = None
        
        # Thread safety
        self._lock = threading.Lock()
        self._initialized = False
        
        logger.info("RAGServerIntegration initialized")
    
    def initialize(self) -> bool:
        """
        Initialize RAG++ components.
        
        Returns:
            bool: True if successfully initialized, False otherwise
        """
        if self._initialized:
            logger.warning("RAG++ components already initialized")
            return True
        
        try:
            with self._lock:
                # Create storage directories
                os.makedirs(self.storage_dir, exist_ok=True)
                os.makedirs(os.path.join(self.storage_dir, "conversations"), exist_ok=True)
                os.makedirs(os.path.join(self.storage_dir, "long_term"), exist_ok=True)
                os.makedirs(os.path.join(self.storage_dir, "knowledge"), exist_ok=True)
                os.makedirs(os.path.join(self.storage_dir, "preferences"), exist_ok=True)
                
                # Initialize adapters
                self.event_adapter = EventAdapter()
                self.message_adapter = MessageAdapter()
                
                # Register RAG++ event types
                self.event_adapter.register_rag_event_types()
                
                # Initialize RAG++ components
                self._initialize_components()
                
                # Initialize state-aware handler
                self.state_aware_handler = StateAwareRAGHandler(
                    state_controller=self.state_controller,
                    domain_detector=self.domain_detector,
                    knowledge_retriever=self.knowledge_retriever,
                    conversation_memory=self.conversation_memory,
                    long_term_memory=self.long_term_memory
                )
                
                # Register event handlers
                self._register_event_handlers()
                
                self._initialized = True
                logger.info("RAG++ components initialized")
                return True
                
        except Exception as e:
            logger.error(f"Error initializing RAG++ components: {e}")
            return False
    
    def _initialize_components(self) -> None:
        """Initialize RAG++ components."""
        # Initialize conversation memory
        self.conversation_memory = ConversationMemory(
            storage_dir=os.path.join(self.storage_dir, "conversations")
        )
        
        # Initialize knowledge base
        self.knowledge_base = FinancialKnowledgeBase(
            storage_dir=os.path.join(self.storage_dir, "knowledge")
        )
        
        # Initialize domain detector
        self.domain_detector = FinancialDomainDetector(
            knowledge_base=self.knowledge_base
        )
        
        # Initialize knowledge retriever
        self.knowledge_retriever = KnowledgeRetriever(
            financial_knowledge_base=self.knowledge_base
        )
        
        # Initialize long-term memory
        self.long_term_memory = LongTermMemory(
            storage_dir=os.path.join(self.storage_dir, "long_term")
        )
        
        # Initialize user preference store
        self.user_preference_store = UserPreferenceStore(
            storage_dir=os.path.join(self.storage_dir, "preferences")
        )
        
        # Initialize RAG handler
        self.rag_handler = RAGEnhancedOpenAIHandler(
            conversation_memory=self.conversation_memory,
            long_term_memory=self.long_term_memory,
            knowledge_retriever=self.knowledge_retriever,
            domain_detector=self.domain_detector,
            rag_enabled=self.rag_enabled
        )
        
        # Initialize session adapter
        from backend.core.session_persistence import session_manager
        self.session_adapter = SessionAdapter(
            session_manager=session_manager,
            conversation_memory=self.conversation_memory
        )
    
    def _register_event_handlers(self) -> None:
        """Register event handlers for RAG++ operations."""
        # Register event handlers
        event_bus.subscribe("user_message", self._handle_user_message)
        event_bus.subscribe("session_created", self._handle_session_created)
        event_bus.subscribe("session_loaded", self._handle_session_loaded)
        event_bus.subscribe("agent_state_changed", self._handle_agent_state_changed)
    
    def _handle_user_message(self, event: CoreEvent) -> None:
        """
        Handle user message events.
        
        Args:
            event: Core Event representing a user message
        """
        if not isinstance(event.data, dict):
            return
        
        data = event.data
        session_id = data.get("session_id")
        message = data.get("message")
        
        if not session_id or not message:
            return
        
        try:
            # Detect domain
            if self.domain_detector:
                domain = self.domain_detector.detect_domain(message)
                
                # Publish domain detection event
                event_bus.publish(CoreEvent(
                    event_type="rag_domain_detected",
                    data={
                        "domain": domain,
                        "query": message,
                        "session_id": session_id
                    }
                ))
        except Exception as e:
            logger.error(f"Error handling user message: {e}")
    
    def _handle_session_created(self, event: CoreEvent) -> None:
        """
        Handle session created events.
        
        Args:
            event: Core Event representing a session creation
        """
        if not isinstance(event.data, dict):
            return
        
        data = event.data
        session_id = data.get("session_id")
        
        if not session_id:
            return
        
        try:
            # Initialize conversation memory for the session
            if self.conversation_memory:
                self.conversation_memory.clear_events(session_id)
        except Exception as e:
            logger.error(f"Error handling session created: {e}")
    
    def _handle_session_loaded(self, event: CoreEvent) -> None:
        """
        Handle session loaded events.
        
        Args:
            event: Core Event representing a session load
        """
        if not isinstance(event.data, dict):
            return
        
        data = event.data
        session_id = data.get("session_id")
        
        if not session_id:
            return
        
        try:
            # Load conversation memory for the session
            if self.conversation_memory:
                self.conversation_memory.load_events(session_id)
        except Exception as e:
            logger.error(f"Error handling session loaded: {e}")
    
    def _handle_agent_state_changed(self, event: CoreEvent) -> None:
        """
        Handle agent state changed events.
        
        Args:
            event: Core Event representing an agent state change
        """
        # This is handled by the StateAwareRAGHandler
        pass
    
    def get_rag_handler(self) -> RAGEnhancedOpenAIHandler:
        """
        Get the RAG handler.
        
        Returns:
            RAGEnhancedOpenAIHandler: RAG handler
        """
        if not self._initialized:
            self.initialize()
        
        return self.rag_handler
    
    def get_session_adapter(self) -> SessionAdapter:
        """
        Get the session adapter.
        
        Returns:
            SessionAdapter: Session adapter
        """
        if not self._initialized:
            self.initialize()
        
        return self.session_adapter
    
    def get_state_aware_handler(self) -> StateAwareRAGHandler:
        """
        Get the state-aware handler.
        
        Returns:
            StateAwareRAGHandler: State-aware handler
        """
        if not self._initialized:
            self.initialize()
        
        return self.state_aware_handler
    
    def is_rag_enabled(self) -> bool:
        """
        Check if RAG enhancement is enabled.
        
        Returns:
            bool: True if RAG enhancement is enabled, False otherwise
        """
        return self.rag_enabled
    
    def set_rag_enabled(self, enabled: bool) -> None:
        """
        Set whether RAG enhancement is enabled.
        
        Args:
            enabled: Whether RAG enhancement is enabled
        """
        self.rag_enabled = enabled
        
        if self.rag_handler:
            self.rag_handler.rag_enabled = enabled
        
        logger.info(f"RAG enhancement {'enabled' if enabled else 'disabled'}")
    
    def process_feedback(
        self,
        session_id: str,
        feedback: str,
        rating: Optional[int] = None
    ) -> bool:
        """
        Process user feedback for learning.
        
        Args:
            session_id: Session ID
            feedback: User feedback text
            rating: Optional numerical rating (1-5)
            
        Returns:
            bool: True if successfully processed, False otherwise
        """
        if not self._initialized:
            self.initialize()
        
        if self.rag_handler:
            return self.rag_handler.process_feedback(
                session_id=session_id,
                feedback=feedback,
                rating=rating
            )
        
        return False
    
    def condense_memory(self, session_id: str) -> bool:
        """
        Condense conversation memory for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            bool: True if successfully condensed, False otherwise
        """
        if not self._initialized:
            self.initialize()
        
        if self.rag_handler:
            return self.rag_handler.condense_memory(session_id)
        
        return False
