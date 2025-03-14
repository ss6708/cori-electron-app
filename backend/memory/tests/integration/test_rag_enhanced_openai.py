"""
Integration tests for the RAGEnhancedOpenAIHandler class.
Tests the integration with the core OpenAIHandler and RAG++ components.
"""

import unittest
import os
import sys
from datetime import datetime
import json
import tempfile
from unittest.mock import MagicMock, patch

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

from backend.memory.rag_enhanced_openai import RAGEnhancedOpenAIHandler

# Mock core classes
class MockOpenAIHandler:
    """Mock implementation of OpenAIHandler class for testing."""
    
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or "mock-api-key"
        self.model = model or "gpt-4"
    
    def get_completion(self, messages, model=None, temperature=0.7, max_tokens=None, session_id=None):
        """Get a completion from the OpenAI API."""
        return MockCoreMessage(
            role="assistant",
            content="This is a mock response from the core handler."
        )
    
    def get_streaming_completion(self, messages, model=None, temperature=0.7, max_tokens=None, session_id=None):
        """Get a streaming completion from the OpenAI API."""
        yield MockCoreMessage(
            role="assistant",
            content="This is a mock streaming response from the core handler."
        )

class MockCoreMessage:
    """Mock implementation of Message class for testing."""
    
    def __init__(
        self,
        role="user",
        content="",
        timestamp=None,
        message_id=None,
        thinking_time=None,
        displayed=True,
        metadata=None
    ):
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now().isoformat()
        self.message_id = message_id or "mock-message-id"
        self.thinking_time = thinking_time
        self.displayed = displayed
        self.metadata = metadata or {}
    
    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "message_id": self.message_id,
            "thinking_time": self.thinking_time,
            "displayed": self.displayed,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            role=data.get("role", "user"),
            content=data.get("content", ""),
            timestamp=data.get("timestamp"),
            message_id=data.get("message_id"),
            thinking_time=data.get("thinking_time"),
            displayed=data.get("displayed", True),
            metadata=data.get("metadata", {})
        )
    
    def to_openai_format(self):
        return {
            "role": self.role,
            "content": self.content
        }
    
    @classmethod
    def from_openai_format(cls, data):
        return cls(
            role=data.get("role", "user"),
            content=data.get("content", "")
        )

