import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
import shutil
from datetime import datetime

from ..memory_manager import MemoryManager
from ..models.event import UserMessageEvent, AssistantMessageEvent

class TestMemoryManager(unittest.TestCase):
    """Tests for the MemoryManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.session_id = "test-session"
        self.user_id = "test-user"
        
        # Create temporary directory for vector DB
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "vector_db")
        
        # Mock OpenAI handler
        self.mock_openai_handler = MagicMock()
        self.mock_openai_handler.get_completion.return_value = MagicMock(content="Summary")
        
        # Create memory manager without long-term memory
        self.memory_manager = MemoryManager(
            session_id=self.session_id,
            user_id=self.user_id,
            openai_handler=self.mock_openai_handler
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_add_user_message(self):
        """Test adding a user message."""
        event_id = self.memory_manager.add_user_message("Test message")
        
        # Check that event was added to conversation memory
        self.assertEqual(len(self.memory_manager.conversation_memory.events), 1)
        self.assertEqual(self.memory_manager.conversation_memory.events[0].content, "Test message")
        self.assertEqual(self.memory_manager.conversation_memory.events[0].role, "user")
    
    def test_add_assistant_message(self):
        """Test adding an assistant message."""
        event_id = self.memory_manager.add_assistant_message("Test response", thinking_time=2)
        
        # Check that event was added to conversation memory
        self.assertEqual(len(self.memory_manager.conversation_memory.events), 1)
        self.assertEqual(self.memory_manager.conversation_memory.events[0].content, "Test response")
        self.assertEqual(self.memory_manager.conversation_memory.events[0].role, "system")
        self.assertEqual(self.memory_manager.conversation_memory.events[0].thinking_time, 2)
    
    def test_get_conversation_messages(self):
        """Test getting conversation messages."""
        # Add user message
        self.memory_manager.add_user_message("User message")
        
        # Add assistant message
        self.memory_manager.add_assistant_message("Assistant message")
        
        # Get messages
        messages = self.memory_manager.get_conversation_messages()
        
        # Should have 2 messages
        self.assertEqual(len(messages), 2)
        
        # Check message content
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[0]["content"], "User message")
        self.assertEqual(messages[1]["role"], "assistant")
        self.assertEqual(messages[1]["content"], "Assistant message")
    
    def test_clear_conversation(self):
        """Test clearing the conversation."""
        # Add user message
        self.memory_manager.add_user_message("User message")
        
        # Clear conversation
        self.memory_manager.clear_conversation()
        
        # Should have no events
        self.assertEqual(len(self.memory_manager.conversation_memory.events), 0)
    
    @patch('chromadb.PersistentClient')
    def test_with_long_term_memory(self, mock_client):
        """Test memory manager with long-term memory."""
        # Mock ChromaDB client
        mock_client.return_value.get_or_create_collection.return_value = MagicMock()
        
        # Create memory manager with long-term memory
        memory_manager = MemoryManager(
            session_id=self.session_id,
            user_id=self.user_id,
            db_path=self.db_path,
            openai_handler=self.mock_openai_handler
        )
        
        # Add user message
        event_id = memory_manager.add_user_message("Test message")
        
        # Check that event was added to conversation memory
        self.assertEqual(len(memory_manager.conversation_memory.events), 1)
        
        # Mock search results
        mock_search_results = [
            {
                "id": "doc1",
                "text": "Test document",
                "metadata": {"domain": "lbo"},
                "distance": 0.1
            }
        ]
        memory_manager.long_term_memory.search = MagicMock(return_value=mock_search_results)
        
        # Search knowledge
        results = memory_manager.search_knowledge("test query")
        
        # Should have 1 result
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "doc1")

if __name__ == "__main__":
    unittest.main()
