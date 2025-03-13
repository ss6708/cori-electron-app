"""
Session persistence system for Cori backend.
Provides mechanisms for saving and restoring conversation state.
"""
from typing import Dict, List, Any, Optional
import json
import os
import logging
from datetime import datetime
import shutil

from ..models.message import Message
from .state_management import AgentStateController, AgentState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionManager:
    """
    Manager for persisting and restoring session state.
    Handles conversation history, agent state, and metadata.
    """
    def __init__(self, storage_dir: str = "sessions"):
        self.storage_dir = storage_dir
        self.current_session_id: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        logger.info(f"SessionManager initialized with storage directory: {storage_dir}")
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        Create a new session.
        
        Args:
            session_id: Optional custom session ID
            
        Returns:
            str: The session ID
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session_id = session_id
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        # Create session directory
        session_dir = os.path.join(self.storage_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Save initial metadata
        self._save_metadata()
        
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def save_session(self, messages: List[Message], state_controller: AgentStateController, 
                    additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save the current session state.
        
        Args:
            messages: List of conversation messages
            state_controller: Agent state controller
            additional_data: Optional additional data to save
            
        Returns:
            bool: True if successfully saved, False otherwise
        """
        if not self.current_session_id:
            logger.error("Cannot save session: No active session")
            return False
        
        try:
            session_dir = os.path.join(self.storage_dir, self.current_session_id)
            
            # Save messages
            messages_data = [msg.to_dict() for msg in messages]
            with open(os.path.join(session_dir, "messages.json"), 'w') as f:
                json.dump(messages_data, f, indent=2)
            
            # Save state
            with open(os.path.join(session_dir, "state.json"), 'w') as f:
                json.dump(state_controller.to_dict(), f, indent=2)
            
            # Save additional data if provided
            if additional_data:
                with open(os.path.join(session_dir, "data.json"), 'w') as f:
                    json.dump(additional_data, f, indent=2)
            
            # Update metadata
            self.metadata["last_updated"] = datetime.now().isoformat()
            self.metadata["message_count"] = len(messages)
            self.metadata["current_state"] = state_controller.current_state
            self._save_metadata()
            
            logger.info(f"Session saved: {self.current_session_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a session by ID.
        
        Args:
            session_id: ID of the session to load
            
        Returns:
            Optional[Dict]: Session data if successful, None otherwise
        """
        session_dir = os.path.join(self.storage_dir, session_id)
        
        if not os.path.exists(session_dir):
            logger.error(f"Session not found: {session_id}")
            return None
        
        try:
            # Load messages
            messages_path = os.path.join(session_dir, "messages.json")
            if os.path.exists(messages_path):
                with open(messages_path, 'r') as f:
                    messages_data = json.load(f)
                messages = [Message.from_dict(msg) for msg in messages_data]
            else:
                messages = []
            
            # Load state
            state_path = os.path.join(session_dir, "state.json")
            if os.path.exists(state_path):
                with open(state_path, 'r') as f:
                    state_data = json.load(f)
                state_controller = AgentStateController.from_dict(state_data)
            else:
                state_controller = AgentStateController()
            
            # Load additional data
            data_path = os.path.join(session_dir, "data.json")
            if os.path.exists(data_path):
                with open(data_path, 'r') as f:
                    additional_data = json.load(f)
            else:
                additional_data = {}
            
            # Load metadata
            metadata_path = os.path.join(session_dir, "metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
            
            # Set as current session
            self.current_session_id = session_id
            
            logger.info(f"Session loaded: {session_id}")
            return {
                "messages": messages,
                "state_controller": state_controller,
                "additional_data": additional_data,
                "metadata": self.metadata
            }
        
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all available sessions with metadata.
        
        Returns:
            List[Dict]: List of session metadata
        """
        sessions = []
        
        if not os.path.exists(self.storage_dir):
            return sessions
        
        for session_id in os.listdir(self.storage_dir):
            session_dir = os.path.join(self.storage_dir, session_id)
            
            if os.path.isdir(session_dir):
                metadata_path = os.path.join(session_dir, "metadata.json")
                
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                        
                        sessions.append({
                            "session_id": session_id,
                            **metadata
                        })
                    except Exception as e:
                        logger.error(f"Error reading metadata for session {session_id}: {e}")
                        sessions.append({
                            "session_id": session_id,
                            "error": str(e)
                        })
                else:
                    # Session exists but has no metadata
                    sessions.append({
                        "session_id": session_id,
                        "created_at": "unknown",
                        "last_updated": "unknown"
                    })
        
        # Sort by last updated time (newest first)
        sessions.sort(key=lambda s: s.get("last_updated", ""), reverse=True)
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            bool: True if successfully deleted, False otherwise
        """
        session_dir = os.path.join(self.storage_dir, session_id)
        
        if not os.path.exists(session_dir):
            logger.error(f"Session not found: {session_id}")
            return False
        
        try:
            shutil.rmtree(session_dir)
            
            if self.current_session_id == session_id:
                self.current_session_id = None
                self.metadata = {}
            
            logger.info(f"Session deleted: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False
    
    def _save_metadata(self) -> None:
        """Save session metadata to file."""
        if not self.current_session_id:
            return
        
        session_dir = os.path.join(self.storage_dir, self.current_session_id)
        metadata_path = os.path.join(session_dir, "metadata.json")
        
        try:
            with open(metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")

# Create a global session manager instance
session_manager = SessionManager()
