import unittest
from datetime import datetime
import uuid

from ..conversation_memory import ConversationMemory
from ..models.event import Event, UserMessageEvent, AssistantMessageEvent
from ..condenser.condenser import RecentEventsCondenser

class TestConversationMemory(unittest.TestCase):
    """Tests for the ConversationMemory class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.session_id = "test-session"
        self.user_id = "test-user"
        self.memory = ConversationMemory(
            session_id=self.session_id,
            user_id=self.user_id,
            condensers=[RecentEventsCondenser(max_size=5, keep_first=1)]
        )
    
    def test_add_event(self):
        """Test adding an event to the conversation memory."""
        event = UserMessageEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_id=self.user_id,
            session_id=self.session_id,
            content="Test message"
        )
        
        self.memory.add_event(event)
        
        self.assertEqual(len(self.memory.events), 1)
        self.assertEqual(self.memory.events[0], event)
    
    def test_condensed_events(self):
        """Test getting condensed events."""
        # Add initial event
        initial_event = UserMessageEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_id=self.user_id,
            session_id=self.session_id,
            content="Initial message"
        )
        self.memory.add_event(initial_event)
        
        # Add more events than the max size
        for i in range(10):
            event = AssistantMessageEvent(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                user_id=self.user_id,
                session_id=self.session_id,
                content=f"Message {i}"
            )
            self.memory.add_event(event)
        
        # Get condensed events
        condensed = self.memory.condensed_events()
        
        # Should have max_size events (5)
        self.assertEqual(len(condensed), 5)
        
        # First event should be the initial event
        self.assertEqual(condensed[0], initial_event)
        
        # Last events should be the most recent ones
        self.assertEqual(condensed[-1].content, "Message 9")
    
    def test_to_messages(self):
        """Test converting events to messages."""
        # Add user message
        user_event = UserMessageEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_id=self.user_id,
            session_id=self.session_id,
            content="User message"
        )
        self.memory.add_event(user_event)
        
        # Add assistant message
        assistant_event = AssistantMessageEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_id=self.user_id,
            session_id=self.session_id,
            content="Assistant message"
        )
        self.memory.add_event(assistant_event)
        
        # Get messages
        messages = self.memory.to_messages()
        
        # Should have 2 messages
        self.assertEqual(len(messages), 2)
        
        # Check message content
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[0]["content"], "User message")
        self.assertEqual(messages[1]["role"], "assistant")
        self.assertEqual(messages[1]["content"], "Assistant message")
    
    def test_clear(self):
        """Test clearing the conversation memory."""
        # Add an event
        event = UserMessageEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_id=self.user_id,
            session_id=self.session_id,
            content="Test message"
        )
        self.memory.add_event(event)
        
        # Clear memory
        self.memory.clear()
        
        # Should have no events
        self.assertEqual(len(self.memory.events), 0)
    
    def test_get_events_by_domain(self):
        """Test getting events by domain."""
        # Add events with different domains
        lbo_event = UserMessageEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_id=self.user_id,
            session_id=self.session_id,
            content="LBO message",
            domain="lbo"
        )
        self.memory.add_event(lbo_event)
        
        ma_event = UserMessageEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_id=self.user_id,
            session_id=self.session_id,
            content="M&A message",
            domain="ma"
        )
        self.memory.add_event(ma_event)
        
        # Get events by domain
        lbo_events = self.memory.get_events_by_domain("lbo")
        
        # Should have 1 LBO event
        self.assertEqual(len(lbo_events), 1)
        self.assertEqual(lbo_events[0], lbo_event)
    
    def test_get_recent_events(self):
        """Test getting recent events."""
        # Add events
        for i in range(5):
            event = UserMessageEvent(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                user_id=self.user_id,
                session_id=self.session_id,
                content=f"Message {i}"
            )
            self.memory.add_event(event)
        
        # Get recent events (3)
        recent = self.memory.get_recent_events(3)
        
        # Should have 3 events
        self.assertEqual(len(recent), 3)
        
        # Should be the most recent ones
        self.assertEqual(recent[0].content, "Message 2")
        self.assertEqual(recent[1].content, "Message 3")
        self.assertEqual(recent[2].content, "Message 4")

if __name__ == "__main__":
    unittest.main()
