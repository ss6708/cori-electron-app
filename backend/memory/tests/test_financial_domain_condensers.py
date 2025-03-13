"""
Tests for the financial domain condensers.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from memory.models.event import Event
from memory.condenser.impl.financial_domain_condensers import (
    FinancialDomainCondenser,
    LBOModelingCondenser,
    MAModelingCondenser
)

class TestFinancialDomainCondenser(unittest.TestCase):
    """Test cases for the FinancialDomainCondenser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the OpenAI client
        self.mock_openai_patcher = patch('memory.condenser.impl.financial_domain_condensers.OpenAI')
        self.mock_openai = self.mock_openai_patcher.start()
        
        # Set up mock client
        self.mock_client = MagicMock()
        self.mock_openai.return_value = self.mock_client
        
        # Initialize the condenser
        self.condenser = FinancialDomainCondenser(
            max_size=10,
            keep_first=1,
            keep_last=2,
            api_key="test_api_key",
            importance_threshold=0.5
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.mock_openai_patcher.stop()
    
    def test_initialization(self):
        """Test initialization of the condenser."""
        # Check that the parameters were set
        self.assertEqual(self.condenser.max_size, 10)
        self.assertEqual(self.condenser.keep_first, 1)
        self.assertEqual(self.condenser.keep_last, 2)
        self.assertEqual(self.condenser.importance_threshold, 0.5)
        self.assertEqual(self.condenser.domain, "financial")
    
    def test_condense_below_max_size(self):
        """Test condensing events below max size."""
        # Create events
        events = [
            Event(id="1", role="user", content="What is an LBO?", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="An LBO is a leveraged buyout.", timestamp="2023-01-01T00:00:01Z"),
            Event(id="3", role="user", content="How is it structured?", timestamp="2023-01-01T00:00:02Z")
        ]
        
        # Condense events
        condensed = self.condenser.condense(events)
        
        # Check that the events were not condensed
        self.assertEqual(condensed, events)
    
    def test_condense_above_max_size(self):
        """Test condensing events above max size."""
        # Create events
        events = []
        for i in range(15):
            events.append(Event(
                id=str(i),
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                timestamp=f"2023-01-01T00:00:{i:02d}Z"
            ))
        
        # Set up mock response for importance scores
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "0.8,0.2,0.9,0.3,0.1,0.7,0.4"
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Condense events
        condensed = self.condenser.condense(events)
        
        # Check that the events were condensed
        self.assertLess(len(condensed), len(events))
        
        # Check that the first and last events were kept
        self.assertEqual(condensed[0], events[0])
        self.assertEqual(condensed[-2], events[-2])
        self.assertEqual(condensed[-1], events[-1])
        
        # Check that the API was called
        self.mock_client.chat.completions.create.assert_called_once()
    
    def test_calculate_importance_scores(self):
        """Test calculating importance scores."""
        # Create events
        events = [
            Event(id="1", role="user", content="What is an LBO?", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="An LBO is a leveraged buyout.", timestamp="2023-01-01T00:00:01Z"),
            Event(id="3", role="user", content="How is it structured?", timestamp="2023-01-01T00:00:02Z"),
            Event(id="4", role="assistant", content="It typically involves debt and equity.", timestamp="2023-01-01T00:00:03Z"),
            Event(id="5", role="user", content="What is the typical debt-to-equity ratio?", timestamp="2023-01-01T00:00:04Z")
        ]
        
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "0.8,0.6,0.9,0.7,0.8"
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Calculate importance scores
        scores = self.condenser._calculate_importance_scores(events)
        
        # Check that the API was called with the right arguments
        self.mock_client.chat.completions.create.assert_called_once()
        call_args = self.mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], "gpt-4o")
        self.assertEqual(call_args["temperature"], 0.1)
        
        # Check that the scores were parsed correctly
        self.assertEqual(scores, [0.8, 0.6, 0.9, 0.7, 0.8])
    
    def test_filter_by_importance(self):
        """Test filtering events by importance."""
        # Create events
        events = [
            Event(id="1", role="user", content="What is an LBO?", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="An LBO is a leveraged buyout.", timestamp="2023-01-01T00:00:01Z"),
            Event(id="3", role="user", content="How is it structured?", timestamp="2023-01-01T00:00:02Z"),
            Event(id="4", role="assistant", content="It typically involves debt and equity.", timestamp="2023-01-01T00:00:03Z"),
            Event(id="5", role="user", content="What is the typical debt-to-equity ratio?", timestamp="2023-01-01T00:00:04Z")
        ]
        
        # Define importance scores
        scores = [0.8, 0.3, 0.9, 0.4, 0.7]
        
        # Filter events
        filtered = self.condenser._filter_by_importance(events, scores)
        
        # Check that the events were filtered correctly
        self.assertEqual(len(filtered), 3)
        self.assertEqual(filtered[0], events[0])  # 0.8 > 0.5
        self.assertEqual(filtered[1], events[2])  # 0.9 > 0.5
        self.assertEqual(filtered[2], events[4])  # 0.7 > 0.5
    
    def test_api_error_handling(self):
        """Test handling API errors."""
        # Create events
        events = []
        for i in range(15):
            events.append(Event(
                id=str(i),
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                timestamp=f"2023-01-01T00:00:{i:02d}Z"
            ))
        
        # Set up mock to raise an exception
        self.mock_client.chat.completions.create.side_effect = Exception("API error")
        
        # Condense events
        condensed = self.condenser.condense(events)
        
        # Check that the events were condensed using the fallback method
        self.assertLess(len(condensed), len(events))
        
        # Check that the first and last events were kept
        self.assertEqual(condensed[0], events[0])
        self.assertEqual(condensed[-2], events[-2])
        self.assertEqual(condensed[-1], events[-1])


