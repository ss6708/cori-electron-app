"""
Integration tests for the RAGServerIntegration class.
Tests the integration of RAG++ components with the server.
"""

import unittest
import os
import sys
from datetime import datetime
import json
import tempfile
from unittest.mock import MagicMock, patch

# Add the parent directory to sys.path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Import core classes
from backend.core.state_management import AgentStateController, AgentState
from backend.core.event_system import event_bus, Event as CoreEvent

# Import RAG++ classes
from backend.memory.adapters.server_integration import RAGServerIntegration

class TestRAGServerIntegration(unittest.TestCase):
    """Test the RAGServerIntegration class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for testing
        self.storage_dir = tempfile.mkdtemp()
        
        # Create state controller
        self.state_controller = AgentStateController()
        
        # Create server integration
        self.server_integration = RAGServerIntegration(
            state_controller=self.state_controller,
            storage_dir=self.storage_dir,
            rag_enabled=True
        )
        
        # Track events
        self.events = []
        event_bus.subscribe("rag_domain_detected", self._handle_event)
        event_bus.subscribe("rag_knowledge_retrieved", self._handle_event)
        event_bus.subscribe("rag_context_injected", self._handle_event)
        event_bus.subscribe("rag_memory_updated", self._handle_event)
        event_bus.subscribe("rag_memory_condensed", self._handle_event)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.storage_dir)
        
        # Clear events
        self.events = []
        
        # Unsubscribe from events
        event_bus.unsubscribe("rag_domain_detected", self._handle_event)
        event_bus.unsubscribe("rag_knowledge_retrieved", self._handle_event)
        event_bus.unsubscribe("rag_context_injected", self._handle_event)
        event_bus.unsubscribe("rag_memory_updated", self._handle_event)
        event_bus.unsubscribe("rag_memory_condensed", self._handle_event)
    
    def _handle_event(self, event):
        """Handle events for testing."""
        self.events.append(event)
    
    def test_initialize(self):
        """Test initializing RAG++ components."""
        # Initialize components
        success = self.server_integration.initialize()
        
        # Check that initialization was successful
        self.assertTrue(success)
        
        # Check that components were initialized
        self.assertIsNotNone(self.server_integration.conversation_memory)
        self.assertIsNotNone(self.server_integration.long_term_memory)
        self.assertIsNotNone(self.server_integration.knowledge_base)
        self.assertIsNotNone(self.server_integration.knowledge_retriever)
        self.assertIsNotNone(self.server_integration.domain_detector)
        self.assertIsNotNone(self.server_integration.user_preference_store)
        self.assertIsNotNone(self.server_integration.rag_handler)
        self.assertIsNotNone(self.server_integration.state_aware_handler)
        
        # Check that adapters were initialized
        self.assertIsNotNone(self.server_integration.event_adapter)
        self.assertIsNotNone(self.server_integration.message_adapter)
        self.assertIsNotNone(self.server_integration.session_adapter)
        
        # Check that storage directories were created
        self.assertTrue(os.path.exists(os.path.join(self.storage_dir, "conversations")))
        self.assertTrue(os.path.exists(os.path.join(self.storage_dir, "long_term")))
        self.assertTrue(os.path.exists(os.path.join(self.storage_dir, "knowledge")))
        self.assertTrue(os.path.exists(os.path.join(self.storage_dir, "preferences")))
    
    def test_get_rag_handler(self):
        """Test getting the RAG handler."""
        # Get RAG handler
        rag_handler = self.server_integration.get_rag_handler()
        
        # Check that RAG handler was returned
        self.assertIsNotNone(rag_handler)
        
        # Check that RAG handler is the same as the one in the server integration
        self.assertEqual(rag_handler, self.server_integration.rag_handler)
    
    def test_get_session_adapter(self):
        """Test getting the session adapter."""
        # Get session adapter
        session_adapter = self.server_integration.get_session_adapter()
        
        # Check that session adapter was returned
        self.assertIsNotNone(session_adapter)
        
        # Check that session adapter is the same as the one in the server integration
        self.assertEqual(session_adapter, self.server_integration.session_adapter)
    
    def test_get_state_aware_handler(self):
        """Test getting the state-aware handler."""
        # Get state-aware handler
        state_aware_handler = self.server_integration.get_state_aware_handler()
        
        # Check that state-aware handler was returned
        self.assertIsNotNone(state_aware_handler)
        
        # Check that state-aware handler is the same as the one in the server integration
        self.assertEqual(state_aware_handler, self.server_integration.state_aware_handler)
    
    def test_is_rag_enabled(self):
        """Test checking if RAG enhancement is enabled."""
        # Check if RAG is enabled
        enabled = self.server_integration.is_rag_enabled()
        
        # Check that RAG is enabled
        self.assertTrue(enabled)
    
    def test_set_rag_enabled(self):
        """Test setting whether RAG enhancement is enabled."""
        # Set RAG to disabled
        self.server_integration.set_rag_enabled(False)
        
        # Check that RAG is disabled
        self.assertFalse(self.server_integration.is_rag_enabled())
        
        # Check that RAG handler is disabled
        self.assertFalse(self.server_integration.rag_handler.rag_enabled)
        
        # Set RAG to enabled
        self.server_integration.set_rag_enabled(True)
        
        # Check that RAG is enabled
        self.assertTrue(self.server_integration.is_rag_enabled())
        
        # Check that RAG handler is enabled
        self.assertTrue(self.server_integration.rag_handler.rag_enabled)
    
    @patch('backend.memory.adapters.server_integration.RAGEnhancedOpenAIHandler.process_feedback')
    def test_process_feedback(self, mock_process_feedback):
        """Test processing feedback."""
        # Configure mock
        mock_process_feedback.return_value = True
        
        # Process feedback
        result = self.server_integration.process_feedback(
            session_id="test_session",
            feedback="This response was very helpful.",
            rating=5
        )
        
        # Check that feedback was processed successfully
        self.assertTrue(result)
        
        # Check that RAG handler was called
        mock_process_feedback.assert_called_once_with(
            session_id="test_session",
            feedback="This response was very helpful.",
            rating=5
        )
    
    @patch('backend.memory.adapters.server_integration.RAGEnhancedOpenAIHandler.condense_memory')
    def test_condense_memory(self, mock_condense_memory):
        """Test condensing memory."""
        # Configure mock
        mock_condense_memory.return_value = True
        
        # Condense memory
        result = self.server_integration.condense_memory("test_session")
        
        # Check that memory was condensed successfully
        self.assertTrue(result)
        
        # Check that RAG handler was called
        mock_condense_memory.assert_called_once_with("test_session")
    
    def test_handle_user_message(self):
        """Test handling user message events."""
        # Initialize components
        self.server_integration.initialize()
        
        # Configure mock
        self.server_integration.domain_detector.detect_domain = MagicMock(return_value="LBO")
        
        # Publish user message event
        event_bus.publish(CoreEvent(
            event_type="user_message",
            data={
                "session_id": "test_session",
                "message": "How do I build an LBO model?"
            }
        ))
        
        # Check that domain detector was called
        self.server_integration.domain_detector.detect_domain.assert_called_once_with("How do I build an LBO model?")
        
        # Check that events were published
        self.assertEqual(len(self.events), 1)
        
        # Check event types
        event_types = [event.event_type for event in self.events]
        self.assertIn("rag_domain_detected", event_types)
    
    def test_handle_session_created(self):
        """Test handling session created events."""
        # Initialize components
        self.server_integration.initialize()
        
        # Configure mock
        self.server_integration.conversation_memory.clear_events = MagicMock()
        
        # Publish session created event
        event_bus.publish(CoreEvent(
            event_type="session_created",
            data={
                "session_id": "test_session"
            }
        ))
        
        # Check that conversation memory was called
        self.server_integration.conversation_memory.clear_events.assert_called_once_with("test_session")
    
    def test_handle_session_loaded(self):
        """Test handling session loaded events."""
        # Initialize components
        self.server_integration.initialize()
        
        # Configure mock
        self.server_integration.conversation_memory.load_events = MagicMock()
        
        # Publish session loaded event
        event_bus.publish(CoreEvent(
            event_type="session_loaded",
            data={
                "session_id": "test_session"
            }
        ))
        
        # Check that conversation memory was called
        self.server_integration.conversation_memory.load_events.assert_called_once_with("test_session")

if __name__ == "__main__":
    unittest.main()
