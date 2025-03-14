"""
Integration tests for the MessageAdapter class.
Tests the conversion between core Message and RAG++ Event models.
"""

import unittest
import os
import sys
from datetime import datetime
import json
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

from backend.memory.adapters.message_adapter import MessageAdapter

class MockCoreMessage:
    """Mock implementation of core Message class for testing."""
    
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

class TestMessageAdapter(unittest.TestCase):
    """Test the MessageAdapter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test messages and events
        self.core_message = MockCoreMessage(
            role="user",
            content="How do I build an LBO model?",
            timestamp=datetime.now().isoformat(),
            displayed=True,
            thinking_time=1500
        )
        
        self.rag_event = RAGEvent(
            role="user",
            content="How do I build an LBO model?",
            metadata={
                "thinking_time": 1500,
                "displayed": True
            }
        )
        
        # Create adapter
        self.message_adapter = MessageAdapter()
        
        # Patch the CoreMessage import in the adapter
        patcher = patch('backend.memory.adapters.message_adapter.CoreMessage', MockCoreMessage)
        self.addCleanup(patcher.stop)
        patcher.start()
    
    def test_core_to_rag_conversion(self):
        """Test conversion from core Message to RAG++ Event."""
        # Convert core Message to RAG++ Event
        rag_event = self.message_adapter.core_to_rag(self.core_message)
        
        # Check event properties
        self.assertEqual(rag_event.role, self.core_message.role)
        self.assertEqual(rag_event.content, self.core_message.content)
        self.assertEqual(rag_event.metadata.get("thinking_time"), self.core_message.thinking_time)
        self.assertEqual(rag_event.metadata.get("displayed"), self.core_message.displayed)
    
    def test_rag_to_core_conversion(self):
        """Test conversion from RAG++ Event to core Message."""
        # Convert RAG++ Event to core Message
        core_message = self.message_adapter.rag_to_core(self.rag_event)
        
        # Check message properties
        self.assertEqual(core_message.role, self.rag_event.role)
        self.assertEqual(core_message.content, self.rag_event.content)
        self.assertEqual(core_message.thinking_time, self.rag_event.metadata.get("thinking_time"))
        self.assertEqual(core_message.displayed, self.rag_event.metadata.get("displayed"))
    
    def test_core_to_rag_batch_conversion(self):
        """Test batch conversion from core Messages to RAG++ Events."""
        # Create batch of core Messages
        core_messages = [
            MockCoreMessage(
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                thinking_time=i * 100 if i % 2 != 0 else None
            )
            for i in range(5)
        ]
        
        # Convert batch of core Messages to RAG++ Events
        rag_events = self.message_adapter.core_to_rag_batch(core_messages)
        
        # Check number of events
        self.assertEqual(len(rag_events), len(core_messages))
        
        # Check event properties
        for i, rag_event in enumerate(rag_events):
            self.assertEqual(rag_event.role, core_messages[i].role)
            self.assertEqual(rag_event.content, core_messages[i].content)
            
            if core_messages[i].thinking_time is not None:
                self.assertEqual(rag_event.metadata.get("thinking_time"), core_messages[i].thinking_time)
            else:
                self.assertNotIn("thinking_time", rag_event.metadata)
    
    def test_rag_to_core_batch_conversion(self):
        """Test batch conversion from RAG++ Events to core Messages."""
        # Create batch of RAG++ Events
        rag_events = [
            RAGEvent(
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                metadata={
                    "thinking_time": i * 100 if i % 2 != 0 else None,
                    "displayed": i % 2 == 0
                }
            )
            for i in range(5)
        ]
        
        # Convert batch of RAG++ Events to core Messages
        core_messages = self.message_adapter.rag_to_core_batch(rag_events)
        
        # Check number of messages
        self.assertEqual(len(core_messages), len(rag_events))
        
        # Check message properties
        for i, core_message in enumerate(core_messages):
            self.assertEqual(core_message.role, rag_events[i].role)
            self.assertEqual(core_message.content, rag_events[i].content)
            self.assertEqual(core_message.thinking_time, rag_events[i].metadata.get("thinking_time"))
            self.assertEqual(core_message.displayed, rag_events[i].metadata.get("displayed", True))
    
    def test_openai_format_to_rag_conversion(self):
        """Test conversion from OpenAI format message to RAG++ Event."""
        # Create OpenAI format message
        openai_message = {
            "role": "user",
            "content": "How do I build an LBO model?"
        }
        
        # Convert OpenAI format message to RAG++ Event
        rag_event = self.message_adapter.openai_format_to_rag(openai_message)
        
        # Check event properties
        self.assertEqual(rag_event.role, openai_message["role"])
        self.assertEqual(rag_event.content, openai_message["content"])
    
    def test_rag_to_openai_format_conversion(self):
        """Test conversion from RAG++ Event to OpenAI format message."""
        # Convert RAG++ Event to OpenAI format message
        openai_message = self.message_adapter.rag_to_openai_format(self.rag_event)
        
        # Check message properties
        self.assertEqual(openai_message["role"], self.rag_event.role)
        self.assertEqual(openai_message["content"], self.rag_event.content)
    
    def test_openai_format_to_core_conversion(self):
        """Test conversion from OpenAI format message to core Message."""
        # Create OpenAI format message
        openai_message = {
            "role": "user",
            "content": "How do I build an LBO model?"
        }
        
        # Convert OpenAI format message to core Message
        core_message = self.message_adapter.openai_format_to_core(openai_message)
        
        # Check message properties
        self.assertEqual(core_message.role, openai_message["role"])
        self.assertEqual(core_message.content, openai_message["content"])
    
    def test_thread_safety(self):
        """Test thread safety of the MessageAdapter."""
        import threading
        
        # Create a list to store results
        results = []
        
        # Define a function to convert messages in a thread
        def convert_messages():
            # Convert core Message to RAG++ Event
            rag_event = self.message_adapter.core_to_rag(self.core_message)
            
            # Convert RAG++ Event to core Message
            core_message = self.message_adapter.rag_to_core(rag_event)
            
            # Add result to list
            results.append((rag_event, core_message))
        
        # Create threads
        threads = [threading.Thread(target=convert_messages) for _ in range(10)]
        
        # Start threads
        for thread in threads:
            thread.start()
        
        # Wait for threads to finish
        for thread in threads:
            thread.join()
        
        # Check results
        self.assertEqual(len(results), 10)
        
        for rag_event, core_message in results:
            # Check event properties
            self.assertEqual(rag_event.role, self.core_message.role)
            self.assertEqual(rag_event.content, self.core_message.content)
            
            # Check message properties
            self.assertEqual(core_message.role, self.core_message.role)
            self.assertEqual(core_message.content, self.core_message.content)

if __name__ == "__main__":
    unittest.main()