class TestLBOModelingCondenser(unittest.TestCase):
    """Test cases for the LBOModelingCondenser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the OpenAI client
        self.mock_openai_patcher = patch('memory.condenser.impl.financial_domain_condensers.OpenAI')
        self.mock_openai = self.mock_openai_patcher.start()
        
        # Set up mock client
        self.mock_client = MagicMock()
        self.mock_openai.return_value = self.mock_client
        
        # Initialize the condenser
        self.condenser = LBOModelingCondenser(
            max_size=10,
            keep_first=1,
            keep_last=2,
            api_key="test_api_key",
            importance_threshold=0.5
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.mock_openai_patcher.stop()
    
    def test_initialization(self):
        """Test initialization of the condenser."""
        # Check that the parameters were set
        self.assertEqual(self.condenser.max_size, 10)
        self.assertEqual(self.condenser.keep_first, 1)
        self.assertEqual(self.condenser.keep_last, 2)
        self.assertEqual(self.condenser.importance_threshold, 0.5)
        self.assertEqual(self.condenser.domain, "lbo")
    
    def test_lbo_specific_prompt(self):
        """Test that the LBO-specific prompt is used."""
        # Create events
        events = []
        for i in range(15):
            events.append(Event(
                id=str(i),
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                timestamp=f"2023-01-01T00:00:{i:02d}Z"
            ))
        
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "0.8,0.2,0.9,0.3,0.1,0.7,0.4"
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Condense events
        self.condenser.condense(events)
        
        # Check that the API was called with the LBO-specific prompt
        self.mock_client.chat.completions.create.assert_called_once()
        call_args = self.mock_client.chat.completions.create.call_args[1]
        self.assertIn("LBO modeling", call_args["messages"][0]["content"])


class TestMAModelingCondenser(unittest.TestCase):
    """Test cases for the MAModelingCondenser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the OpenAI client
        self.mock_openai_patcher = patch('memory.condenser.impl.financial_domain_condensers.OpenAI')
        self.mock_openai = self.mock_openai_patcher.start()
        
        # Set up mock client
        self.mock_client = MagicMock()
        self.mock_openai.return_value = self.mock_client
        
        # Initialize the condenser
        self.condenser = MAModelingCondenser(
            max_size=10,
            keep_first=1,
            keep_last=2,
            api_key="test_api_key",
            importance_threshold=0.5
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.mock_openai_patcher.stop()
    
    def test_initialization(self):
        """Test initialization of the condenser."""
        # Check that the parameters were set
        self.assertEqual(self.condenser.max_size, 10)
        self.assertEqual(self.condenser.keep_first, 1)
        self.assertEqual(self.condenser.keep_last, 2)
        self.assertEqual(self.condenser.importance_threshold, 0.5)
        self.assertEqual(self.condenser.domain, "ma")
    
    def test_ma_specific_prompt(self):
        """Test that the M&A-specific prompt is used."""
        # Create events
        events = []
        for i in range(15):
            events.append(Event(
                id=str(i),
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                timestamp=f"2023-01-01T00:00:{i:02d}Z"
            ))
        
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "0.8,0.2,0.9,0.3,0.1,0.7,0.4"
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Condense events
        self.condenser.condense(events)
        
        # Check that the API was called with the M&A-specific prompt
        self.mock_client.chat.completions.create.assert_called_once()
        call_args = self.mock_client.chat.completions.create.call_args[1]
        self.assertIn("M&A modeling", call_args["messages"][0]["content"])

if __name__ == "__main__":
    unittest.main()
