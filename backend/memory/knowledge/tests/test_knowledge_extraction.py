"""
Tests for the knowledge extraction utilities.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from memory.knowledge.knowledge_extraction import KnowledgeExtractor
from memory.models.event import Event

class TestKnowledgeExtractor(unittest.TestCase):
    """Test cases for the KnowledgeExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock OpenAI client
        self.mock_openai_patcher = patch('memory.knowledge.knowledge_extraction.OpenAI')
        self.mock_openai = self.mock_openai_patcher.start()
        
        # Set up mock response
        self.mock_client = MagicMock()
        self.mock_openai.return_value = self.mock_client
        
        # Initialize the knowledge extractor
        self.knowledge_extractor = KnowledgeExtractor(api_key="test_api_key")
        self.knowledge_extractor.client = self.mock_client
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.mock_openai_patcher.stop()
    
    def test_extract_from_events(self):
        """Test extracting knowledge from events."""
        # Create test events
        events = [
            Event(id="1", role="user", content="How do I structure an LBO model?", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="To structure an LBO model, you need to consider debt sizing...", timestamp="2023-01-01T00:00:01Z"),
            Event(id="3", role="user", content="What's a typical debt-to-EBITDA ratio?", timestamp="2023-01-01T00:00:02Z")
        ]
        
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """
        Title: LBO Debt Sizing Guidelines
        
        Content: In LBO modeling, debt sizing is typically based on EBITDA multiples. Senior debt is usually 3-4x EBITDA, while total leverage can range from 5-7x EBITDA depending on the industry. More stable businesses can support higher leverage (6-7x), while cyclical businesses typically have lower leverage (4-5x).
        
        Topic: debt_sizing
        
        Subtopics: leverage, tranches, industry_specific
        """
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Call the method
        result = self.knowledge_extractor.extract_from_events(events, "lbo")
        
        # Check the result
        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "LBO Debt Sizing Guidelines")
        self.assertIn("debt sizing is typically based on EBITDA multiples", result["content"])
        self.assertEqual(result["metadata"]["topic"], "debt_sizing")
        self.assertEqual(result["metadata"]["domain"], "lbo")
        self.assertIn("leverage", result["metadata"]["subtopics"])
        
        # Check that the API was called with the right arguments
        self.mock_client.chat.completions.create.assert_called_once()
        call_args = self.mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], "gpt-4o")
        self.assertEqual(call_args["temperature"], 0.3)
    
    def test_extract_from_text(self):
        """Test extracting knowledge from text."""
        # Test text
        text = """
        When structuring an LBO, the debt package typically consists of multiple tranches:
        1. Senior secured debt: Usually 3-4x EBITDA with lower interest rates
        2. Second lien: 1-2x EBITDA with higher interest rates
        3. Mezzanine: 1-1.5x EBITDA with the highest interest rates
        
        The total leverage is typically 5-7x EBITDA depending on the industry and company stability.
        """
        
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """
        Title: LBO Debt Tranches Structure
        
        Content: In leveraged buyouts, the debt package is structured in multiple tranches with varying priorities and interest rates:
        - Senior secured debt: 3-4x EBITDA, lower interest rates (L+250-350bps)
        - Second lien: 1-2x EBITDA, higher interest rates (L+550-750bps)
        - Mezzanine: 1-1.5x EBITDA, highest interest rates (10-12%)
        
        Total leverage typically ranges from 5-7x EBITDA, varying by industry and company stability.
        
        Topic: debt_structure
        
        Subtopics: tranches, pricing, leverage
        """
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Call the method
        result = self.knowledge_extractor.extract_from_text(text, "lbo")
        
        # Check the result
        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "LBO Debt Tranches Structure")
        self.assertIn("debt package is structured in multiple tranches", result["content"])
        self.assertEqual(result["metadata"]["topic"], "debt_structure")
        self.assertEqual(result["metadata"]["domain"], "lbo")
        self.assertIn("tranches", result["metadata"]["subtopics"])
        
        # Check that the API was called with the right arguments
        self.mock_client.chat.completions.create.assert_called_once()
    
    def test_insufficient_events(self):
        """Test handling insufficient events."""
        # Create test events (less than 3)
        events = [
            Event(id="1", role="user", content="How do I structure an LBO model?", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="To structure an LBO model, you need to consider debt sizing...", timestamp="2023-01-01T00:00:01Z")
        ]
        
        # Call the method
        result = self.knowledge_extractor.extract_from_events(events, "lbo")
        
        # Check the result (should be None)
        self.assertIsNone(result)
        
        # Check that the API was not called
        self.mock_client.chat.completions.create.assert_not_called()
    
    def test_invalid_extraction_response(self):
        """Test handling invalid extraction responses."""
        # Create test events
        events = [
            Event(id="1", role="user", content="How do I structure an LBO model?", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="To structure an LBO model, you need to consider debt sizing...", timestamp="2023-01-01T00:00:01Z"),
            Event(id="3", role="user", content="What's a typical debt-to-EBITDA ratio?", timestamp="2023-01-01T00:00:02Z")
        ]
        
        # Set up mock response with missing fields
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """
        Title: LBO Debt Sizing Guidelines
        
        Content: In LBO modeling, debt sizing is typically based on EBITDA multiples.
        """
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Call the method
        result = self.knowledge_extractor.extract_from_events(events, "lbo")
        
        # Check the result (should be None due to missing topic)
        self.assertIsNone(result)
    
    def test_api_error_handling(self):
        """Test handling API errors."""
        # Create test events
        events = [
            Event(id="1", role="user", content="How do I structure an LBO model?", timestamp="2023-01-01T00:00:00Z"),
            Event(id="2", role="assistant", content="To structure an LBO model, you need to consider debt sizing...", timestamp="2023-01-01T00:00:01Z"),
            Event(id="3", role="user", content="What's a typical debt-to-EBITDA ratio?", timestamp="2023-01-01T00:00:02Z")
        ]
        
        # Set up mock to raise an exception
        self.mock_client.chat.completions.create.side_effect = Exception("API error")
        
        # Call the method
        result = self.knowledge_extractor.extract_from_events(events, "lbo")
        
        # Check the result (should be None)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
