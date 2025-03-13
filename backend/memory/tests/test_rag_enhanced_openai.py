"""
Tests for the RAG-enhanced OpenAI integration.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from memory.models.event import Event
from memory.rag_enhanced_openai import RAGEnhancedOpenAI
from memory.conversation_memory import ConversationMemory
from memory.long_term_memory import LongTermMemory
from memory.knowledge.financial_knowledge_base import FinancialKnowledgeBase
from memory.knowledge.financial_domain_detector import FinancialDomainDetector

class TestRAGEnhancedOpenAI(unittest.TestCase):
    """Test cases for the RAGEnhancedOpenAI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock OpenAI client
        self.mock_openai_patcher = patch('memory.rag_enhanced_openai.OpenAI')
        self.mock_openai = self.mock_openai_patcher.start()
        
        # Set up mock client
        self.mock_client = MagicMock()
        self.mock_openai.return_value = self.mock_client
        
        # Mock conversation memory
        self.mock_conversation_memory = MagicMock(spec=ConversationMemory)
        
        # Mock long-term memory
        self.mock_long_term_memory = MagicMock(spec=LongTermMemory)
        
        # Mock knowledge base
        self.mock_knowledge_base = MagicMock(spec=FinancialKnowledgeBase)
        
        # Mock domain detector
        self.mock_domain_detector = MagicMock(spec=FinancialDomainDetector)
        self.mock_domain_detector.detect_domain.return_value = ("lbo", 0.8)
        self.mock_domain_detector.get_relevant_domains.return_value = ["lbo", "ma"]
        
        # Mock knowledge retriever
        self.mock_knowledge_retriever_patcher = patch('memory.rag_enhanced_openai.KnowledgeRetriever')
        self.mock_knowledge_retriever_class = self.mock_knowledge_retriever_patcher.start()
        self.mock_knowledge_retriever = MagicMock()
        self.mock_knowledge_retriever_class.return_value = self.mock_knowledge_retriever
        self.mock_knowledge_retriever.retrieve_for_query.return_value = "Sample RAG context"
        self.mock_knowledge_retriever.retrieve_multi_domain.return_value = "Multi-domain RAG context"
        
        # Initialize RAG-enhanced OpenAI
        self.rag_openai = RAGEnhancedOpenAI(
            api_key="test_api_key",
            model="gpt-4o",
            conversation_memory=self.mock_conversation_memory,
            long_term_memory=self.mock_long_term_memory,
            knowledge_base=self.mock_knowledge_base,
            domain_detector=self.mock_domain_detector
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.mock_openai_patcher.stop()
        self.mock_knowledge_retriever_patcher.stop()
    
    def test_initialization(self):
        """Test initialization of RAG-enhanced OpenAI."""
        # Check that the client was created
        self.mock_openai.assert_called_once_with(api_key="test_api_key")
        
        # Check that the knowledge retriever was created
        self.mock_knowledge_retriever_class.assert_called_once_with(
            financial_knowledge_base=self.mock_knowledge_base
        )
        
        # Check that the model and parameters were set
        self.assertEqual(self.rag_openai.model, "gpt-4o")
        self.assertEqual(self.rag_openai.temperature, 0.7)
        self.assertEqual(self.rag_openai.max_tokens, None)
        
        # Check that RAG is enabled by default
        self.assertTrue(self.rag_openai.rag_enabled)
        
        # Check that the current domain is set to general by default
        self.assertEqual(self.rag_openai.current_domain, "general")
        self.assertEqual(self.rag_openai.domain_confidence, 0.0)
    
    def test_chat_completion(self):
        """Test chat completion."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Create messages
        messages = [
            {"role": "system", "content": "You are Cori, a financial modeling expert."},
            {"role": "user", "content": "What is EBITDA?"}
        ]
        
        # Generate completion
        response = self.rag_openai.chat_completion(
            messages=messages,
            temperature=0.5,
            max_tokens=100
        )
        
        # Check that the API was called with the right arguments
        self.mock_client.chat.completions.create.assert_called_once()
        call_args = self.mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], "gpt-4o")
        self.assertEqual(call_args["temperature"], 0.5)
        self.assertEqual(call_args["max_tokens"], 100)
        self.assertEqual(len(call_args["messages"]), 2)
        
        # Check that the response was returned
        self.assertEqual(response.choices[0].message.content, "Test response")
        
        # Check that the interaction was stored in conversation memory
        self.mock_conversation_memory.add_event.assert_called()
    
    def test_chat_completion_with_rag(self):
        """Test chat completion with RAG."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response with RAG"
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Create messages
        messages = [
            {"role": "system", "content": "You are Cori, a financial modeling expert."},
            {"role": "user", "content": "What is the typical capital structure for an LBO?"}
        ]
        
        # Generate completion
        response = self.rag_openai.chat_completion(
            messages=messages,
            rag_enabled=True
        )
        
        # Check that the API was called with the right arguments
        self.mock_client.chat.completions.create.assert_called_once()
        call_args = self.mock_client.chat.completions.create.call_args[1]
        
        # Check that the RAG context was added to the system message
        self.assertTrue(any("Sample RAG context" in msg["content"] for msg in call_args["messages"]))
        
        # Check that the response was returned
        self.assertEqual(response.choices[0].message.content, "Test response with RAG")
    
    def test_chat_completion_with_domain_detection(self):
        """Test chat completion with domain detection."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response with domain detection"
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Create messages
        messages = [
            {"role": "system", "content": "You are Cori, a financial modeling expert."},
            {"role": "user", "content": "What is the typical capital structure for an LBO?"}
        ]
        
        # Generate completion with domain detection
        response = self.rag_openai.chat_completion_with_domain_detection(
            messages=messages
        )
        
        # Check that the domain detector was called
        self.mock_domain_detector.detect_domain.assert_called_once_with(
            "What is the typical capital structure for an LBO?"
        )
        
        # Check that the current domain was updated
        self.assertEqual(self.rag_openai.current_domain, "lbo")
        self.assertEqual(self.rag_openai.domain_confidence, 0.8)
        
        # Check that the API was called with the right arguments
        self.mock_client.chat.completions.create.assert_called_once()
        
        # Check that the response was returned
        self.assertEqual(response.choices[0].message.content, "Test response with domain detection")
    
    def test_chat_completion_with_feedback(self):
        """Test chat completion with feedback."""
        # Set up mock responses
        mock_response1 = MagicMock()
        mock_response1.choices = [MagicMock()]
        mock_response1.choices[0].message.content = "Test response 1"
        
        mock_response2 = MagicMock()
        mock_response2.choices = [MagicMock()]
        mock_response2.choices[0].message.content = "Test response 2"
        
        self.mock_client.chat.completions.create.side_effect = [mock_response1, mock_response2]
        
        # Create messages
        messages = [
            {"role": "system", "content": "You are Cori, a financial modeling expert."},
            {"role": "user", "content": "Create a simple LBO model."}
        ]
        
        # Define feedback function
        def feedback_function(completion):
            if completion.choices[0].message.content == "Test response 1":
                return False, "Missing key elements"
            else:
                return True, "Good response"
        
        # Generate completion with feedback
        completion, is_acceptable, feedback = self.rag_openai.chat_completion_with_feedback(
            messages=messages,
            feedback_function=feedback_function,
            max_attempts=3
        )
        
        # Check that the API was called twice
        self.assertEqual(self.mock_client.chat.completions.create.call_count, 2)
        
        # Check that the final response was returned
        self.assertEqual(completion.choices[0].message.content, "Test response 2")
        self.assertTrue(is_acceptable)
        self.assertEqual(feedback, "Good response")
    
    def test_process_messages(self):
        """Test processing messages."""
        # Create messages
        messages = [
            {"role": "system", "content": "You are Cori, a financial modeling expert."},
            {"role": "user", "content": "What is EBITDA?"}
        ]
        
        # Process messages without RAG
        processed_messages = self.rag_openai._process_messages(
            messages=messages,
            rag_enabled=False
        )
        
        # Check that the messages were not modified
        self.assertEqual(len(processed_messages), 2)
        self.assertEqual(processed_messages[0]["content"], "You are Cori, a financial modeling expert.")
        
        # Process messages with RAG
        processed_messages = self.rag_openai._process_messages(
            messages=messages,
            rag_enabled=True
        )
        
        # Check that the RAG context was added to the system message
        self.assertEqual(len(processed_messages), 2)
        self.assertIn("Sample RAG context", processed_messages[0]["content"])
        
        # Process messages with system prompt
        processed_messages = self.rag_openai._process_messages(
            messages=messages,
            system_prompt="You are Cori, an expert in financial modeling and LBOs."
        )
        
        # Check that the system message was replaced
        self.assertEqual(len(processed_messages), 2)
        self.assertEqual(processed_messages[0]["content"], "You are Cori, an expert in financial modeling and LBOs.")
    
    def test_retrieve_rag_context(self):
        """Test retrieving RAG context."""
        # Set current domain
        self.rag_openai.current_domain = "lbo"
        self.rag_openai.domain_confidence = 0.8
        
        # Retrieve RAG context
        context = self.rag_openai._retrieve_rag_context(
            query="What is the typical capital structure for an LBO?"
        )
        
        # Check that the knowledge retriever was called
        self.mock_knowledge_retriever.retrieve_for_query.assert_called_once_with(
            query="What is the typical capital structure for an LBO?",
            domain="lbo",
            k=5
        )
        
        # Check that the context was returned
        self.assertEqual(context, "Sample RAG context")
        
        # Set low confidence
        self.rag_openai.domain_confidence = 0.6
        
        # Retrieve RAG context with low confidence
        context = self.rag_openai._retrieve_rag_context(
            query="What is the typical capital structure for an LBO?"
        )
        
        # Check that the domain detector was called
        self.mock_domain_detector.get_relevant_domains.assert_called_with(
            query="What is the typical capital structure for an LBO?",
            threshold=0.3
        )
        
        # Check that the multi-domain retriever was called
        self.mock_knowledge_retriever.retrieve_multi_domain.assert_called_with(
            query="What is the typical capital structure for an LBO?",
            domains=["ma"],  # lbo is removed from the list
            k_per_domain=2
        )
    
    def test_store_interaction(self):
        """Test storing interaction in conversation memory."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        
        # Create messages
        messages = [
            {"role": "system", "content": "You are Cori, a financial modeling expert."},
            {"role": "user", "content": "What is EBITDA?"}
        ]
        
        # Store interaction
        self.rag_openai._store_interaction(
            messages=messages,
            response=mock_response
        )
        
        # Check that the events were added to conversation memory
        self.mock_conversation_memory.add_event.assert_called()
        
        # Check that the call count matches the number of events
        self.assertEqual(self.mock_conversation_memory.add_event.call_count, 2)
    
    def test_get_conversation_history(self):
        """Test getting conversation history."""
        # Set up mock events
        mock_events = [
            Event(id="1", role="user", content="Test message", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="Test response", timestamp="2023-01-01T00:00:01Z")
        ]
        self.mock_conversation_memory.get_events.return_value = mock_events
        
        # Get conversation history
        events = self.rag_openai.get_conversation_history()
        
        # Check that the events were returned
        self.assertEqual(events, mock_events)
        
        # Check that get_events was called
        self.mock_conversation_memory.get_events.assert_called_once()
    
    def test_clear_conversation_history(self):
        """Test clearing conversation history."""
        # Set up mock session IDs
        self.mock_conversation_memory.get_session_ids.return_value = ["session1", "session2"]
        
        # Clear conversation history
        self.rag_openai.clear_conversation_history()
        
        # Check that get_session_ids was called
        self.mock_conversation_memory.get_session_ids.assert_called_once()
        
        # Check that delete_session was called for each session
        self.assertEqual(self.mock_conversation_memory.delete_session.call_count, 2)
        self.mock_conversation_memory.delete_session.assert_any_call("session1")
        self.mock_conversation_memory.delete_session.assert_any_call("session2")
    
    def test_set_rag_enabled(self):
        """Test setting RAG enabled."""
        # Set RAG enabled
        self.rag_openai.set_rag_enabled(False)
        
        # Check that RAG is disabled
        self.assertFalse(self.rag_openai.rag_enabled)
        
        # Set RAG enabled
        self.rag_openai.set_rag_enabled(True)
        
        # Check that RAG is enabled
        self.assertTrue(self.rag_openai.rag_enabled)
    
    def test_set_current_domain(self):
        """Test setting current domain."""
        # Set current domain
        self.rag_openai.set_current_domain("ma", 0.9)
        
        # Check that the domain was set
        self.assertEqual(self.rag_openai.current_domain, "ma")
        self.assertEqual(self.rag_openai.domain_confidence, 0.9)
    
    def test_detect_domain_from_history(self):
        """Test detecting domain from history."""
        # Set up mock events
        mock_events = [
            Event(id="1", role="user", content="Test message", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="Test response", timestamp="2023-01-01T00:00:01Z")
        ]
        self.mock_conversation_memory.get_events.return_value = mock_events
        
        # Set up mock domain detection
        self.mock_domain_detector.detect_domain_from_events.return_value = ("debt", 0.7)
        
        # Detect domain from history
        domain, confidence = self.rag_openai.detect_domain_from_history()
        
        # Check that the domain detector was called
        self.mock_domain_detector.detect_domain_from_events.assert_called_once_with(mock_events)
        
        # Check that the domain was returned
        self.assertEqual(domain, "debt")
        self.assertEqual(confidence, 0.7)
        
        # Check that the current domain was updated
        self.assertEqual(self.rag_openai.current_domain, "debt")
        self.assertEqual(self.rag_openai.domain_confidence, 0.7)
    
    def test_format_response(self):
        """Test formatting response."""
        # Format response
        response = "**Title**\n\nThis is a paragraph.\n\n- Bullet 1\n- Bullet 2\n\n1. Item 1\n2. Item 2"
        formatted = self.rag_openai.format_response(response)
        
        # Check that the response was formatted
        self.assertEqual(formatted, "Title\n\nThis is a paragraph.\n\n\n- Bullet 1\n\n- Bullet 2\n\n1. Item 1\n2. Item 2")

if __name__ == "__main__":
    unittest.main()
