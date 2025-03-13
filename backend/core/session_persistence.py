"""
Session persistence for Cori backend.
Provides a session manager for storing and retrieving session data.
"""

from typing import Dict, List, Any, Optional, Union
import os
import json
import threading
import logging
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionManager:
    """
    Session manager for storing and retrieving session data.
    Provides thread-safe operations for concurrent access.
    """
    
    def __init__(self, storage_dir: str = "sessions"):
        """
        Initialize the session manager.
        
        Args:
            storage_dir: Directory to store session data
        """
        self.storage_dir = storage_dir
        self.current_session_id = None
        self.sessions = {}
        self._lock = threading.Lock()
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        logger.info(f"SessionManager initialized with storage directory: {storage_dir}")
    
    def create_session(self) -> str:
        """
        Create a new session.
        
        Returns:
            Session ID
        """
        with self._lock:
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Create session directory
            session_dir = os.path.join(self.storage_dir, session_id)
            os.makedirs(session_dir, exist_ok=True)
            
            # Create metadata file
            metadata = {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            with open(os.path.join(session_dir, "metadata.json"), "w") as f:
                json.dump(metadata, f, indent=2)
            
            # Set current session ID
            self.current_session_id = session_id
            
            logger.info(f"Created session: {session_id}")
            
            return session_id
    
    def save_session(self, session_id: str, messages: List[Any], state_controller: Any = None) -> bool:
        """
        Save session data.
        
        Args:
            session_id: Session ID
            messages: List of messages
            state_controller: Optional state controller
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            # Check if session exists
            session_dir = os.path.join(self.storage_dir, session_id)
            if not os.path.exists(session_dir):
                logger.warning(f"Session not found: {session_id}")
                return False
            
            try:
                # Save messages
                messages_data = [message.to_dict() if hasattr(message, "to_dict") else message for message in messages]
                
                with open(os.path.join(session_dir, "messages.json"), "w") as f:
                    json.dump(messages_data, f, indent=2)
                
                # Save state if provided
                if state_controller:
                    state_data = {
                        "current_state": state_controller.current_state.value if hasattr(state_controller.current_state, "value") else state_controller.current_state,
                        "previous_state": state_controller.previous_state.value if state_controller.previous_state and hasattr(state_controller.previous_state, "value") else state_controller.previous_state,
                        "metadata": state_controller.metadata,
                        "state_history": state_controller.state_history
                    }
                    
                    with open(os.path.join(session_dir, "state.json"), "w") as f:
                        json.dump(state_data, f, indent=2)
                
                # Update metadata
                metadata_path = os.path.join(session_dir, "metadata.json")
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                else:
                    metadata = {
                        "created_at": datetime.now().isoformat()
                    }
                
                metadata["updated_at"] = datetime.now().isoformat()
                metadata["message_count"] = len(messages)
                
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2)
                
                logger.info(f"Saved session: {session_id}")
                
                return True
            except Exception as e:
                logger.error(f"Error saving session: {e}")
                return False
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load session data.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data or None if not found
        """
        # Check if session exists
        session_dir = os.path.join(self.storage_dir, session_id)
        if not os.path.exists(session_dir):
            logger.warning(f"Session not found: {session_id}")
            return None
        
        try:
            # Load metadata
            metadata_path = os.path.join(session_dir, "metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
            else:
                metadata = {}
            
            # Load messages
            messages_path = os.path.join(session_dir, "messages.json")
            if os.path.exists(messages_path):
                with open(messages_path, "r") as f:
                    messages_data = json.load(f)
            else:
                messages_data = []
            
            # Load state
            state_path = os.path.join(session_dir, "state.json")
            if os.path.exists(state_path):
                with open(state_path, "r") as f:
                    state_data = json.load(f)
            else:
                state_data = {}
            
            # Set current session ID
            with self._lock:
                self.current_session_id = session_id
            
            logger.info(f"Loaded session: {session_id}")
            
            return {
                "session_id": session_id,
                "metadata": metadata,
                "messages": messages_data,
                "state": state_data
            }
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if successful, False otherwise
        """
        # Check if session exists
        session_dir = os.path.join(self.storage_dir, session_id)
        if not os.path.exists(session_dir):
            logger.warning(f"Session not found: {session_id}")
            return False
        
        try:
            # Delete session directory
            import shutil
            shutil.rmtree(session_dir)
            
            # Clear current session ID if it matches
            with self._lock:
                if self.current_session_id == session_id:
                    self.current_session_id = None
            
            logger.info(f"Deleted session: {session_id}")
            
            return True
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all sessions.
        
        Returns:
            List of session data
        """
        sessions = []
        
        # Check if storage directory exists
        if not os.path.exists(self.storage_dir):
            logger.warning(f"Storage directory not found: {self.storage_dir}")
            return sessions
        
        # List session directories
        for session_id in os.listdir(self.storage_dir):
            session_dir = os.path.join(self.storage_dir, session_id)
            
            # Skip non-directories
            if not os.path.isdir(session_dir):
                continue
            
            # Load metadata
            metadata_path = os.path.join(session_dir, "metadata.json")
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading metadata for session {session_id}: {e}")
                    metadata = {}
            else:
                metadata = {}
            
            # Add session to list
            sessions.append({
                "session_id": session_id,
                "metadata": metadata
            })
        
        return sessions
    
    def get_current_session_id(self) -> Optional[str]:
        """
        Get the current session ID.
        
        Returns:
            Current session ID or None if no session is active
        """
        with self._lock:
            return self.current_session_id
    
    def set_current_session_id(self, session_id: str) -> None:
        """
        Set the current session ID.
        
        Args:
            session_id: Session ID
        """
        with self._lock:
            self.current_session_id = session_id
