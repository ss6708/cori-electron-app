"""
Integration tests for the StateAwareComponent and StateAwareRAGHandler classes.
Tests the integration with the core state management system.
"""

import unittest
import os
import sys
from datetime import datetime
import json
import tempfile
from unittest.mock import MagicMock, patch
from enum import Enum

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

# Import adapters
from backend.memory.adapters.state_adapter import StateAwareComponent, StateAwareRAGHandler

class MockAgentState(Enum):
    """Mock implementation of AgentState enum for testing."""
    IDLE = "idle"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    ERROR = "error"
    AWAITING_INPUT = "awaiting_input"

class MockAgentStateController:
    """Mock implementation of AgentStateController class for testing."""
    
    def __init__(self):
        """Initialize the state controller."""
        self.current_state = MockAgentState.IDLE
        self.previous_state = None
        self.state_history = []
        self.metadata = {}
    
    def get_current_state(self):
        """Get the current state."""
        return self.current_state
    
    def get_previous_state(self):
        """Get the previous state."""
        return self.previous_state
    
    def get_state_history(self):
        """Get the state history."""
        return self.state_history.copy()
    
    def transition_to(self, state, reason, metadata=None):
        """Transition to a new state."""
        # Check if the state is already the current state
        if state == self.current_state:
            return
        
        # Update state
        self.previous_state = self.current_state
        self.current_state = state
        
        # Update metadata
        if metadata:
            self.metadata.update(metadata)
        
        # Create state transition record
        transition = {
            "from_state": self.previous_state.value if self.previous_state else None,
            "to_state": state.value,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Add transition to history
        self.state_history.append(transition)
    
    def set_metadata(self, key, value):
        """Set metadata for the current state."""
        self.metadata[key] = value
    
    def get_metadata(self, key, default=None):
        """Get metadata for the current state."""
        return self.metadata.get(key, default)
    
    def clear_metadata(self):
        """Clear metadata for the current state."""
        self.metadata = {}
    
    def is_in_state(self, state):
        """Check if the agent is in a specific state."""
        return self.current_state == state
    
    def reset(self):
        """Reset the state controller."""
        self.current_state = MockAgentState.IDLE
        self.previous_state = None
        self.state_history = []
        self.metadata = {}

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
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event handler: {e}")

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

class TestStateAwareComponent(unittest.TestCase):
    """Test the StateAwareComponent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create state controller
        self.state_controller = MockAgentStateController()
        
        # Create state-aware component
        self.component = StateAwareComponent(self.state_controller)
        
        # Track state transition calls
        self.state_transition_calls = {
            "on_analyzing_state": 0,
            "on_planning_state": 0,
            "on_executing_state": 0,
            "on_reviewing_state": 0,
            "on_error_state": 0,
            "on_idle_state": 0,
            "on_awaiting_input_state": 0
        }
        
        # Override state transition methods to track calls
        self.component.on_analyzing_state = lambda metadata: self._track_call("on_analyzing_state")
        self.component.on_planning_state = lambda metadata: self._track_call("on_planning_state")
        self.component.on_executing_state = lambda metadata: self._track_call("on_executing_state")
        self.component.on_reviewing_state = lambda metadata: self._track_call("on_reviewing_state")
        self.component.on_error_state = lambda metadata: self._track_call("on_error_state")
        self.component.on_idle_state = lambda metadata: self._track_call("on_idle_state")
        self.component.on_awaiting_input_state = lambda metadata: self._track_call("on_awaiting_input_state")
        
        # Patch the imports in the component
        patcher1 = patch('backend.memory.adapters.state_adapter.AgentStateController', MockAgentStateController)
        patcher2 = patch('backend.memory.adapters.state_adapter.AgentState', MockAgentState)
        patcher3 = patch('backend.memory.adapters.state_adapter.event_bus', event_bus)
        patcher4 = patch('backend.memory.adapters.state_adapter.CoreEvent', MockCoreEvent)
        
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.addCleanup(patcher3.stop)
        self.addCleanup(patcher4.stop)
        
        patcher1.start()
        patcher2.start()
        patcher3.start()
        patcher4.start()
    
    def _track_call(self, method_name):
        """Track method calls."""
        self.state_transition_calls[method_name] += 1
    
    def test_state_transition_handling(self):
        """Test handling of state transitions."""
        # Call the handler methods directly
        self.component._handle_state_transition(MockCoreEvent(
            event_type="agent_state_changed",
            data={
                "from_state": MockAgentState.IDLE.value,
                "to_state": MockAgentState.ANALYZING.value,
                "reason": "Test transition"
            }
        ))
        
        self.component._handle_state_transition(MockCoreEvent(
            event_type="agent_state_changed",
            data={
                "from_state": MockAgentState.ANALYZING.value,
                "to_state": MockAgentState.PLANNING.value,
                "reason": "Test transition"
            }
        ))
        
        self.component._handle_state_transition(MockCoreEvent(
            event_type="agent_state_changed",
            data={
                "from_state": MockAgentState.PLANNING.value,
                "to_state": MockAgentState.EXECUTING.value,
                "reason": "Test transition"
            }
        ))
        
        self.component._handle_state_transition(MockCoreEvent(
            event_type="agent_state_changed",
            data={
                "from_state": MockAgentState.EXECUTING.value,
                "to_state": MockAgentState.REVIEWING.value,
                "reason": "Test transition"
            }
        ))
        
        self.component._handle_state_transition(MockCoreEvent(
            event_type="agent_state_changed",
            data={
                "from_state": MockAgentState.REVIEWING.value,
                "to_state": MockAgentState.ERROR.value,
                "reason": "Test transition"
            }
        ))
        
        self.component._handle_state_transition(MockCoreEvent(
            event_type="agent_state_changed",
            data={
                "from_state": MockAgentState.ERROR.value,
                "to_state": MockAgentState.IDLE.value,
                "reason": "Test transition"
            }
        ))
        
        self.component._handle_state_transition(MockCoreEvent(
            event_type="agent_state_changed",
            data={
                "from_state": MockAgentState.IDLE.value,
                "to_state": MockAgentState.AWAITING_INPUT.value,
                "reason": "Test transition"
            }
        ))
        
        # Check that state transition methods were called
        self.assertEqual(self.state_transition_calls["on_analyzing_state"], 1)
        self.assertEqual(self.state_transition_calls["on_planning_state"], 1)
        self.assertEqual(self.state_transition_calls["on_executing_state"], 1)
        self.assertEqual(self.state_transition_calls["on_reviewing_state"], 1)
        self.assertEqual(self.state_transition_calls["on_error_state"], 1)
        self.assertEqual(self.state_transition_calls["on_idle_state"], 1)
        self.assertEqual(self.state_transition_calls["on_awaiting_input_state"], 1)
    
    def test_check_valid_state(self):
        """Test checking if the current state is valid."""
        # Set current state
        self.state_controller.transition_to(
            MockAgentState.ANALYZING,
            reason="Test transition"
        )
        
        # Check valid state
        self.assertTrue(self.component.check_valid_state([MockAgentState.ANALYZING]))
        self.assertTrue(self.component.check_valid_state([MockAgentState.ANALYZING, MockAgentState.PLANNING]))
        self.assertFalse(self.component.check_valid_state([MockAgentState.PLANNING]))
        self.assertFalse(self.component.check_valid_state([MockAgentState.EXECUTING, MockAgentState.REVIEWING]))
    
    def test_transition_to(self):
        """Test transitioning to a new state."""
        # Transition to a new state
        success = self.component.transition_to(
            state=MockAgentState.PLANNING,
            reason="Test transition",
            metadata={"test_key": "test_value"}
        )
        
        # Check that transition was successful
        self.assertTrue(success)
        
        # Check that state was updated
        self.assertEqual(self.state_controller.get_current_state(), MockAgentState.PLANNING)
        
        # Check that metadata was set
        self.assertEqual(self.state_controller.get_metadata("test_key"), "test_value")
    
    def test_set_get_metadata(self):
        """Test setting and getting metadata."""
        # Set metadata
        self.component.set_metadata("test_key", "test_value")
        
        # Get metadata
        value = self.component.get_metadata("test_key")
        
        # Check that metadata was set and retrieved correctly
        self.assertEqual(value, "test_value")
        
        # Get non-existent metadata
        value = self.component.get_metadata("non_existent_key", "default_value")
        
        # Check that default value was returned
        self.assertEqual(value, "default_value")
    
    def test_handle_error(self):
        """Test handling an error."""
        # Handle error
        self.component.handle_error(
            error=ValueError("Test error"),
            context="Test context"
        )
        
        # Check that state was updated
        self.assertEqual(self.state_controller.get_current_state(), MockAgentState.ERROR)
        
        # Check that metadata was set
        self.assertEqual(self.state_controller.get_metadata("error_type"), "ValueError")
        self.assertEqual(self.state_controller.get_metadata("error_message"), "Test error")
        self.assertEqual(self.state_controller.get_metadata("context"), "Test context")

class TestStateAwareRAGHandler(unittest.TestCase):
    """Test the StateAwareRAGHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create state controller
        self.state_controller = MockAgentStateController()
        
        # Create mock components
        self.domain_detector = MagicMock()
        self.knowledge_retriever = MagicMock()
        self.conversation_memory = MagicMock()
        self.long_term_memory = MagicMock()
        
        # Configure mock behavior
        self.domain_detector.detect_domain.return_value = "LBO"
        
        self.knowledge_retriever.retrieve_for_query.return_value = """
        Leveraged Buyout (LBO) is a financial transaction where a company is acquired using a significant amount of borrowed money (bonds or loans) to meet the acquisition cost. The assets of the acquired company are often used as collateral for the loans, and the purpose is to allow companies to make large acquisitions without committing a lot of capital.
        """
        
        self.conversation_memory.get_events.return_value = [
            MagicMock(role="user", content="How do I build an LBO model?"),
            MagicMock(role="assistant", content="An LBO model is a financial model used for leveraged buyouts.")
        ]
        
        self.long_term_memory.get_relevant_memories.return_value = "Previous conversation about LBO models."
        
        # Create state-aware RAG handler
        self.rag_handler = StateAwareRAGHandler(
            state_controller=self.state_controller,
            domain_detector=self.domain_detector,
            knowledge_retriever=self.knowledge_retriever,
            conversation_memory=self.conversation_memory,
            long_term_memory=self.long_term_memory
        )
        
        # Patch the imports in the handler
        patcher1 = patch('backend.memory.adapters.state_adapter.AgentStateController', MockAgentStateController)
        patcher2 = patch('backend.memory.adapters.state_adapter.AgentState', MockAgentState)
        patcher3 = patch('backend.memory.adapters.state_adapter.event_bus', event_bus)
        patcher4 = patch('backend.memory.adapters.state_adapter.CoreEvent', MockCoreEvent)
        
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.addCleanup(patcher3.stop)
        self.addCleanup(patcher4.stop)
        
        patcher1.start()
        patcher2.start()
        patcher3.start()
        patcher4.start()
        
        # Track events
        self.events = []
        event_bus.subscribe("rag_domain_detected", self._handle_event)
        event_bus.subscribe("rag_knowledge_retrieved", self._handle_event)
        event_bus.subscribe("rag_context_injected", self._handle_event)
        event_bus.subscribe("rag_memory_updated", self._handle_event)
        event_bus.subscribe("rag_memory_condensed", self._handle_event)
    
    def tearDown(self):
        """Tear down test fixtures."""
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
    
    def test_on_analyzing_state(self):
        """Test handling of ANALYZING state."""
        # Call the handler method directly
        self.rag_handler.on_analyzing_state({
            "session_id": "test_session",
            "query": "How do I build an LBO model?"
        })
        
        # Check that domain detector was called
        self.domain_detector.detect_domain.assert_called_once_with("How do I build an LBO model?")
        
        # Check that knowledge retriever was called
        self.knowledge_retriever.retrieve_for_query.assert_called_once()
        
        # Check that metadata was set
        self.assertEqual(self.state_controller.get_metadata("detected_domain"), "LBO")
        self.assertIsNotNone(self.state_controller.get_metadata("rag_context"))
        
        # Check that events were published
        self.assertEqual(len(self.events), 2)
        
        # Check event types
        event_types = [event.event_type for event in self.events]
        self.assertIn("rag_domain_detected", event_types)
        self.assertIn("rag_knowledge_retrieved", event_types)
    
    def test_on_planning_state(self):
        """Test handling of PLANNING state."""
        # Set metadata for ANALYZING state
        self.state_controller.set_metadata("detected_domain", "LBO")
        self.state_controller.set_metadata("rag_context", "LBO context")
        
        # Call the handler method directly
        self.rag_handler.on_planning_state({
            "session_id": "test_session",
            "query": "How do I build an LBO model?"
        })
        
        # Check that long-term memory was called
        self.long_term_memory.get_relevant_memories.assert_called_once_with(
            query="How do I build an LBO model?",
            session_id="test_session"
        )
        
        # Check that metadata was set
        self.assertIsNotNone(self.state_controller.get_metadata("system_prompt"))
        self.assertIsNotNone(self.state_controller.get_metadata("long_term_context"))
        
        # Check that events were published
        self.assertEqual(len(self.events), 1)
        
        # Check event types
        event_types = [event.event_type for event in self.events]
        self.assertIn("rag_context_injected", event_types)
    
    def test_on_reviewing_state(self):
        """Test handling of REVIEWING state."""
        # Call the handler method directly
        self.rag_handler.on_reviewing_state({
            "session_id": "test_session",
            "response_length": 100
        })
        
        # Check that conversation memory was called
        self.conversation_memory.get_events.assert_called_once_with("test_session")
        
        # Check that long-term memory was called
        self.long_term_memory.add_conversation_summary.assert_called_once()
        
        # Check that events were published
        self.assertEqual(len(self.events), 1)
        
        # Check event types
        event_types = [event.event_type for event in self.events]
        self.assertIn("rag_memory_updated", event_types)
    
    def test_on_idle_state(self):
        """Test handling of IDLE state."""
        # Call the handler method directly
        self.rag_handler.on_idle_state({
            "session_id": "test_session"
        })
        
        # Check that conversation memory was called
        self.conversation_memory.get_events.assert_called_once_with("test_session")
        
        # Check that long-term memory was called
        self.long_term_memory.add_conversation_summary.assert_called_once()
        
        # Check that events were published
        self.assertEqual(len(self.events), 1)
        
        # Check event types
        event_types = [event.event_type for event in self.events]
        self.assertIn("rag_memory_condensed", event_types)
    
    def test_create_system_prompt(self):
        """Test creating a system prompt with RAG context."""
        # Create system prompt
        system_prompt = self.rag_handler._create_system_prompt(
            rag_context="LBO context",
            long_term_context="Previous conversation about LBO models.",
            domain="LBO"
        )
        
        # Check that system prompt contains RAG context
        self.assertIn("LBO context", system_prompt)
        
        # Check that system prompt contains long-term context
        self.assertIn("Previous conversation about LBO models.", system_prompt)
        
        # Check that system prompt contains domain
        self.assertIn("LBO", system_prompt)

if __name__ == "__main__":
    unittest.main()
