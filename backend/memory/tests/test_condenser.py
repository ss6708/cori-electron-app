"""
Tests for the condenser module.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from memory.models.event import Event
from memory.condenser.condenser import Condenser, RollingCondenser, RecentEventsCondenser
from memory.condenser.impl.financial_domain_condensers import FinancialDomainCondenser, LBOModelingCondenser
from memory.condenser.impl.llm_summarizing_condenser import LLMSummarizingCondenser
from memory.condenser.impl.llm_attention_condenser import LLMAttentionCondenser

class TestRecentEventsCondenser(unittest.TestCase):
    """Test cases for the RecentEventsCondenser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.condenser = RecentEventsCondenser(max_size=5, keep_first=1, keep_last=2)
    
    def test_condense_below_max_size(self):
        """Test condensing events below max size."""
        # Create test events
        events = [
            Event(id="1", role="user", content="Event 1", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="Event 2", timestamp="2023-01-01T00:00:01Z"),
            Event(id="3", role="user", content="Event 3", timestamp="2023-01-01T00:00:02Z")
        ]
        
        # Condense events
        condensed = self.condenser.condense(events)
        
        # Check that all events are preserved
        self.assertEqual(len(condensed), 3)
        self.assertEqual(condensed[0].id, "1")
        self.assertEqual(condensed[1].id, "2")
        self.assertEqual(condensed[2].id, "3")
    
    def test_condense_above_max_size(self):
        """Test condensing events above max size."""
        # Create test events
        events = [
            Event(id="1", role="user", content="Event 1", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="Event 2", timestamp="2023-01-01T00:00:01Z"),
            Event(id="3", role="user", content="Event 3", timestamp="2023-01-01T00:00:02Z"),
            Event(id="4", role="assistant", content="Event 4", timestamp="2023-01-01T00:00:03Z"),
            Event(id="5", role="user", content="Event 5", timestamp="2023-01-01T00:00:04Z"),
            Event(id="6", role="assistant", content="Event 6", timestamp="2023-01-01T00:00:05Z"),
            Event(id="7", role="user", content="Event 7", timestamp="2023-01-01T00:00:06Z")
        ]
        
        # Condense events
        condensed = self.condenser.condense(events)
        
        # Check that the right events are preserved
        self.assertEqual(len(condensed), 5)
        self.assertEqual(condensed[0].id, "1")  # First event
        self.assertEqual(condensed[-2].id, "6")  # Second-to-last event
        self.assertEqual(condensed[-1].id, "7")  # Last event
    
    def test_metadata(self):
        """Test metadata handling."""
        # Create condenser
        condenser = RecentEventsCondenser(max_size=5, keep_first=1, keep_last=2)
        
        # Add metadata
        condenser.add_metadata("key1", "value1")
        condenser.add_metadata("key2", 42)
        
        # Get metadata
        self.assertEqual(condenser.get_metadata("key1"), "value1")
        self.assertEqual(condenser.get_metadata("key2"), 42)
        self.assertIsNone(condenser.get_metadata("key3"))
        
        # Clear metadata
        condenser.clear_metadata()
        self.assertIsNone(condenser.get_metadata("key1"))
        self.assertIsNone(condenser.get_metadata("key2"))


