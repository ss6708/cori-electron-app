"""
Integration tests for the SessionAdapter class.
Tests the integration between core SessionManager and RAG++ ConversationMemory.
"""

import unittest
import os
import sys
import shutil
from datetime import datetime
import json
import tempfile

# Add the parent directory to sys.path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Import core classes
from backend.core.session_persistence import SessionManager
from backend.core.state_management import AgentStateController, AgentState
from backend.models.message import Message as CoreMessage

# Import Memory Event classes
from backend.memory.models.event import (
    Event as MemoryEvent,
    UserMessageEvent as MemoryUserMessageEvent,
    AssistantMessageEvent as MemoryAssistantMessageEvent,
    SystemMessageEvent as MemorySystemMessageEvent,
    CondensationEvent as MemoryCondensationEvent
)

# Import RAG++ Event classes
from backend.memory.models.rag.event import (
    Event as RAGEvent,
    UserMessageEvent,
    AssistantMessageEvent,
    SystemMessageEvent
)

# Import memory components
from backend.memory.conversation_memory import ConversationMemory

# Import adapters
from backend.memory.adapters.session_adapter import SessionAdapter

class TestSessionAdapter(unittest.TestCase):
    """Test the SessionAdapter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directories for testing
        self.core_storage_dir = tempfile.mkdtemp()
        self.rag_storage_dir = tempfile.mkdtemp()
        
        # Create test components
        self.session_manager = SessionManager(storage_dir=self.core_storage_dir)
        self.conversation_memory = ConversationMemory(storage_dir=self.rag_storage_dir)
        self.state_controller = AgentStateController()
        
        # Create adapter
        self.session_adapter = SessionAdapter(
            session_manager=self.session_manager,
            conversation_memory=self.conversation_memory
        )
        
        # Create test data
        self.test_messages = [
            CoreMessage(role="user", content="How do I build an LBO model?"),
            CoreMessage(role="assistant", content="An LBO model is a financial model used for leveraged buyouts.")
        ]
        
        self.test_events = [
            RAGEvent(role="user", content="How do I build an LBO model?"),
            RAGEvent(role="assistant", content="An LBO model is a financial model used for leveraged buyouts.")
        ]
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary directories
        shutil.rmtree(self.core_storage_dir)
        shutil.rmtree(self.rag_storage_dir)
    
    def test_create_session(self):
        """Test creating a session in both systems."""
        # Create session
        session_id = self.session_adapter.create_session()
        
        # Check that session was created in core SessionManager
        self.assertEqual(self.session_manager.current_session_id, session_id)
        
        # Check that session directory was created
        core_session_dir = os.path.join(self.core_storage_dir, session_id)
        self.assertTrue(os.path.exists(core_session_dir))
        
        # Check that metadata file was created
        metadata_path = os.path.join(core_session_dir, "metadata.json")
        self.assertTrue(os.path.exists(metadata_path))
    
    def test_save_session(self):
        """Test saving a session to both systems."""
        # Create session
        session_id = self.session_adapter.create_session()
        
        # Save session
        success = self.session_adapter.save_session(
            session_id=session_id,
            messages=self.test_messages,
            state_controller=self.state_controller
        )
        
        # Check that session was saved successfully
        self.assertTrue(success)
        
        # Check that messages were saved in core SessionManager
        core_session_dir = os.path.join(self.core_storage_dir, session_id)
        messages_path = os.path.join(core_session_dir, "messages.json")
        self.assertTrue(os.path.exists(messages_path))
        
        # Check that events were saved in RAG++ ConversationMemory
        rag_session_dir = os.path.join(self.rag_storage_dir, session_id)
        events_path = os.path.join(rag_session_dir, "events.json")
        self.assertTrue(os.path.exists(events_path))
        
        # Check that events were added to conversation memory
        events = self.conversation_memory.get_events(session_id)
        self.assertEqual(len(events), len(self.test_messages))
    
    def test_load_session(self):
        """Test loading a session from both systems."""
        # Create and save session
        session_id = self.session_adapter.create_session()
        self.session_adapter.save_session(
            session_id=session_id,
            messages=self.test_messages,
            state_controller=self.state_controller
        )
        
        # Clear conversation memory to ensure it's loaded from disk
        self.conversation_memory.clear_events(session_id)
        
        # Load session
        session_data = self.session_adapter.load_session(session_id)
        
        # Check that session was loaded successfully
        self.assertIsNotNone(session_data)
        
        # Check that messages were loaded
        self.assertIn("messages", session_data)
        self.assertEqual(len(session_data["messages"]), len(self.test_messages))
        
        # Check that events were loaded
        self.assertIn("rag_events", session_data)
        self.assertEqual(len(session_data["rag_events"]), len(self.test_messages))
        
        # Check that state controller was loaded
        self.assertIn("state_controller", session_data)
        self.assertIsInstance(session_data["state_controller"], AgentStateController)
    
    def test_delete_session(self):
        """Test deleting a session from both systems."""
        # Create and save session
        session_id = self.session_adapter.create_session()
        self.session_adapter.save_session(
            session_id=session_id,
            messages=self.test_messages,
            state_controller=self.state_controller
        )
        
        # Delete session
        success = self.session_adapter.delete_session(session_id)
        
        # Check that session was deleted successfully
        self.assertTrue(success)
        
        # Check that session directory was deleted in core SessionManager
        core_session_dir = os.path.join(self.core_storage_dir, session_id)
        self.assertFalse(os.path.exists(core_session_dir))
        
        # Check that session directory was deleted in RAG++ ConversationMemory
        rag_session_dir = os.path.join(self.rag_storage_dir, session_id)
        self.assertFalse(os.path.exists(rag_session_dir))
    
    def test_sync_messages_to_events(self):
        """Test synchronizing core Messages to RAG++ Events."""
        # Create session
        session_id = self.session_adapter.create_session()
        
        # Sync messages to events
        success = self.session_adapter.sync_messages_to_events(
            session_id=session_id,
            messages=self.test_messages
        )
        
        # Check that synchronization was successful
        self.assertTrue(success)
        
        # Check that events were added to conversation memory
        events = self.conversation_memory.get_events(session_id)
        self.assertEqual(len(events), len(self.test_messages))
        
        # Check that events were saved to disk
        rag_session_dir = os.path.join(self.rag_storage_dir, session_id)
        events_path = os.path.join(rag_session_dir, "events.json")
        self.assertTrue(os.path.exists(events_path))
    
    def test_sync_events_to_messages(self):
        """Test synchronizing RAG++ Events to core Messages."""
        # Create session
        session_id = self.session_adapter.create_session()
        
        # Add events to conversation memory
        self.conversation_memory.add_events(session_id, self.test_events)
        
        # Sync events to messages
        messages = self.session_adapter.sync_events_to_messages(session_id)
        
        # Check that synchronization was successful
        self.assertEqual(len(messages), len(self.test_events))
        
        # Check message properties
        for i, message in enumerate(messages):
            self.assertEqual(message.role, self.test_events[i].role)
            self.assertEqual(message.content, self.test_events[i].content)
    
    def test_list_sessions(self):
        """Test listing sessions."""
        # Create multiple sessions
        session_ids = [
            self.session_adapter.create_session(),
            self.session_adapter.create_session(),
            self.session_adapter.create_session()
        ]
        
        # List sessions
        sessions = self.session_adapter.list_sessions()
        
        # Check that all sessions are listed
        self.assertEqual(len(sessions), len(session_ids))
        
        # Check that session IDs are correct
        listed_ids = [session["session_id"] for session in sessions]
        for session_id in session_ids:
            self.assertIn(session_id, listed_ids)
    
    def test_thread_safety(self):
        """Test thread safety of the SessionAdapter."""
        import threading
        
        # Create a list to store results
        results = []
        
        # Define a function to create and save sessions in a thread
        def create_and_save_session():
            # Create session
            session_id = self.session_adapter.create_session()
            
            # Save session
            success = self.session_adapter.save_session(
                session_id=session_id,
                messages=self.test_messages,
                state_controller=self.state_controller
            )
            
            # Add result to list
            results.append((session_id, success))
        
        # Create threads
        threads = [threading.Thread(target=create_and_save_session) for _ in range(5)]
        
        # Start threads
        for thread in threads:
            thread.start()
        
        # Wait for threads to finish
        for thread in threads:
            thread.join()
        
        # Check results
        self.assertEqual(len(results), 5)
        
        for session_id, success in results:
            # Check that session was saved successfully
            self.assertTrue(success)
            
            # Check that session directory was created in core SessionManager
            core_session_dir = os.path.join(self.core_storage_dir, session_id)
            self.assertTrue(os.path.exists(core_session_dir))
            
            # Check that session directory was created in RAG++ ConversationMemory
            rag_session_dir = os.path.join(self.rag_storage_dir, session_id)
            self.assertTrue(os.path.exists(rag_session_dir))

if __name__ == "__main__":
    unittest.main()
