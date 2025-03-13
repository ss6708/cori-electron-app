"""
Tests for the conversation memory.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import tempfile
import shutil
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from memory.conversation_memory import ConversationMemory
from memory.models.event import Event
from memory.condenser.condenser import Condenser, RecentEventsCondenser

class TestConversationMemory(unittest.TestCase):
    """Test cases for the ConversationMemory class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for memory files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a mock condenser
        self.mock_condenser = MagicMock(spec=Condenser)
        self.mock_condenser.condense.return_value = []
        
        # Initialize the conversation memory
        self.conversation_memory = ConversationMemory(
            memory_dir=self.temp_dir,
            condenser=self.mock_condenser
        )
        
        # Create a test session ID
        self.session_id = "test_session"
        
        # Create a test event
        self.test_event = Event(
            id="test_event",
            role="user",
            content="This is a test event",
            timestamp="2023-01-01T00:00:00Z",
            metadata={"test": "metadata"}
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_add_event(self):
        """Test adding an event to the memory."""
        # Add the event
        self.conversation_memory.add_event(self.test_event, self.session_id)
        
        # Check that the event file was created
        event_file = os.path.join(
            self.temp_dir,
            "sessions",
            self.session_id,
            f"{self.test_event.id}.json"
        )
        self.assertTrue(os.path.exists(event_file))
        
        # Check that the event file contains the correct data
        with open(event_file, "r") as f:
            event_data = json.load(f)
        
        self.assertEqual(event_data["id"], self.test_event.id)
        self.assertEqual(event_data["role"], self.test_event.role)
        self.assertEqual(event_data["content"], self.test_event.content)
        self.assertEqual(event_data["timestamp"], self.test_event.timestamp)
        self.assertEqual(event_data["metadata"], self.test_event.metadata)
    
    def test_get_event(self):
        """Test getting an event from the memory."""
        # Add the event
        self.conversation_memory.add_event(self.test_event, self.session_id)
        
        # Get the event
        event = self.conversation_memory.get_event(self.test_event.id, self.session_id)
        
        # Check that the event is correct
        self.assertEqual(event.id, self.test_event.id)
        self.assertEqual(event.role, self.test_event.role)
        self.assertEqual(event.content, self.test_event.content)
        self.assertEqual(event.timestamp, self.test_event.timestamp)
        self.assertEqual(event.metadata, self.test_event.metadata)
    
    def test_get_event_not_found(self):
        """Test getting an event that doesn't exist."""
        # Get a non-existent event
        event = self.conversation_memory.get_event("non_existent_event", self.session_id)
        
        # Check that the event is None
        self.assertIsNone(event)
    
    def test_get_events(self):
        """Test getting all events for a session."""
        # Add multiple events
        events = []
        for i in range(3):
            event = Event(
                id=f"test_event_{i}",
                role="user",
                content=f"This is test event {i}",
                timestamp=f"2023-01-01T00:00:0{i}Z",
                metadata={"test": f"metadata_{i}"}
            )
            events.append(event)
            self.conversation_memory.add_event(event, self.session_id)
        
        # Get all events
        retrieved_events = self.conversation_memory.get_events(self.session_id)
        
        # Check that all events were retrieved
        self.assertEqual(len(retrieved_events), len(events))
        
        # Check that events are sorted by timestamp
        self.assertEqual(retrieved_events[0].id, events[0].id)
        self.assertEqual(retrieved_events[1].id, events[1].id)
        self.assertEqual(retrieved_events[2].id, events[2].id)
    
    def test_get_events_empty_session(self):
        """Test getting events for an empty session."""
        # Get events for a non-existent session
        events = self.conversation_memory.get_events("non_existent_session")
        
        # Check that the events list is empty
        self.assertEqual(len(events), 0)
    
    def test_get_condensed_events(self):
        """Test getting condensed events for a session."""
        # Add multiple events
        events = []
        for i in range(3):
            event = Event(
                id=f"test_event_{i}",
                role="user",
                content=f"This is test event {i}",
                timestamp=f"2023-01-01T00:00:0{i}Z",
                metadata={"test": f"metadata_{i}"}
            )
            events.append(event)
            self.conversation_memory.add_event(event, self.session_id)
        
        # Set up the mock condenser to return a specific list of events
        condensed_events = [
            Event(
                id="condensed_event",
                role="system",
                content="This is a condensed event",
                timestamp="2023-01-01T00:00:00Z",
                metadata={"type": "summary"}
            )
        ]
        self.mock_condenser.condense.return_value = condensed_events
        
        # Get condensed events
        retrieved_events = self.conversation_memory.get_condensed_events(self.session_id)
        
        # Check that the condenser was called with the correct events
        self.mock_condenser.condense.assert_called_once()
        self.assertEqual(len(self.mock_condenser.condense.call_args[0][0]), len(events))
        
        # Check that the condensed events were returned
        self.assertEqual(len(retrieved_events), len(condensed_events))
        self.assertEqual(retrieved_events[0].id, condensed_events[0].id)
    
    def test_save_condensed_events(self):
        """Test saving condensed events for a session."""
        # Add multiple events
        events = []
        for i in range(3):
            event = Event(
                id=f"test_event_{i}",
                role="user",
                content=f"This is test event {i}",
                timestamp=f"2023-01-01T00:00:0{i}Z",
                metadata={"test": f"metadata_{i}"}
            )
            events.append(event)
            self.conversation_memory.add_event(event, self.session_id)
        
        # Set up the mock condenser to return a specific list of events
        condensed_events = [
            Event(
                id="condensed_event",
                role="system",
                content="This is a condensed event",
                timestamp="2023-01-01T00:00:00Z",
                metadata={"type": "summary"}
            )
        ]
        self.mock_condenser.condense.return_value = condensed_events
        
        # Save condensed events
        self.conversation_memory.save_condensed_events(self.session_id)
        
        # Check that the condensed directory was created
        condensed_dir = os.path.join(
            self.temp_dir,
            "condensed",
            self.session_id
        )
        self.assertTrue(os.path.exists(condensed_dir))
        
        # Check that a condensed file was created
        condensed_files = os.listdir(condensed_dir)
        self.assertEqual(len(condensed_files), 1)
        
        # Check that the condensed file contains the correct data
        with open(os.path.join(condensed_dir, condensed_files[0]), "r") as f:
            condensed_data = json.load(f)
        
        self.assertEqual(len(condensed_data), len(condensed_events))
        self.assertEqual(condensed_data[0]["id"], condensed_events[0].id)
    
    def test_get_latest_condensed_events(self):
        """Test getting the latest condensed events for a session."""
        # Add multiple events
        events = []
        for i in range(3):
            event = Event(
                id=f"test_event_{i}",
                role="user",
                content=f"This is test event {i}",
                timestamp=f"2023-01-01T00:00:0{i}Z",
                metadata={"test": f"metadata_{i}"}
            )
            events.append(event)
            self.conversation_memory.add_event(event, self.session_id)
        
        # Set up the mock condenser to return a specific list of events
        condensed_events = [
            Event(
                id="condensed_event",
                role="system",
                content="This is a condensed event",
                timestamp="2023-01-01T00:00:00Z",
                metadata={"type": "summary"}
            )
        ]
        self.mock_condenser.condense.return_value = condensed_events
        
        # Save condensed events
        self.conversation_memory.save_condensed_events(self.session_id)
        
        # Get latest condensed events
        retrieved_events = self.conversation_memory.get_latest_condensed_events(self.session_id)
        
        # Check that the condensed events were returned
        self.assertEqual(len(retrieved_events), len(condensed_events))
        self.assertEqual(retrieved_events[0].id, condensed_events[0].id)
    
    def test_get_latest_condensed_events_no_condensed(self):
        """Test getting the latest condensed events when none exist."""
        # Add multiple events
        events = []
        for i in range(3):
            event = Event(
                id=f"test_event_{i}",
                role="user",
                content=f"This is test event {i}",
                timestamp=f"2023-01-01T00:00:0{i}Z",
                metadata={"test": f"metadata_{i}"}
            )
            events.append(event)
            self.conversation_memory.add_event(event, self.session_id)
        
        # Set up the mock condenser to return a specific list of events
        condensed_events = [
            Event(
                id="condensed_event",
                role="system",
                content="This is a condensed event",
                timestamp="2023-01-01T00:00:00Z",
                metadata={"type": "summary"}
            )
        ]
        self.mock_condenser.condense.return_value = condensed_events
        
        # Get latest condensed events without saving first
        retrieved_events = self.conversation_memory.get_latest_condensed_events(self.session_id)
        
        # Check that the condenser was called
        self.mock_condenser.condense.assert_called_once()
        
        # Check that the condensed events were returned
        self.assertEqual(len(retrieved_events), len(condensed_events))
        self.assertEqual(retrieved_events[0].id, condensed_events[0].id)
    
    def test_get_events_since(self):
        """Test getting events since a timestamp."""
        # Add multiple events
        events = []
        for i in range(3):
            event = Event(
                id=f"test_event_{i}",
                role="user",
                content=f"This is test event {i}",
                timestamp=f"2023-01-01T00:00:0{i}Z",
                metadata={"test": f"metadata_{i}"}
            )
            events.append(event)
            self.conversation_memory.add_event(event, self.session_id)
        
        # Get events since a timestamp
        retrieved_events = self.conversation_memory.get_events_since(
            self.session_id,
            "2023-01-01T00:00:01Z"
        )
        
        # Check that only events after the timestamp were returned
        self.assertEqual(len(retrieved_events), 1)
        self.assertEqual(retrieved_events[0].id, events[2].id)
    
    def test_get_events_by_role(self):
        """Test getting events by role."""
        # Add multiple events with different roles
        events = []
        roles = ["user", "assistant", "user"]
        for i in range(3):
            event = Event(
                id=f"test_event_{i}",
                role=roles[i],
                content=f"This is test event {i}",
                timestamp=f"2023-01-01T00:00:0{i}Z",
                metadata={"test": f"metadata_{i}"}
            )
            events.append(event)
            self.conversation_memory.add_event(event, self.session_id)
        
        # Get events by role
        retrieved_events = self.conversation_memory.get_events_by_role(
            self.session_id,
            "user"
        )
        
        # Check that only events with the specified role were returned
        self.assertEqual(len(retrieved_events), 2)
        self.assertEqual(retrieved_events[0].id, events[0].id)
        self.assertEqual(retrieved_events[1].id, events[2].id)
    
    def test_delete_event(self):
        """Test deleting an event."""
        # Add the event
        self.conversation_memory.add_event(self.test_event, self.session_id)
        
        # Delete the event
        self.conversation_memory.delete_event(self.test_event.id, self.session_id)
        
        # Check that the event file was deleted
        event_file = os.path.join(
            self.temp_dir,
            "sessions",
            self.session_id,
            f"{self.test_event.id}.json"
        )
        self.assertFalse(os.path.exists(event_file))
    
    def test_delete_event_not_found(self):
        """Test deleting an event that doesn't exist."""
        # Delete a non-existent event
        self.conversation_memory.delete_event("non_existent_event", self.session_id)
        
        # No exception should be raised
    
    def test_delete_session(self):
        """Test deleting a session."""
        # Add the event
        self.conversation_memory.add_event(self.test_event, self.session_id)
        
        # Delete the session
        self.conversation_memory.delete_session(self.session_id)
        
        # Check that the session directory was deleted
        session_dir = os.path.join(
            self.temp_dir,
            "sessions",
            self.session_id
        )
        self.assertFalse(os.path.exists(session_dir))
    
    def test_delete_session_not_found(self):
        """Test deleting a session that doesn't exist."""
        # Delete a non-existent session
        self.conversation_memory.delete_session("non_existent_session")
        
        # No exception should be raised
    
    def test_get_session_ids(self):
        """Test getting all session IDs."""
        # Add events to multiple sessions
        session_ids = ["session_1", "session_2", "session_3"]
        for session_id in session_ids:
            event = Event(
                id=f"test_event_{session_id}",
                role="user",
                content=f"This is test event for {session_id}",
                timestamp="2023-01-01T00:00:00Z",
                metadata={"test": "metadata"}
            )
            self.conversation_memory.add_event(event, session_id)
        
        # Get all session IDs
        retrieved_session_ids = self.conversation_memory.get_session_ids()
        
        # Check that all session IDs were retrieved
        self.assertEqual(len(retrieved_session_ids), len(session_ids))
        for session_id in session_ids:
            self.assertIn(session_id, retrieved_session_ids)
    
    def test_get_session_info(self):
        """Test getting information about a session."""
        # Add multiple events
        events = []
        for i in range(3):
            event = Event(
                id=f"test_event_{i}",
                role="user",
                content=f"This is test event {i}",
                timestamp=f"2023-01-01T00:00:0{i}Z",
                metadata={"test": f"metadata_{i}"}
            )
            events.append(event)
            self.conversation_memory.add_event(event, self.session_id)
        
        # Get session information
        session_info = self.conversation_memory.get_session_info(self.session_id)
        
        # Check that the session information is correct
        self.assertEqual(session_info["id"], self.session_id)
        self.assertEqual(session_info["event_count"], len(events))
        self.assertEqual(session_info["first_event"], events[0].timestamp)
        self.assertEqual(session_info["last_event"], events[-1].timestamp)

if __name__ == "__main__":
    unittest.main()