class TestFinancialDomainCondenser(unittest.TestCase):
    """Test cases for the FinancialDomainCondenser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.condenser = FinancialDomainCondenser(max_size=5, keep_first=1, keep_last=2, importance_threshold=0.7)
    
    def test_calculate_importance(self):
        """Test calculating importance of events."""
        # Create test events
        event1 = Event(id="1", role="user", content="What is the EBITDA multiple?", timestamp="2023-01-01T00:00:00Z")
        event2 = Event(id="2", role="assistant", content="The EBITDA multiple is 5.5x.", timestamp="2023-01-01T00:00:01Z")
        event3 = Event(id="3", role="user", content="How are you today?", timestamp="2023-01-01T00:00:02Z")
        
        # Calculate importance
        importance1 = self.condenser._calculate_importance(event1)
        importance2 = self.condenser._calculate_importance(event2)
        importance3 = self.condenser._calculate_importance(event3)
        
        # Check importance scores
        self.assertGreaterEqual(importance1, 0.7)  # Contains "EBITDA"
        self.assertGreaterEqual(importance2, 0.7)  # Contains "EBITDA" and "5.5x"
        self.assertLess(importance3, 0.7)  # No financial terms
    
    def test_is_important_event(self):
        """Test identifying important events."""
        # Create test events
        event1 = Event(id="1", role="user", content="What is the EBITDA multiple?", timestamp="2023-01-01T00:00:00Z")
        event2 = Event(id="2", role="assistant", content="The EBITDA multiple is 5.5x.", timestamp="2023-01-01T00:00:01Z")
        event3 = Event(id="3", role="user", content="How are you today?", timestamp="2023-01-01T00:00:02Z")
        
        # Check importance
        self.assertTrue(self.condenser._is_important_event(event1))
        self.assertTrue(self.condenser._is_important_event(event2))
        self.assertFalse(self.condenser._is_important_event(event3))
    
    def test_condense_middle(self):
        """Test condensing the middle section."""
        # Create test events
        events = [
            Event(id="1", role="user", content="What is the EBITDA multiple?", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="The EBITDA multiple is 5.5x.", timestamp="2023-01-01T00:00:01Z"),
            Event(id="3", role="user", content="How are you today?", timestamp="2023-01-01T00:00:02Z"),
            Event(id="4", role="assistant", content="I'm doing well, thanks for asking.", timestamp="2023-01-01T00:00:03Z"),
            Event(id="5", role="user", content="What is the leverage ratio?", timestamp="2023-01-01T00:00:04Z")
        ]
        
        # Condense middle section
        condensed = self.condenser._condense_middle(events)
        
        # Check that important events are preserved
        self.assertGreaterEqual(len(condensed), 2)
        self.assertIn(events[0], condensed)  # Contains "EBITDA"
        self.assertIn(events[1], condensed)  # Contains "EBITDA" and "5.5x"
        self.assertIn(events[4], condensed)  # Contains "leverage"
        self.assertNotIn(events[2], condensed)  # No financial terms
        self.assertNotIn(events[3], condensed)  # No financial terms


class TestLBOModelingCondenser(unittest.TestCase):
    """Test cases for the LBOModelingCondenser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.condenser = LBOModelingCondenser(max_size=5, keep_first=1, keep_last=2, importance_threshold=0.7)
    
    def test_calculate_importance(self):
        """Test calculating importance of events with LBO-specific keywords."""
        # Create test events
        event1 = Event(id="1", role="user", content="What is the typical debt-to-EBITDA ratio for an LBO?", timestamp="2023-01-01T00:00:00Z")
        event2 = Event(id="2", role="assistant", content="For an LBO, the debt-to-EBITDA ratio is typically 5-6x.", timestamp="2023-01-01T00:00:01Z")
        event3 = Event(id="3", role="user", content="What is the IRR target?", timestamp="2023-01-01T00:00:02Z")
        event4 = Event(id="4", role="assistant", content="The IRR target is usually 20-25%.", timestamp="2023-01-01T00:00:03Z")
        event5 = Event(id="5", role="user", content="How are you today?", timestamp="2023-01-01T00:00:04Z")
        
        # Calculate importance
        importance1 = self.condenser._calculate_importance(event1)
        importance2 = self.condenser._calculate_importance(event2)
        importance3 = self.condenser._calculate_importance(event3)
        importance4 = self.condenser._calculate_importance(event4)
        importance5 = self.condenser._calculate_importance(event5)
        
        # Check importance scores
        self.assertGreaterEqual(importance1, 0.9)  # Contains "LBO" and "debt-to-EBITDA"
        self.assertGreaterEqual(importance2, 0.9)  # Contains "LBO" and "debt-to-EBITDA"
        self.assertGreaterEqual(importance3, 0.9)  # Contains "IRR"
        self.assertGreaterEqual(importance4, 0.9)  # Contains "IRR"
        self.assertLess(importance5, 0.7)  # No financial terms


