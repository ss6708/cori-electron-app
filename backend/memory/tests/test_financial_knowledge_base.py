"""
Tests for the financial knowledge base.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import tempfile
import shutil
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from memory.knowledge.financial_knowledge_base import FinancialKnowledgeBase
from memory.long_term_memory import LongTermMemory

class TestFinancialKnowledgeBase(unittest.TestCase):
    """Test cases for the FinancialKnowledgeBase class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for the knowledge base
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock the long-term memory
        self.mock_ltm = MagicMock(spec=LongTermMemory)
        
        # Initialize the knowledge base
        self.kb = FinancialKnowledgeBase(
            long_term_memory=self.mock_ltm,
            knowledge_dir=self.temp_dir
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test initialization of the knowledge base."""
        # Check that the knowledge directory was created
        self.assertTrue(os.path.exists(self.temp_dir))
        
        # Check that the domain directories were created
        for domain in ["lbo", "ma", "debt", "private_lending", "general"]:
            domain_dir = os.path.join(self.temp_dir, domain)
            self.assertTrue(os.path.exists(domain_dir))
    
    def test_add_knowledge(self):
        """Test adding knowledge to the knowledge base."""
        # Add knowledge
        doc_id = self.kb.add_knowledge(
            domain="lbo",
            topic="capital_structure",
            title="LBO Capital Structure",
            content="Test content",
            source="Test source",
            metadata={"key": "value"}
        )
        
        # Check that the document was added to long-term memory
        self.mock_ltm.add_document.assert_called_once()
        call_args = self.mock_ltm.add_document.call_args[1]
        self.assertEqual(call_args["collection_name"], "lbo")
        self.assertEqual(call_args["text"], "Test content")
        self.assertEqual(call_args["metadata"]["title"], "LBO Capital Structure")
        self.assertEqual(call_args["metadata"]["domain"], "lbo")
        self.assertEqual(call_args["metadata"]["topic"], "capital_structure")
        self.assertEqual(call_args["metadata"]["source"], "Test source")
        self.assertEqual(call_args["metadata"]["type"], "knowledge")
        self.assertEqual(call_args["metadata"]["key"], "value")
        
        # Check that the document ID was returned
        self.assertIsNotNone(doc_id)
        
        # Check that the knowledge file was created
        knowledge_file = os.path.join(self.temp_dir, "lbo", "capital_structure", "LBO Capital Structure.json")
        self.assertTrue(os.path.exists(knowledge_file))
        
        # Check the content of the knowledge file
        with open(knowledge_file, "r") as f:
            knowledge = json.load(f)
            self.assertEqual(knowledge["title"], "LBO Capital Structure")
            self.assertEqual(knowledge["content"], "Test content")
            self.assertEqual(knowledge["domain"], "lbo")
            self.assertEqual(knowledge["topic"], "capital_structure")
            self.assertEqual(knowledge["source"], "Test source")
            self.assertEqual(knowledge["metadata"]["key"], "value")
    
    def test_get_knowledge(self):
        """Test getting knowledge from the knowledge base."""
        # Add knowledge
        doc_id = self.kb.add_knowledge(
            domain="lbo",
            topic="capital_structure",
            title="LBO Capital Structure",
            content="Test content"
        )
        
        # Set up mock response
        self.mock_ltm.get_document.return_value = {
            "id": doc_id,
            "text": "Test content",
            "metadata": {
                "title": "LBO Capital Structure",
                "domain": "lbo",
                "topic": "capital_structure",
                "type": "knowledge"
            }
        }
        
        # Get knowledge
        knowledge = self.kb.get_knowledge(doc_id)
        
        # Check that the document was retrieved from long-term memory
        self.mock_ltm.get_document.assert_called_once_with(
            doc_id=doc_id,
            collection_name="lbo"
        )
        
        # Check that the knowledge was returned
        self.assertEqual(knowledge["title"], "LBO Capital Structure")
        self.assertEqual(knowledge["content"], "Test content")
        self.assertEqual(knowledge["domain"], "lbo")
        self.assertEqual(knowledge["topic"], "capital_structure")
    
    def test_search_knowledge(self):
        """Test searching for knowledge in the knowledge base."""
        # Set up mock response
        self.mock_ltm.search.return_value = [
            {
                "id": "test_id",
                "text": "Test content",
                "metadata": {
                    "title": "LBO Capital Structure",
                    "domain": "lbo",
                    "topic": "capital_structure",
                    "type": "knowledge"
                },
                "distance": 0.1
            }
        ]
        
        # Search for knowledge
        results = self.kb.search_knowledge(
            query="capital structure",
            domain="lbo",
            topic="capital_structure",
            k=5
        )
        
        # Check that the search was performed
        self.mock_ltm.search.assert_called_once()
        call_args = self.mock_ltm.search.call_args[1]
        self.assertEqual(call_args["query"], "capital structure")
        self.assertEqual(call_args["collection_name"], "lbo")
        self.assertEqual(call_args["filters"]["topic"], "capital_structure")
        self.assertEqual(call_args["filters"]["type"], "knowledge")
        self.assertEqual(call_args["k"], 5)
        
        # Check that the results were returned
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "LBO Capital Structure")
        self.assertEqual(results[0]["content"], "Test content")
        self.assertEqual(results[0]["domain"], "lbo")
        self.assertEqual(results[0]["topic"], "capital_structure")
        self.assertEqual(results[0]["distance"], 0.1)
    
    def test_get_knowledge_by_topic(self):
        """Test getting knowledge by topic."""
        # Set up mock response
        self.mock_ltm.search_by_metadata.return_value = [
            {
                "id": "test_id",
                "text": "Test content",
                "metadata": {
                    "title": "LBO Capital Structure",
                    "domain": "lbo",
                    "topic": "capital_structure",
                    "type": "knowledge"
                }
            }
        ]
        
        # Get knowledge by topic
        results = self.kb.get_knowledge_by_topic(
            domain="lbo",
            topic="capital_structure"
        )
        
        # Check that the search was performed
        self.mock_ltm.search_by_metadata.assert_called_once()
        call_args = self.mock_ltm.search_by_metadata.call_args[1]
        self.assertEqual(call_args["collection_name"], "lbo")
        self.assertEqual(call_args["filters"]["topic"], "capital_structure")
        self.assertEqual(call_args["filters"]["type"], "knowledge")
        
        # Check that the results were returned
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "LBO Capital Structure")
        self.assertEqual(results[0]["content"], "Test content")
        self.assertEqual(results[0]["domain"], "lbo")
        self.assertEqual(results[0]["topic"], "capital_structure")
    
    def test_update_knowledge(self):
        """Test updating knowledge in the knowledge base."""
        # Add knowledge
        doc_id = self.kb.add_knowledge(
            domain="lbo",
            topic="capital_structure",
            title="LBO Capital Structure",
            content="Test content"
        )
        
        # Update knowledge
        self.kb.update_knowledge(
            doc_id=doc_id,
            domain="lbo",
            topic="capital_structure",
            title="LBO Capital Structure",
            content="Updated content",
            source="Updated source",
            metadata={"key": "updated_value"}
        )
        
        # Check that the document was updated in long-term memory
        self.mock_ltm.update_document.assert_called_once()
        call_args = self.mock_ltm.update_document.call_args[1]
        self.assertEqual(call_args["doc_id"], doc_id)
        self.assertEqual(call_args["collection_name"], "lbo")
        self.assertEqual(call_args["text"], "Updated content")
        self.assertEqual(call_args["metadata"]["title"], "LBO Capital Structure")
        self.assertEqual(call_args["metadata"]["domain"], "lbo")
        self.assertEqual(call_args["metadata"]["topic"], "capital_structure")
        self.assertEqual(call_args["metadata"]["source"], "Updated source")
        self.assertEqual(call_args["metadata"]["type"], "knowledge")
        self.assertEqual(call_args["metadata"]["key"], "updated_value")
        
        # Check that the knowledge file was updated
        knowledge_file = os.path.join(self.temp_dir, "lbo", "capital_structure", "LBO Capital Structure.json")
        self.assertTrue(os.path.exists(knowledge_file))
        
        # Check the content of the knowledge file
        with open(knowledge_file, "r") as f:
            knowledge = json.load(f)
            self.assertEqual(knowledge["title"], "LBO Capital Structure")
            self.assertEqual(knowledge["content"], "Updated content")
            self.assertEqual(knowledge["domain"], "lbo")
            self.assertEqual(knowledge["topic"], "capital_structure")
            self.assertEqual(knowledge["source"], "Updated source")
            self.assertEqual(knowledge["metadata"]["key"], "updated_value")
    
    def test_delete_knowledge(self):
        """Test deleting knowledge from the knowledge base."""
        # Add knowledge
        doc_id = self.kb.add_knowledge(
            domain="lbo",
            topic="capital_structure",
            title="LBO Capital Structure",
            content="Test content"
        )
        
        # Set up mock response
        self.mock_ltm.get_document.return_value = {
            "id": doc_id,
            "text": "Test content",
            "metadata": {
                "title": "LBO Capital Structure",
                "domain": "lbo",
                "topic": "capital_structure",
                "type": "knowledge"
            }
        }
        
        # Delete knowledge
        self.kb.delete_knowledge(doc_id)
        
        # Check that the document was deleted from long-term memory
        self.mock_ltm.delete_document.assert_called_once_with(
            doc_id=doc_id,
            collection_name="lbo"
        )
        
        # Check that the knowledge file was deleted
        knowledge_file = os.path.join(self.temp_dir, "lbo", "capital_structure", "LBO Capital Structure.json")
        self.assertFalse(os.path.exists(knowledge_file))
    
    def test_load_knowledge_from_file(self):
        """Test loading knowledge from a file."""
        # Create a knowledge file
        knowledge_dir = os.path.join(self.temp_dir, "lbo", "capital_structure")
        os.makedirs(knowledge_dir, exist_ok=True)
        knowledge_file = os.path.join(knowledge_dir, "LBO Capital Structure.json")
        
        knowledge_data = {
            "title": "LBO Capital Structure",
            "content": "Test content",
            "domain": "lbo",
            "topic": "capital_structure",
            "source": "Test source",
            "metadata": {"key": "value"}
        }
        
        with open(knowledge_file, "w") as f:
            json.dump(knowledge_data, f)
        
        # Load knowledge from file
        doc_id = self.kb.load_knowledge_from_file(knowledge_file)
        
        # Check that the document was added to long-term memory
        self.mock_ltm.add_document.assert_called_once()
        call_args = self.mock_ltm.add_document.call_args[1]
        self.assertEqual(call_args["collection_name"], "lbo")
        self.assertEqual(call_args["text"], "Test content")
        self.assertEqual(call_args["metadata"]["title"], "LBO Capital Structure")
        self.assertEqual(call_args["metadata"]["domain"], "lbo")
        self.assertEqual(call_args["metadata"]["topic"], "capital_structure")
        self.assertEqual(call_args["metadata"]["source"], "Test source")
        self.assertEqual(call_args["metadata"]["type"], "knowledge")
        self.assertEqual(call_args["metadata"]["key"], "value")
        
        # Check that the document ID was returned
        self.assertIsNotNone(doc_id)
    
    def test_load_knowledge_directory(self):
        """Test loading knowledge from a directory."""
        # Create knowledge files
        for domain in ["lbo", "ma"]:
            for topic in ["capital_structure", "valuation"]:
                topic_dir = os.path.join(self.temp_dir, domain, topic)
                os.makedirs(topic_dir, exist_ok=True)
                
                for i in range(2):
                    knowledge_file = os.path.join(topic_dir, f"Test Knowledge {i}.json")
                    
                    knowledge_data = {
                        "title": f"Test Knowledge {i}",
                        "content": f"Test content {i}",
                        "domain": domain,
                        "topic": topic,
                        "source": f"Test source {i}",
                        "metadata": {"key": f"value{i}"}
                    }
                    
                    with open(knowledge_file, "w") as f:
                        json.dump(knowledge_data, f)
        
        # Load knowledge from directory
        doc_ids = self.kb.load_knowledge_directory(self.temp_dir)
        
        # Check that the documents were added to long-term memory
        self.assertEqual(self.mock_ltm.add_document.call_count, 8)  # 2 domains * 2 topics * 2 files
        
        # Check that the document IDs were returned
        self.assertEqual(len(doc_ids), 8)
    
    def test_get_all_topics(self):
        """Test getting all topics."""
        # Create topic directories
        for domain in ["lbo", "ma"]:
            for topic in ["capital_structure", "valuation"]:
                topic_dir = os.path.join(self.temp_dir, domain, topic)
                os.makedirs(topic_dir, exist_ok=True)
        
        # Get all topics
        topics = self.kb.get_all_topics()
        
        # Check that the topics were returned
        self.assertEqual(len(topics), 4)  # 2 domains * 2 topics
        self.assertIn(("lbo", "capital_structure"), topics)
        self.assertIn(("lbo", "valuation"), topics)
        self.assertIn(("ma", "capital_structure"), topics)
        self.assertIn(("ma", "valuation"), topics)
    
    def test_get_topics_by_domain(self):
        """Test getting topics by domain."""
        # Create topic directories
        for domain in ["lbo", "ma"]:
            for topic in ["capital_structure", "valuation"]:
                topic_dir = os.path.join(self.temp_dir, domain, topic)
                os.makedirs(topic_dir, exist_ok=True)
        
        # Get topics by domain
        lbo_topics = self.kb.get_topics_by_domain("lbo")
        
        # Check that the topics were returned
        self.assertEqual(len(lbo_topics), 2)
        self.assertIn("capital_structure", lbo_topics)
        self.assertIn("valuation", lbo_topics)

if __name__ == "__main__":
    unittest.main()
