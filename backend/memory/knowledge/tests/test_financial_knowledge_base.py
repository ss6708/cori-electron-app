"""
Tests for the financial knowledge base.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import tempfile
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from memory.knowledge.financial_knowledge_base import FinancialKnowledgeBase
from memory.long_term_memory import LongTermMemory

class TestFinancialKnowledgeBase(unittest.TestCase):
    """Test cases for the FinancialKnowledgeBase class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock LongTermMemory
        self.mock_ltm = MagicMock(spec=LongTermMemory)
        
        # Create a temporary directory for knowledge files
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Initialize the financial knowledge base
        self.knowledge_base = FinancialKnowledgeBase(
            long_term_memory=self.mock_ltm,
            knowledge_dir=self.temp_dir.name
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_load_default_lbo_knowledge(self):
        """Test loading default LBO knowledge."""
        # Set up mock
        self.mock_ltm.add_document.return_value = "doc123"
        
        # Call the method
        count = self.knowledge_base._load_default_lbo_knowledge()
        
        # Check that knowledge was loaded
        self.assertGreater(count, 0)
        
        # Check that add_document was called
        self.mock_ltm.add_document.assert_called()
    
    def test_load_domain_knowledge_existing_files(self):
        """Test loading domain knowledge from existing files."""
        # Create a test knowledge file
        domain_dir = os.path.join(self.temp_dir.name, "lbo")
        os.makedirs(domain_dir, exist_ok=True)
        
        test_knowledge = [
            {
                "title": "Test LBO Knowledge",
                "content": "This is test LBO knowledge.",
                "metadata": {
                    "type": "financial_knowledge",
                    "domain": "lbo",
                    "topic": "test",
                    "subtopics": ["test1", "test2"]
                }
            }
        ]
        
        with open(os.path.join(domain_dir, "test_knowledge.json"), "w") as f:
            json.dump(test_knowledge, f)
        
        # Set up mock
        self.mock_ltm.add_document.return_value = "doc123"
        
        # Call the method
        count = self.knowledge_base.load_domain_knowledge("lbo")
        
        # Check that knowledge was loaded
        self.assertEqual(count, 1)
        
        # Check that add_document was called with the right arguments
        self.mock_ltm.add_document.assert_called_with(
            text="This is test LBO knowledge.",
            metadata={
                "type": "financial_knowledge",
                "domain": "lbo",
                "topic": "test",
                "subtopics": ["test1", "test2"],
                "title": "Test LBO Knowledge"
            },
            domain="lbo"
        )
    
    def test_add_knowledge_item(self):
        """Test adding a knowledge item."""
        # Set up mock
        self.mock_ltm.add_document.return_value = "doc123"
        
        # Call the method
        doc_id = self.knowledge_base.add_knowledge_item(
            title="Test Knowledge",
            content="This is test knowledge.",
            domain="lbo",
            topic="test",
            subtopics=["test1", "test2"]
        )
        
        # Check the result
        self.assertEqual(doc_id, "doc123")
        
        # Check that add_document was called with the right arguments
        self.mock_ltm.add_document.assert_called_with(
            text="This is test knowledge.",
            metadata={
                "type": "financial_knowledge",
                "domain": "lbo",
                "topic": "test",
                "title": "Test Knowledge",
                "subtopics": ["test1", "test2"]
            },
            domain="lbo"
        )
    
    def test_search_knowledge(self):
        """Test searching for knowledge."""
        # Set up mock
        self.mock_ltm.search.return_value = [
            {
                "text": "This is test knowledge.",
                "metadata": {
                    "type": "financial_knowledge",
                    "domain": "lbo",
                    "topic": "test",
                    "title": "Test Knowledge"
                },
                "distance": 0.1
            }
        ]
        
        # Call the method
        results = self.knowledge_base.search_knowledge(
            query="test query",
            domain="lbo",
            topic="test",
            k=5
        )
        
        # Check the results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["text"], "This is test knowledge.")
        
        # Check that search was called with the right arguments
        self.mock_ltm.search.assert_called_with(
            query="test query",
            domain="lbo",
            filters={"type": "financial_knowledge", "topic": "test"},
            k=5
        )
    
    def test_save_domain_knowledge(self):
        """Test saving domain knowledge to file."""
        # Set up mock
        self.mock_ltm.get_documents_by_metadata.return_value = [
            {
                "text": "This is test knowledge.",
                "metadata": {
                    "type": "financial_knowledge",
                    "domain": "lbo",
                    "topic": "test",
                    "title": "Test Knowledge"
                }
            }
        ]
        
        # Call the method
        result = self.knowledge_base.save_domain_knowledge("lbo")
        
        # Check the result
        self.assertTrue(result)
        
        # Check that the file was created
        file_path = os.path.join(self.temp_dir.name, "lbo", "lbo_knowledge.json")
        self.assertTrue(os.path.exists(file_path))
        
        # Check the file contents
        with open(file_path, "r") as f:
            saved_knowledge = json.load(f)
        
        self.assertEqual(len(saved_knowledge), 1)
        self.assertEqual(saved_knowledge[0]["content"], "This is test knowledge.")
        self.assertEqual(saved_knowledge[0]["title"], "Test Knowledge")

if __name__ == "__main__":
    unittest.main()
