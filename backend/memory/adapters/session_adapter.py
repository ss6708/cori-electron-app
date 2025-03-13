"""
Session adapter for Cori RAG++ system.
Provides adapters for converting between core SessionManager and RAG++ ConversationMemory.
"""

from typing import Dict, List, Any, Optional, Union
import os
import json
import threading
import logging
from datetime import datetime

# Import core classes
from backend.core.session_persistence import session_manager, SessionManager
from backend.core.state_management import AgentStateController, AgentState
from backend.models.message import Message as CoreMessage

# Import RAG++ classes
from backend.memory.conversation_memory import ConversationMemory
from backend.memory.models.event import Event as RAGEvent

# Import adapters
from backend.memory.adapters.message_adapter import MessageAdapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionAdapter:
    """
    Adapter for converting between core SessionManager and RAG++ ConversationMemory.
    Provides methods to convert between core session data and RAG++ conversation memory.
    Thread-safe for concurrent operations.
    """
    
    def __init__(self, session_manager: SessionManager = session_manager, 
                conversation_memory: Optional[ConversationMemory] = None):
        """
        Initialize the session adapter.
        
        Args:
            session_manager: Core SessionManager instance
            conversation_memory: RAG++ ConversationMemory instance
        """
        self.session_manager = session_manager
        self.conversation_memory = conversation_memory or ConversationMemory()
        self.message_adapter = MessageAdapter()
        self._lock = threading.Lock()
        
        logger.info("SessionAdapter initialized")
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        Create a new session in both core SessionManager and RAG++ ConversationMemory.
        
        Args:
            session_id: Optional custom session ID
            
        Returns:
            str: The session ID
        """
        with self._lock:
            # Create session in core SessionManager
            session_id = self.session_manager.create_session(session_id)
            
            # Clear any existing events for this session in RAG++ ConversationMemory
            self.conversation_memory.clear_events(session_id)
            
            logger.info(f"Created new session in both systems: {session_id}")
            return session_id
    
    def save_session(self, session_id: str, messages: List[CoreMessage], 
                    state_controller: AgentStateController,
                    additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save session data to both core SessionManager and RAG++ ConversationMemory.
        
        Args:
            session_id: Session ID
            messages: List of core Messages
            state_controller: Agent state controller
            additional_data: Optional additional data to save
            
        Returns:
            bool: True if successfully saved, False otherwise
        """
        with self._lock:
            # Convert core Messages to RAG++ Events
            events = self.message_adapter.core_to_rag_batch(messages)
            
            # Save events to RAG++ ConversationMemory
            self.conversation_memory.clear_events(session_id)
            self.conversation_memory.add_events(session_id, events)
            rag_saved = self.conversation_memory.save_events(session_id)
            
            # Prepare additional data with RAG++ metadata
            additional_data = additional_data or {}
            additional_data["rag_metadata"] = {
                "event_count": len(events),
                "last_updated": datetime.now().isoformat()
            }
            
            # Save to core SessionManager
            core_saved = self.session_manager.save_session(
                messages=messages,
                state_controller=state_controller,
                additional_data=additional_data
            )
            
            success = rag_saved and core_saved
            logger.info(f"Session saved to both systems: {session_id} (success: {success})")
            return success
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load session data from both core SessionManager and RAG++ ConversationMemory.
        
        Args:
            session_id: Session ID
            
        Returns:
            Optional[Dict]: Session data if successful, None otherwise
        """
        # Load from core SessionManager
        core_data = self.session_manager.load_session(session_id)
        
        if not core_data:
            logger.error(f"Failed to load session from core SessionManager: {session_id}")
            return None
        
        # Load events from RAG++ ConversationMemory
        rag_loaded = self.conversation_memory.load_events(session_id)
        
        if not rag_loaded:
            logger.warning(f"Failed to load events from RAG++ ConversationMemory: {session_id}")
            # Continue with core data only
        
        # Get events from RAG++ ConversationMemory
        events = self.conversation_memory.get_events(session_id)
        
        # Add RAG++ data to the result
        core_data["rag_events"] = events
        
        logger.info(f"Session loaded from both systems: {session_id}")
        return core_data
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete session data from both core SessionManager and RAG++ ConversationMemory.
        
        Args:
            session_id: Session ID
            
        Returns:
            bool: True if successfully deleted, False otherwise
        """
        with self._lock:
            # Delete from core SessionManager
            core_deleted = self.session_manager.delete_session(session_id)
            
            # Delete from RAG++ ConversationMemory
            rag_deleted = self.conversation_memory.delete_session(session_id)
            
            success = core_deleted and rag_deleted
            logger.info(f"Session deleted from both systems: {session_id} (success: {success})")
            return success
    
    def sync_messages_to_events(self, session_id: str, messages: List[CoreMessage]) -> bool:
        """
        Synchronize core Messages to RAG++ Events for a session.
        
        Args:
            session_id: Session ID
            messages: List of core Messages
            
        Returns:
            bool: True if successfully synchronized, False otherwise
        """
        with self._lock:
            # Convert core Messages to RAG++ Events
            events = self.message_adapter.core_to_rag_batch(messages)
            
            # Save events to RAG++ ConversationMemory
            self.conversation_memory.clear_events(session_id)
            self.conversation_memory.add_events(session_id, events)
            success = self.conversation_memory.save_events(session_id)
            
            logger.info(f"Synchronized {len(messages)} messages to {len(events)} events for session {session_id}")
            return success
    
    def sync_events_to_messages(self, session_id: str) -> List[CoreMessage]:
        """
        Synchronize RAG++ Events to core Messages for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            List[CoreMessage]: List of core Messages
        """
        with self._lock:
            # Get events from RAG++ ConversationMemory
            events = self.conversation_memory.get_events(session_id)
            
            # Convert RAG++ Events to core Messages
            messages = self.message_adapter.rag_to_core_batch(events)
            
            logger.info(f"Synchronized {len(events)} events to {len(messages)} messages for session {session_id}")
            return messages
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all available sessions with metadata.
        
        Returns:
            List[Dict]: List of session metadata
        """
        # Get sessions from core SessionManager
        return self.session_manager.list_sessions()