@patch('memory.condenser.impl.llm_summarizing_condenser.OpenAI')
class TestLLMSummarizingCondenser(unittest.TestCase):
    """Test cases for the LLMSummarizingCondenser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Set environment variable for API key
        os.environ["OPENAI_API_KEY"] = "test_api_key"
    
    def test_events_to_conversation(self, mock_openai):
        """Test converting events to conversation format."""
        # Create condenser
        condenser = LLMSummarizingCondenser(max_size=5, keep_first=1, keep_last=2)
        
        # Create test events
        events = [
            Event(id="1", role="user", content="What is the EBITDA multiple?", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="The EBITDA multiple is 5.5x.", timestamp="2023-01-01T00:00:01Z")
        ]
        
        # Convert to conversation
        conversation = condenser._events_to_conversation(events)
        
        # Check conversation format
        self.assertIn("User: What is the EBITDA multiple?", conversation)
        self.assertIn("Assistant: The EBITDA multiple is 5.5x.", conversation)
    
    def test_create_summary(self, mock_openai):
        """Test creating a summary using the LLM."""
        # Set up mock response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "summary": "Discussion about EBITDA multiples.",
            "key_parameters": {"ebitda_multiple": "5.5x"},
            "financial_metrics": {}
        })
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create condenser
        condenser = LLMSummarizingCondenser(max_size=5, keep_first=1, keep_last=2)
        condenser.client = mock_client
        
        # Create test events
        events = [
            Event(id="1", role="user", content="What is the EBITDA multiple?", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="The EBITDA multiple is 5.5x.", timestamp="2023-01-01T00:00:01Z")
        ]
        
        # Create summary
        summary_data = condenser._create_summary(events)
        
        # Check summary data
        self.assertEqual(summary_data["summary"], "Discussion about EBITDA multiples.")
        self.assertEqual(summary_data["key_parameters"]["ebitda_multiple"], "5.5x")
        
        # Check that the API was called with the right arguments
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], "gpt-4o")
        self.assertEqual(call_args["temperature"], 0.3)
    
    def test_create_summary_event(self, mock_openai):
        """Test creating a summary event."""
        # Create condenser
        condenser = LLMSummarizingCondenser(max_size=5, keep_first=1, keep_last=2)
        
        # Create test events
        events = [
            Event(id="1", role="user", content="What is the EBITDA multiple?", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="The EBITDA multiple is 5.5x.", timestamp="2023-01-01T00:00:01Z")
        ]
        
        # Create summary data
        summary_data = {
            "summary": "Discussion about EBITDA multiples.",
            "key_parameters": {"ebitda_multiple": "5.5x"},
            "financial_metrics": {}
        }
        
        # Create summary event
        summary_event = condenser._create_summary_event(events, summary_data)
        
        # Check summary event
        self.assertEqual(summary_event.role, "assistant")
        self.assertIn("[SUMMARY OF 2 EVENTS]", summary_event.content)
        self.assertIn("Discussion about EBITDA multiples.", summary_event.content)
        self.assertIn("ebitda_multiple: 5.5x", summary_event.content)
        self.assertEqual(summary_event.metadata["type"], "summary")
        self.assertEqual(summary_event.metadata["summarized_events"], 2)
        self.assertEqual(summary_event.metadata["first_event_id"], "1")
        self.assertEqual(summary_event.metadata["last_event_id"], "2")
    
    def test_condense_middle(self, mock_openai):
        """Test condensing the middle section using the LLM."""
        # Set up mock response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "summary": "Discussion about EBITDA multiples.",
            "key_parameters": {"ebitda_multiple": "5.5x"},
            "financial_metrics": {}
        })
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create condenser
        condenser = LLMSummarizingCondenser(max_size=5, keep_first=1, keep_last=2)
        condenser.client = mock_client
        
        # Create test events
        events = [
            Event(id="1", role="user", content="What is the EBITDA multiple?", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="The EBITDA multiple is 5.5x.", timestamp="2023-01-01T00:00:01Z"),
            Event(id="3", role="user", content="What about the leverage ratio?", timestamp="2023-01-01T00:00:02Z"),
            Event(id="4", role="assistant", content="The leverage ratio is typically 4-5x.", timestamp="2023-01-01T00:00:03Z")
        ]
        
        # Condense middle section
        condensed = condenser._condense_middle(events)
        
        # Check that a summary event was created
        self.assertEqual(len(condensed), 1)
        self.assertEqual(condensed[0].role, "assistant")
        self.assertIn("[SUMMARY OF 4 EVENTS]", condensed[0].content)
        self.assertIn("Discussion about EBITDA multiples.", condensed[0].content)
        
        # Check that the API was called
        mock_client.chat.completions.create.assert_called_once()


@patch('memory.condenser.impl.llm_attention_condenser.OpenAI')
class TestLLMAttentionCondenser(unittest.TestCase):
    """Test cases for the LLMAttentionCondenser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Set environment variable for API key
        os.environ["OPENAI_API_KEY"] = "test_api_key"
    
    def test_events_to_json(self, mock_openai):
        """Test converting events to JSON format."""
        # Create condenser
        condenser = LLMAttentionCondenser(max_size=5, keep_first=1, keep_last=2)
        
        # Create test events
        events = [
            Event(id="1", role="user", content="What is the EBITDA multiple?", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="The EBITDA multiple is 5.5x.", timestamp="2023-01-01T00:00:01Z")
        ]
        
        # Convert to JSON
        events_json = condenser._events_to_json(events)
        
        # Parse JSON
        events_data = json.loads(events_json)
        
        # Check JSON format
        self.assertEqual(len(events_data), 2)
        self.assertEqual(events_data[0]["event_id"], "1")
        self.assertEqual(events_data[0]["role"], "user")
        self.assertEqual(events_data[0]["content"], "What is the EBITDA multiple?")
        self.assertEqual(events_data[1]["event_id"], "2")
        self.assertEqual(events_data[1]["role"], "assistant")
        self.assertEqual(events_data[1]["content"], "The EBITDA multiple is 5.5x.")
    
    def test_score_events(self, mock_openai):
        """Test scoring events using the LLM."""
        # Set up mock response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps([
            {
                "event_id": "1",
                "importance": 0.8,
                "reason": "Contains key financial term EBITDA"
            },
            {
                "event_id": "2",
                "importance": 0.9,
                "reason": "Contains key financial term EBITDA and specific multiple value"
            }
        ])
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create condenser
        condenser = LLMAttentionCondenser(max_size=5, keep_first=1, keep_last=2)
        condenser.client = mock_client
        
        # Create test events
        events = [
            Event(id="1", role="user", content="What is the EBITDA multiple?", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="The EBITDA multiple is 5.5x.", timestamp="2023-01-01T00:00:01Z")
        ]
        
        # Score events
        scores = condenser._score_events(events)
        
        # Check scores
        self.assertEqual(len(scores), 2)
        self.assertEqual(scores[0]["event_id"], "1")
        self.assertEqual(scores[0]["importance"], 0.8)
        self.assertEqual(scores[1]["event_id"], "2")
        self.assertEqual(scores[1]["importance"], 0.9)
        
        # Check that the API was called with the right arguments
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], "gpt-4o")
        self.assertEqual(call_args["temperature"], 0.3)
    
    def test_condense_middle(self, mock_openai):
        """Test condensing the middle section using the LLM."""
        # Set up mock response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps([
            {
                "event_id": "1",
                "importance": 0.8,
                "reason": "Contains key financial term EBITDA"
            },
            {
                "event_id": "2",
                "importance": 0.9,
                "reason": "Contains key financial term EBITDA and specific multiple value"
            },
            {
                "event_id": "3",
                "importance": 0.5,
                "reason": "General question about leverage"
            },
            {
                "event_id": "4",
                "importance": 0.7,
                "reason": "Contains specific leverage ratio value"
            }
        ])
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create condenser
        condenser = LLMAttentionCondenser(max_size=5, keep_first=1, keep_last=2, importance_threshold=0.7)
        condenser.client = mock_client
        
        # Create test events
        events = [
            Event(id="1", role="user", content="What is the EBITDA multiple?", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="The EBITDA multiple is 5.5x.", timestamp="2023-01-01T00:00:01Z"),
            Event(id="3", role="user", content="What about leverage?", timestamp="2023-01-01T00:00:02Z"),
            Event(id="4", role="assistant", content="The leverage ratio is typically 4-5x.", timestamp="2023-01-01T00:00:03Z")
        ]
        
        # Condense middle section
        condensed = condenser._condense_middle(events)
        
        # Check that important events were preserved
        self.assertEqual(len(condensed), 3)
        self.assertIn(events[0], condensed)  # Importance 0.8
        self.assertIn(events[1], condensed)  # Importance 0.9
        self.assertIn(events[3], condensed)  # Importance 0.7
        self.assertNotIn(events[2], condensed)  # Importance 0.5
        
        # Check that the API was called
        mock_client.chat.completions.create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