class MockEventBus:
    """Mock implementation of EventBus class for testing."""
    
    def __init__(self):
        self.subscribers = {}
    
    def subscribe(self, event_type, callback):
        """Subscribe to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type, callback):
        """Unsubscribe from an event type."""
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
    
    def publish(self, event):
        """Publish an event."""
        if event.event_type in self.subscribers:
            for callback in self.subscribers[event.event_type]:
                callback(event)

class MockCoreEvent:
    """Mock implementation of Event class for testing."""
    
    def __init__(self, event_type, data=None):
        self.id = "mock-event-id"
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data):
        event = cls(
            event_type=data.get("event_type", "unknown"),
            data=data.get("data")
        )
        event.id = data.get("id", "mock-event-id")
        event.timestamp = data.get("timestamp", datetime.now().isoformat())
        return event

# Create mock event bus
event_bus = MockEventBus()

# Mock RAG++ classes
class MockConversationMemory:
    """Mock implementation of ConversationMemory class for testing."""
    
    def __init__(self, storage_dir=None):
        self.storage_dir = storage_dir or tempfile.mkdtemp()
        self.events = {}
    
    def add_event(self, session_id, event):
        """Add an event to the conversation memory."""
        if session_id not in self.events:
            self.events[session_id] = []
        self.events[session_id].append(event)
        return True
    
    def add_events(self, session_id, events):
        """Add multiple events to the conversation memory."""
        if session_id not in self.events:
            self.events[session_id] = []
        self.events[session_id].extend(events)
        return True
    
    def get_events(self, session_id):
        """Get events from the conversation memory."""
        return self.events.get(session_id, [])
    
    def clear_events(self, session_id):
        """Clear events from the conversation memory."""
        if session_id in self.events:
            self.events[session_id] = []
        return True

class MockLongTermMemory:
    """Mock implementation of LongTermMemory class for testing."""
    
    def __init__(self, storage_dir=None):
        self.storage_dir = storage_dir or tempfile.mkdtemp()
        self.summaries = {}
        self.feedback = {}
    
    def add_conversation_summary(self, session_id, summary, metadata=None):
        """Add a conversation summary to the long-term memory."""
        self.summaries[session_id] = {
            "summary": summary,
            "metadata": metadata or {}
        }
        return True
    
    def get_conversation_summary(self, session_id):
        """Get a conversation summary from the long-term memory."""
        return self.summaries.get(session_id, {}).get("summary")
    
    def add_feedback(self, session_id, feedback, rating=None):
        """Add feedback to the long-term memory."""
        self.feedback[session_id] = {
            "feedback": feedback,
            "rating": rating
        }
        return True
    
    def get_feedback(self, session_id):
        """Get feedback from the long-term memory."""
        return self.feedback.get(session_id, {}).get("feedback")

class MockKnowledgeRetriever:
    """Mock implementation of KnowledgeRetriever class for testing."""
    
    def __init__(self):
        self.knowledge = {
            "LBO": """
            Leveraged Buyout (LBO) is a financial transaction where a company is acquired using a significant amount of borrowed money (bonds or loans) to meet the acquisition cost. The assets of the acquired company are often used as collateral for the loans, and the purpose is to allow companies to make large acquisitions without committing a lot of capital.
            """,
            "M&A": """
            Mergers and Acquisitions (M&A) refers to the consolidation of companies or assets through various types of financial transactions, including mergers, acquisitions, consolidations, tender offers, purchase of assets, and management acquisitions.
            """,
            "Debt Modeling": """
            Debt Modeling is the process of creating a financial model to analyze a company's debt structure, including interest payments, principal repayments, and covenant compliance.
            """,
            "Private Lending": """
            Private Lending refers to loans made by private individuals or institutions rather than traditional banks. These loans often have higher interest rates but more flexible terms.
            """
        }
    
    def retrieve_for_query(self, query, domain=None, max_results=3):
        """Retrieve knowledge for a query."""
        if domain and domain in self.knowledge:
            return self.knowledge[domain]
        
        # Simple keyword matching
        results = []
        for domain, knowledge in self.knowledge.items():
            if any(keyword in query.lower() for keyword in domain.lower().split()):
                results.append(knowledge)
        
        return "\n\n".join(results[:max_results]) if results else ""

class MockFinancialDomainDetector:
    """Mock implementation of FinancialDomainDetector class for testing."""
    
    def __init__(self):
        self.domains = ["LBO", "M&A", "Debt Modeling", "Private Lending"]
    
    def detect_domain(self, query):
        """Detect the financial domain of a query."""
        for domain in self.domains:
            if any(keyword in query.lower() for keyword in domain.lower().split()):
                return domain
        return "LBO"  # Default domain

class TestRAGEnhancedOpenAIHandler(unittest.TestCase):
    """Test the RAGEnhancedOpenAIHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directories for testing
        self.storage_dir = tempfile.mkdtemp()
        
        # Create mock components
        self.core_handler = MockOpenAIHandler()
        self.conversation_memory = MockConversationMemory()
        self.long_term_memory = MockLongTermMemory()
        self.knowledge_retriever = MockKnowledgeRetriever()
        self.domain_detector = MockFinancialDomainDetector()
        
        # Create test messages
        self.test_messages = [
            MockCoreMessage(role="user", content="How do I build an LBO model?"),
            MockCoreMessage(role="assistant", content="An LBO model is a financial model used for leveraged buyouts.")
        ]
        
        # Create RAG handler
        self.rag_handler = RAGEnhancedOpenAIHandler(
            core_handler=self.core_handler,
            conversation_memory=self.conversation_memory,
            long_term_memory=self.long_term_memory,
            knowledge_retriever=self.knowledge_retriever,
            domain_detector=self.domain_detector,
            rag_enabled=True
        )
        
        # Patch the imports in the RAG handler
        patcher1 = patch('backend.memory.rag_enhanced_openai.OpenAIHandler', MockOpenAIHandler)
        patcher2 = patch('backend.memory.rag_enhanced_openai.ConversationMemory', MockConversationMemory)
        patcher3 = patch('backend.memory.rag_enhanced_openai.LongTermMemory', MockLongTermMemory)
        patcher4 = patch('backend.memory.rag_enhanced_openai.KnowledgeRetriever', MockKnowledgeRetriever)
        patcher5 = patch('backend.memory.rag_enhanced_openai.FinancialDomainDetector', MockFinancialDomainDetector)
        patcher6 = patch('backend.memory.rag_enhanced_openai.event_bus', event_bus)
        patcher7 = patch('backend.memory.rag_enhanced_openai.Event', MockCoreEvent)
        
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.addCleanup(patcher3.stop)
        self.addCleanup(patcher4.stop)
        self.addCleanup(patcher5.stop)
        self.addCleanup(patcher6.stop)
        self.addCleanup(patcher7.stop)
        
        patcher1.start()
        patcher2.start()
        patcher3.start()
        patcher4.start()
        patcher5.start()
        patcher6.start()
        patcher7.start()
        
        # Subscribe to events for testing
        self.events = []
        event_bus.subscribe("rag_domain_detected", self._handle_event)
        event_bus.subscribe("rag_knowledge_retrieved", self._handle_event)
        event_bus.subscribe("rag_context_injected", self._handle_event)
    
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
    
    def _handle_event(self, event):
        """Handle events for testing."""
        self.events.append(event)
    
    def test_get_completion_with_rag_enabled(self):
        """Test getting a completion with RAG enhancement enabled."""
        # Get completion
        response = self.rag_handler.get_completion(
            messages=self.test_messages,
            session_id="test_session"
        )
        
        # Check that domain detector was called
        self.domain_detector.detect_domain.assert_called_once()
        
        # Check that knowledge retriever was called
        self.knowledge_retriever.retrieve_for_query.assert_called_once()
        
        # Check that core handler was called
        self.core_handler.get_completion.assert_called_once()
        
        # Check that response is from core handler
        self.assertEqual(response.role, "assistant")
        self.assertEqual(response.content, "This is a mock response from the core handler.")
        
        # Check that events were published
        self.assertEqual(len(self.events), 3)
        
        # Check event types
        event_types = [event.event_type for event in self.events]
        self.assertIn("rag_domain_detected", event_types)
        self.assertIn("rag_knowledge_retrieved", event_types)
        self.assertIn("rag_context_injected", event_types)
    
    def test_get_completion_with_rag_disabled(self):
        """Test getting a completion with RAG enhancement disabled."""
        # Disable RAG
        self.rag_handler.rag_enabled = False
        
        # Get completion
        response = self.rag_handler.get_completion(
            messages=self.test_messages,
            session_id="test_session"
        )
        
        # Check that domain detector was not called
        self.domain_detector.detect_domain.assert_not_called()
        
        # Check that knowledge retriever was not called
        self.knowledge_retriever.retrieve_for_query.assert_not_called()
        
        # Check that core handler was called
        self.core_handler.get_completion.assert_called_once()
        
        # Check that response is from core handler
        self.assertEqual(response.role, "assistant")
        self.assertEqual(response.content, "This is a mock response from the core handler.")
        
        # Check that no events were published
        self.assertEqual(len(self.events), 0)
    
    def test_get_completion_with_missing_components(self):
        """Test getting a completion with missing RAG components."""
        # Create RAG handler with missing components
        rag_handler = RAGEnhancedOpenAIHandler(
            core_handler=self.core_handler,
            conversation_memory=None,
            long_term_memory=None,
            knowledge_retriever=None,
            domain_detector=None,
            rag_enabled=True
        )
        
        # Get completion
        response = rag_handler.get_completion(
            messages=self.test_messages,
            session_id="test_session"
        )
        
        # Check that core handler was called
        self.core_handler.get_completion.assert_called_once()
        
        # Check that response is from core handler
        self.assertEqual(response.role, "assistant")
        self.assertEqual(response.content, "This is a mock response from the core handler.")
        
        # Check that no events were published
        self.assertEqual(len(self.events), 0)
    
    def test_get_completion_with_error(self):
        """Test getting a completion with an error in RAG components."""
        # Configure domain detector to raise an exception
        self.domain_detector.detect_domain.side_effect = Exception("Test error")
        
        # Get completion
        response = self.rag_handler.get_completion(
            messages=self.test_messages,
            session_id="test_session"
        )
        
        # Check that domain detector was called
        self.domain_detector.detect_domain.assert_called_once()
        
        # Check that knowledge retriever was not called
        self.knowledge_retriever.retrieve_for_query.assert_not_called()
        
        # Check that core handler was called
        self.core_handler.get_completion.assert_called_once()
        
        # Check that response is from core handler
        self.assertEqual(response.role, "assistant")
        self.assertEqual(response.content, "This is a mock response from the core handler.")
    
    def test_process_feedback(self):
        """Test processing feedback."""
        # Process feedback
        result = self.rag_handler.process_feedback(
            session_id="test_session",
            feedback="This response was very helpful.",
            rating=5
        )
        
        # Check that feedback was processed successfully
        self.assertTrue(result)
        
        # Check that long-term memory was called
        self.long_term_memory.add_feedback.assert_called_once_with(
            session_id="test_session",
            feedback="This response was very helpful.",
            rating=5
        )
    
    def test_process_feedback_with_missing_components(self):
        """Test processing feedback with missing components."""
        # Create RAG handler with missing components
        rag_handler = RAGEnhancedOpenAIHandler(
            core_handler=self.core_handler,
            conversation_memory=None,
            long_term_memory=None,
            knowledge_retriever=None,
            domain_detector=None,
            rag_enabled=True
        )
        
        # Process feedback
        result = rag_handler.process_feedback(
            session_id="test_session",
            feedback="This response was very helpful.",
            rating=5
        )
        
        # Check that feedback was not processed
        self.assertFalse(result)
    
    def test_condense_memory(self):
        """Test condensing memory."""
        # Condense memory
        result = self.rag_handler.condense_memory("test_session")
        
        # Check that memory was condensed successfully
        self.assertTrue(result)
        
        # Check that conversation memory was called
        self.conversation_memory.get_events.assert_called_once_with("test_session")
        
        # Check that long-term memory was called
        self.long_term_memory.add_conversation_summary.assert_called_once()
    
    def test_condense_memory_with_missing_components(self):
        """Test condensing memory with missing components."""
        # Create RAG handler with missing components
        rag_handler = RAGEnhancedOpenAIHandler(
            core_handler=self.core_handler,
            conversation_memory=None,
            long_term_memory=None,
            knowledge_retriever=None,
            domain_detector=None,
            rag_enabled=True
        )
        
        # Condense memory
        result = rag_handler.condense_memory("test_session")
        
        # Check that memory was not condensed
        self.assertFalse(result)
    
    def test_api_compatibility(self):
        """Test API compatibility with core OpenAIHandler."""
        # Get completion with model parameter
        response = self.rag_handler.get_completion(
            messages=self.test_messages,
            model="gpt-4"
        )
        
        # Check that core handler was called with model parameter
        self.core_handler.get_completion.assert_called_with(
            messages=self.test_messages,
            model="gpt-4"
        )
        
        # Check that response is from core handler
        self.assertEqual(response.role, "assistant")
        self.assertEqual(response.content, "This is a mock response from the core handler.")

if __name__ == "__main__":
    unittest.main()
