"""
Integration tests for the EventAdapter class.
Tests the conversion between core Event and RAG++ Event models.
"""

import unittest
import os
import sys
from datetime import datetime
import json
from unittest.mock import MagicMock, patch

# Import RAG++ classes
from backend.memory.models.event import Event as RAGEvent
from backend.memory.adapters.event_adapter import EventAdapter

class MockCoreEvent:
    """Mock implementation of core Event class for testing."""
    
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

class TestEventAdapter(unittest.TestCase):
    """Test the EventAdapter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test events
        self.core_event = MockCoreEvent(
            event_type="conversation",
            data={
                "role": "user",
                "content": "How do I build an LBO model?",
                "metadata": {"session_id": "test_session"},
                "original_id": "test_id",
                "original_timestamp": datetime.now().isoformat()
            }
        )
        
        self.rag_event = RAGEvent(
            id="test_id",
            role="user",
            content="How do I build an LBO model?",
            metadata={"session_id": "test_session"}
        )
        
        # Create adapter
        self.adapter = EventAdapter()
        
        # Patch the CoreEvent import in the adapter
        patcher = patch('backend.memory.adapters.event_adapter.CoreEvent', MockCoreEvent)
        self.addCleanup(patcher.stop)
        patcher.start()
    
    def test_rag_to_core_conversion(self):
        """Test conversion from RAG++ Event to core Event."""
        # Convert RAG++ Event to core Event
        core_event = self.adapter.rag_to_core(self.rag_event)
        
        # Check event type
        self.assertEqual(core_event.event_type, "conversation")
        
        # Check data
        self.assertEqual(core_event.data["role"], self.rag_event.role)
        self.assertEqual(core_event.data["content"], self.rag_event.content)
        self.assertEqual(core_event.data["original_id"], self.rag_event.id)
        self.assertEqual(core_event.data["metadata"], self.rag_event.metadata)
    
    def test_core_to_rag_conversion(self):
        """Test conversion from core Event to RAG++ Event."""
        # Convert core Event to RAG++ Event
        rag_event = self.adapter.core_to_rag(self.core_event)
        
        # Check event properties
        self.assertEqual(rag_event.role, self.core_event.data["role"])
        self.assertEqual(rag_event.content, self.core_event.data["content"])
        self.assertEqual(rag_event.id, self.core_event.data["original_id"])
        self.assertEqual(rag_event.metadata, self.core_event.data["metadata"])
    
    def test_core_to_rag_non_conversation_event(self):
        """Test conversion from non-conversation core Event to RAG++ Event."""
        # Create non-conversation core Event
        non_conversation_event = MockCoreEvent(
            event_type="system",
            data={"message": "System event"}
        )
        
        # Convert non-conversation core Event to RAG++ Event
        rag_event = self.adapter.core_to_rag(non_conversation_event)
        
        # Check that conversion returns None
        self.assertIsNone(rag_event)
    
    def test_core_to_rag_invalid_data(self):
        """Test conversion from core Event with invalid data to RAG++ Event."""
        # Create core Event with invalid data
        invalid_data_event = MockCoreEvent(
            event_type="conversation",
            data="Invalid data"
        )
        
        # Convert core Event with invalid data to RAG++ Event
        rag_event = self.adapter.core_to_rag(invalid_data_event)
        
        # Check that conversion returns None
        self.assertIsNone(rag_event)
    
    def test_rag_to_core_batch_conversion(self):
        """Test batch conversion from RAG++ Events to core Events."""
        # Create batch of RAG++ Events
        rag_events = [
            RAGEvent(
                id=f"test_id_{i}",
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                metadata={"session_id": "test_session"}
            )
            for i in range(5)
        ]
        
        # Convert batch of RAG++ Events to core Events
        core_events = self.adapter.rag_to_core_batch(rag_events)
        
        # Check number of events
        self.assertEqual(len(core_events), len(rag_events))
        
        # Check event properties
        for i, core_event in enumerate(core_events):
            self.assertEqual(core_event.event_type, "conversation")
            self.assertEqual(core_event.data["role"], rag_events[i].role)
            self.assertEqual(core_event.data["content"], rag_events[i].content)
            self.assertEqual(core_event.data["original_id"], rag_events[i].id)
            self.assertEqual(core_event.data["metadata"], rag_events[i].metadata)
    
    def test_core_to_rag_batch_conversion(self):
        """Test batch conversion from core Events to RAG++ Events."""
        # Create batch of core Events
        core_events = [
            MockCoreEvent(
                event_type="conversation",
                data={
                    "role": "user" if i % 2 == 0 else "assistant",
                    "content": f"Message {i}",
                    "metadata": {"session_id": "test_session"},
                    "original_id": f"test_id_{i}",
                    "original_timestamp": datetime.now().isoformat()
                }
            )
            for i in range(5)
        ]
        
        # Add a non-conversation event
        core_events.append(MockCoreEvent(
            event_type="system",
            data={"message": "System event"}
        ))
        
        # Convert batch of core Events to RAG++ Events
        rag_events = self.adapter.core_to_rag_batch(core_events)
        
        # Check number of events (should be 5, not 6, since one event is not a conversation event)
        self.assertEqual(len(rag_events), 5)
        
        # Check event properties
        for i, rag_event in enumerate(rag_events):
            self.assertEqual(rag_event.role, core_events[i].data["role"])
            self.assertEqual(rag_event.content, core_events[i].data["content"])
            self.assertEqual(rag_event.id, core_events[i].data["original_id"])
            self.assertEqual(rag_event.metadata, core_events[i].data["metadata"])
    
    def test_register_rag_event_types(self):
        """Test registration of RAG++ event types."""
        # Register RAG++ event types
        event_types = self.adapter.register_rag_event_types()
        
        # Check that event types are returned
        self.assertIsInstance(event_types, list)
        self.assertGreater(len(event_types), 0)
        
        # Check that event types are strings
        for event_type in event_types:
            self.assertIsInstance(event_type, str)
            self.assertTrue(event_type.startswith("rag_"))

if __name__ == "__main__":
    unittest.main()
