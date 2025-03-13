"""
Tests for the knowledge retriever.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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
                "title": "LBO Capital Structure",
                "content": "This is test knowledge about LBO capital structure.",
                "domain": "lbo",
                "topic": "capital_structure",
                "distance": 0.1
            }
        ]
        
        # Call the method
        result = self.knowledge_retriever.retrieve_for_query(
            query="What is the typical capital structure for an LBO?",
            domain="lbo",
            topic="capital_structure",
            k=5
        )
        
        # Check that the knowledge base was searched
        self.mock_knowledge_base.search_knowledge.assert_called_once_with(
            query="What is the typical capital structure for an LBO?",
            domain="lbo",
            topic="capital_structure",
            k=5
        )
        
        # Check that the result contains the expected information
        self.assertIn("RELEVANT FINANCIAL KNOWLEDGE", result)
        self.assertIn("LBO Capital Structure", result)
        self.assertIn("This is test knowledge about LBO capital structure.", result)
    
    def test_retrieve_for_query_no_results(self):
        """Test retrieving knowledge for a query with no results."""
        # Set up mock response
        self.mock_knowledge_base.search_knowledge.return_value = []
        
        # Call the method
        result = self.knowledge_retriever.retrieve_for_query(
            query="What is the typical capital structure for an LBO?",
            domain="lbo",
            topic="capital_structure",
            k=5
        )
        
        # Check that the knowledge base was searched
        self.mock_knowledge_base.search_knowledge.assert_called_once()
        
        # Check that the result indicates no knowledge was found
        self.assertIn("NO RELEVANT FINANCIAL KNOWLEDGE FOUND", result)
    
    def test_retrieve_by_topic(self):
        """Test retrieving knowledge by topic."""
        # Set up mock response
        self.mock_knowledge_base.get_knowledge_by_topic.return_value = [
            {
                "title": "LBO Capital Structure",
                "content": "This is test knowledge about LBO capital structure.",
                "domain": "lbo",
                "topic": "capital_structure"
            },
            {
                "title": "LBO Debt Sizing",
                "content": "This is test knowledge about LBO debt sizing.",
                "domain": "lbo",
                "topic": "capital_structure"
            }
        ]
        
        # Call the method
        result = self.knowledge_retriever.retrieve_by_topic(
            domain="lbo",
            topic="capital_structure"
        )
        
        # Check that the knowledge base was searched
        self.mock_knowledge_base.get_knowledge_by_topic.assert_called_once_with(
            domain="lbo",
            topic="capital_structure"
        )
        
        # Check that the result contains the expected information
        self.assertIn("FINANCIAL KNOWLEDGE ON CAPITAL_STRUCTURE", result)
        self.assertIn("LBO Capital Structure", result)
        self.assertIn("This is test knowledge about LBO capital structure.", result)
        self.assertIn("LBO Debt Sizing", result)
        self.assertIn("This is test knowledge about LBO debt sizing.", result)
    
    def test_retrieve_by_topic_no_results(self):
        """Test retrieving knowledge by topic with no results."""
        # Set up mock response
        self.mock_knowledge_base.get_knowledge_by_topic.return_value = []
        
        # Call the method
        result = self.knowledge_retriever.retrieve_by_topic(
            domain="lbo",
            topic="nonexistent_topic"
        )
        
        # Check that the knowledge base was searched
        self.mock_knowledge_base.get_knowledge_by_topic.assert_called_once()
        
        # Check that the result indicates no knowledge was found
        self.assertIn("NO KNOWLEDGE FOUND FOR TOPIC", result)
    
    def test_retrieve_multi_domain(self):
        """Test retrieving knowledge across multiple domains."""
        # Set up mock responses
        self.mock_knowledge_base.search_knowledge.side_effect = [
            [
                {
                    "title": "LBO Capital Structure",
                    "content": "This is test knowledge about LBO capital structure.",
                    "domain": "lbo",
                    "topic": "capital_structure",
                    "distance": 0.1
                }
            ],
            [
                {
                    "title": "M&A Valuation",
                    "content": "This is test knowledge about M&A valuation.",
                    "domain": "ma",
                    "topic": "valuation",
                    "distance": 0.2
                }
            ]
        ]
        
        # Call the method
        result = self.knowledge_retriever.retrieve_multi_domain(
            query="What are the differences between LBO and M&A financing?",
            domains=["lbo", "ma"],
            k_per_domain=3
        )
        
        # Check that the knowledge base was searched for each domain
        self.assertEqual(self.mock_knowledge_base.search_knowledge.call_count, 2)
        self.mock_knowledge_base.search_knowledge.assert_any_call(
            query="What are the differences between LBO and M&A financing?",
            domain="lbo",
            k=3
        )
        self.mock_knowledge_base.search_knowledge.assert_any_call(
            query="What are the differences between LBO and M&A financing?",
            domain="ma",
            k=3
        )
        
        # Check that the result contains the expected information
        self.assertIn("CROSS-DOMAIN FINANCIAL KNOWLEDGE", result)
        self.assertIn("[LBO DOMAIN]", result)
        self.assertIn("LBO Capital Structure", result)
        self.assertIn("This is test knowledge about LBO capital structure.", result)
        self.assertIn("[MA DOMAIN]", result)
        self.assertIn("M&A Valuation", result)
        self.assertIn("This is test knowledge about M&A valuation.", result)
    
    def test_retrieve_multi_domain_some_empty(self):
        """Test retrieving knowledge across multiple domains with some empty results."""
        # Set up mock responses
        self.mock_knowledge_base.search_knowledge.side_effect = [
            [],  # No results for LBO
            [
                {
                    "title": "M&A Valuation",
                    "content": "This is test knowledge about M&A valuation.",
                    "domain": "ma",
                    "topic": "valuation",
                    "distance": 0.2
                }
            ]
        ]
        
        # Call the method
        result = self.knowledge_retriever.retrieve_multi_domain(
            query="What are the differences between LBO and M&A financing?",
            domains=["lbo", "ma"],
            k_per_domain=3
        )
        
        # Check that the knowledge base was searched for each domain
        self.assertEqual(self.mock_knowledge_base.search_knowledge.call_count, 2)
        
        # Check that the result contains the expected information
        self.assertIn("CROSS-DOMAIN FINANCIAL KNOWLEDGE", result)
        self.assertIn("[LBO DOMAIN]", result)
        self.assertIn("No relevant knowledge found for LBO domain", result)
        self.assertIn("[MA DOMAIN]", result)
        self.assertIn("M&A Valuation", result)
    
    def test_retrieve_multi_domain_all_empty(self):
        """Test retrieving knowledge across multiple domains with all empty results."""
        # Set up mock responses
        self.mock_knowledge_base.search_knowledge.side_effect = [
            [],  # No results for LBO
            []   # No results for M&A
        ]
        
        # Call the method
        result = self.knowledge_retriever.retrieve_multi_domain(
            query="What are the differences between LBO and M&A financing?",
            domains=["lbo", "ma"],
            k_per_domain=3
        )
        
        # Check that the knowledge base was searched for each domain
        self.assertEqual(self.mock_knowledge_base.search_knowledge.call_count, 2)
        
        # Check that the result indicates no knowledge was found
        self.assertIn("NO RELEVANT FINANCIAL KNOWLEDGE FOUND ACROSS DOMAINS", result)
    
    def test_format_knowledge_item(self):
        """Test formatting a knowledge item."""
        # Create a knowledge item
        knowledge_item = {
            "title": "LBO Capital Structure",
            "content": "This is test knowledge about LBO capital structure.",
            "domain": "lbo",
            "topic": "capital_structure",
            "distance": 0.1
        }
        
        # Format the knowledge item
        result = self.knowledge_retriever._format_knowledge_item(knowledge_item)
        
        # Check that the result contains the expected information
        self.assertIn("[LBO Capital Structure]", result)
        self.assertIn("This is test knowledge about LBO capital structure.", result)
        self.assertIn("(Relevance: 90%)", result)  # 1 - 0.1 = 0.9 = 90%

if __name__ == "__main__":
    unittest.main()
