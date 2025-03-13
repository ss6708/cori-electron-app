"""
Tests for the financial domain detector.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from memory.knowledge.financial_domain_detector import FinancialDomainDetector
from memory.models.event import Event

class TestFinancialDomainDetector(unittest.TestCase):
    """Test cases for the FinancialDomainDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock OpenAI client
        self.mock_openai_patcher = patch('memory.knowledge.financial_domain_detector.OpenAI')
        self.mock_openai = self.mock_openai_patcher.start()
        
        # Set up mock response
        self.mock_client = MagicMock()
        self.mock_openai.return_value = self.mock_client
        
        # Initialize the domain detector
        self.domain_detector = FinancialDomainDetector(api_key="test_api_key")
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.mock_openai_patcher.stop()
    
    def test_detect_domain(self):
        """Test detecting domain from a query."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "lbo,0.85"
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Call the method
        domain, confidence = self.domain_detector.detect_domain(
            "What's the typical debt structure for a leveraged buyout?"
        )
        
        # Check the result
        self.assertEqual(domain, "lbo")
        self.assertEqual(confidence, 0.85)
        
        # Check that the API was called with the right arguments
        self.mock_client.chat.completions.create.assert_called_once()
        call_args = self.mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], "gpt-4o")
        self.assertEqual(call_args["temperature"], 0.1)
    
    def test_detect_domain_from_events(self):
        """Test detecting domain from events."""
        # Create test events
        events = [
            Event(id="1", role="user", content="How do I structure an LBO model?", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="To structure an LBO model, you need to consider debt sizing...", timestamp="2023-01-01T00:00:01Z"),
            Event(id="3", role="user", content="What's a typical debt-to-EBITDA ratio?", timestamp="2023-01-01T00:00:02Z")
        ]
        
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "lbo,0.95"
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Call the method
        domain, confidence = self.domain_detector.detect_domain_from_events(events)
        
        # Check the result
        self.assertEqual(domain, "lbo")
        self.assertEqual(confidence, 0.95)
        
        # Check that the API was called with the right arguments
        self.mock_client.chat.completions.create.assert_called_once()
    
    def test_get_relevant_domains(self):
        """Test getting relevant domains for a query."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "lbo,0.85\nma,0.65\ndebt,0.45\nprivate_lending,0.25\ngeneral,0.3"
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Call the method
        domains = self.domain_detector.get_relevant_domains(
            "How do I model an acquisition with significant leverage?",
            threshold=0.6
        )
        
        # Check the result
        self.assertEqual(len(domains), 2)
        self.assertIn("lbo", domains)
        self.assertIn("ma", domains)
        
        # Check that the API was called with the right arguments
        self.mock_client.chat.completions.create.assert_called_once()
    
    def test_invalid_domain_response(self):
        """Test handling invalid domain responses."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "invalid_domain,0.85"
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Call the method
        domain, confidence = self.domain_detector.detect_domain(
            "What's the typical debt structure for a leveraged buyout?"
        )
        
        # Check the result (should default to general)
        self.assertEqual(domain, "general")
        self.assertEqual(confidence, 0.5)
    
    def test_api_error_handling(self):
        """Test handling API errors."""
        # Set up mock to raise an exception
        self.mock_client.chat.completions.create.side_effect = Exception("API error")
        
        # Call the method
        domain, confidence = self.domain_detector.detect_domain(
            "What's the typical debt structure for a leveraged buyout?"
        )
        
        # Check the result (should default to general)
        self.assertEqual(domain, "general")
        self.assertEqual(confidence, 0.5)

if __name__ == "__main__":
    unittest.main()
