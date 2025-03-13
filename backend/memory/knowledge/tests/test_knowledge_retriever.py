"""
Tests for the knowledge retriever.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from memory.knowledge.knowledge_retriever import KnowledgeRetriever
from memory.knowledge.financial_knowledge_base import FinancialKnowledgeBase

class TestKnowledgeRetriever(unittest.TestCase):
    """Test cases for the KnowledgeRetriever class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock FinancialKnowledgeBase
        self.mock_knowledge_base = MagicMock(spec=FinancialKnowledgeBase)
        
        # Initialize the knowledge retriever
        self.knowledge_retriever = KnowledgeRetriever(
            financial_knowledge_base=self.mock_knowledge_base
        )
    
    def test_retrieve_for_query(self):
        """Test retrieving knowledge for a query."""
        # Set up mock response
        self.mock_knowledge_base.search_knowledge.return_value = [
            {
                "text": "This is test knowledge.",
                "metadata": {
                    "title": "Test Knowledge",
                    "domain": "lbo",
                    "topic": "test"
                },
                "distance": 0.1
            }
        ]
        
        # Call the method
        result = self.knowledge_retriever.retrieve_for_query(
            query="test query",
            domain="lbo",
            topic="test",
            k=5
        )
        
        # Check the result
        self.assertIn("RELEVANT FINANCIAL KNOWLEDGE", result)
        self.assertIn("[Test Knowledge]", result)
        self.assertIn("This is test knowledge.", result)
        
        # Check that search_knowledge was called with the right arguments
        self.mock_knowledge_base.search_knowledge.assert_called_with(
            query="test query",
            domain="lbo",
            topic="test",
            k=5
        )
    
    def test_retrieve_by_topic(self):
        """Test retrieving knowledge by topic."""
        # Set up mock response
        self.mock_knowledge_base.get_knowledge_by_topic.return_value = [
            {
                "text": "This is topic-specific knowledge.",
                "metadata": {
                    "title": "Topic Knowledge",
                    "domain": "lbo",
                    "topic": "test_topic"
                }
            }
        ]
        
        # Call the method
        result = self.knowledge_retriever.retrieve_by_topic(
            domain="lbo",
            topic="test_topic"
        )
        
        # Check the result
        self.assertIn("FINANCIAL KNOWLEDGE ON TEST_TOPIC", result)
        self.assertIn("[Topic Knowledge]", result)
        self.assertIn("This is topic-specific knowledge.", result)
        
        # Check that get_knowledge_by_topic was called with the right arguments
        self.mock_knowledge_base.get_knowledge_by_topic.assert_called_with(
            domain="lbo",
            topic="test_topic"
        )
    
    def test_retrieve_multi_domain(self):
        """Test retrieving knowledge across multiple domains."""
        # Set up mock response
        self.mock_knowledge_base.search_knowledge.side_effect = [
            [
                {
                    "text": "This is LBO knowledge.",
                    "metadata": {
                        "title": "LBO Knowledge",
                        "domain": "lbo",
                        "topic": "test"
                    },
                    "distance": 0.1
                }
            ],
            [
                {
                    "text": "This is M&A knowledge.",
                    "metadata": {
                        "title": "M&A Knowledge",
                        "domain": "ma",
                        "topic": "test"
                    },
                    "distance": 0.2
                }
            ]
        ]
        
        # Call the method
        result = self.knowledge_retriever.retrieve_multi_domain(
            query="test query",
            domains=["lbo", "ma"],
            k_per_domain=2
        )
        
        # Check the result
        self.assertIn("CROSS-DOMAIN FINANCIAL KNOWLEDGE", result)
        self.assertIn("[LBO DOMAIN]", result)
        self.assertIn("- LBO Knowledge:", result)
        self.assertIn("[MA DOMAIN]", result)
        self.assertIn("- M&A Knowledge:", result)
        
        # Check that search_knowledge was called with the right arguments
        self.mock_knowledge_base.search_knowledge.assert_any_call(
            query="test query",
            domain="lbo",
            k=2
        )
        self.mock_knowledge_base.search_knowledge.assert_any_call(
            query="test query",
            domain="ma",
            k=2
        )

if __name__ == "__main__":
    unittest.main()
