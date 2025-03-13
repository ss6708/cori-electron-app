"""
Tests for the long-term memory system.
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

from memory.models.event import Event
from memory.long_term_memory import LongTermMemory

class TestLongTermMemory(unittest.TestCase):
    """Test cases for the LongTermMemory class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for the vector store
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock the embedding model
        self.mock_embedding_model_patcher = patch('memory.long_term_memory.EmbeddingModel')
        self.mock_embedding_model = self.mock_embedding_model_patcher.start()
        
        # Mock the embedding functions
        self.mock_embedding_functions_patcher = patch('memory.long_term_memory.embedding_functions')
        self.mock_embedding_functions = self.mock_embedding_functions_patcher.start()
        
        # Mock ChromaDB
        self.mock_chromadb_patcher = patch('memory.long_term_memory.chromadb')
        self.mock_chromadb = self.mock_chromadb_patcher.start()
        
        # Set up mock client
        self.mock_client = MagicMock()
        self.mock_chromadb.PersistentClient.return_value = self.mock_client
        
        # Set up mock collections
        self.mock_collections = {}
        for domain in ["lbo", "ma", "debt", "private_lending", "general", "preferences", "sessions"]:
            mock_collection = MagicMock()
            self.mock_collections[domain] = mock_collection
            self.mock_client.get_or_create_collection.return_value = mock_collection
        
        # Initialize the long-term memory
        self.ltm = LongTermMemory(
            vector_store_dir=self.temp_dir,
            embedding_model_name="text-embedding-ada-002",
            api_key="test_api_key"
        )
        
        # Set up the mock collections in the LTM
        self.ltm.collections = self.mock_collections
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Stop the patchers
        self.mock_embedding_model_patcher.stop()
        self.mock_embedding_functions_patcher.stop()
        self.mock_chromadb_patcher.stop()
        
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test initialization of the long-term memory."""
        # Check that the client was created
        self.mock_chromadb.PersistentClient.assert_called_once()
        
        # Check that the embedding model was created
        self.mock_embedding_model.assert_called_once()
        
        # Check that the collections were created
        self.assertEqual(len(self.ltm.collections), 7)
    
    def test_add_document(self):
        """Test adding a document to a collection."""
        # Set up mock collection
        mock_collection = MagicMock()
        self.ltm.collections["test_collection"] = mock_collection
        
        # Add a document
        doc_id = self.ltm.add_document(
            collection_name="test_collection",
            text="Test document",
            metadata={"key": "value"}
        )
        
        # Check that the document was added
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args[1]
        self.assertEqual(len(call_args["ids"]), 1)
        self.assertEqual(call_args["documents"], ["Test document"])
        self.assertEqual(call_args["metadatas"], [{"key": "value"}])
        
        # Check that the document ID was returned
        self.assertIsNotNone(doc_id)
    
    def test_add_event(self):
        """Test adding an event to a collection."""
        # Set up mock collection
        mock_collection = MagicMock()
        self.ltm.collections["lbo"] = mock_collection
        
        # Create an event
        event = Event(
            id="test_id",
            role="user",
            content="Test event",
            timestamp="2023-01-01T00:00:00Z"
        )
        
        # Add the event
        doc_id = self.ltm.add_event(
            event=event,
            domain="lbo"
        )
        
        # Check that the document was added
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args[1]
        self.assertEqual(call_args["ids"], ["test_id"])
        self.assertEqual(call_args["documents"], ["Test event"])
        self.assertEqual(call_args["metadatas"][0]["role"], "user")
        self.assertEqual(call_args["metadatas"][0]["timestamp"], "2023-01-01T00:00:00Z")
        self.assertEqual(call_args["metadatas"][0]["domain"], "lbo")
        
        # Check that the document ID was returned
        self.assertEqual(doc_id, "test_id")
    
    def test_search(self):
        """Test searching for documents."""
        # Set up mock collection
        mock_collection = MagicMock()
        self.ltm.collections["general"] = mock_collection
        
        # Set up mock response
        mock_collection.query.return_value = {
            "documents": [["Test document"]],
            "metadatas": [[{"key": "value"}]],
            "distances": [[0.1]]
        }
        
        # Search for documents
        results = self.ltm.search(
            query="Test query",
            collection_name="general",
            filters={"key": "value"},
            k=5
        )
        
        # Check that the search was performed
        mock_collection.query.assert_called_once()
        call_args = mock_collection.query.call_args[1]
        self.assertEqual(call_args["query_texts"], ["Test query"])
        self.assertEqual(call_args["n_results"], 5)
        self.assertEqual(call_args["where"], {"key": "value"})
        
        # Check the results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["text"], "Test document")
        self.assertEqual(results[0]["metadata"], {"key": "value"})
        self.assertEqual(results[0]["distance"], 0.1)
    
    def test_search_by_metadata(self):
        """Test searching for documents by metadata."""
        # Set up mock collection
        mock_collection = MagicMock()
        self.ltm.collections["general"] = mock_collection
        
        # Set up mock response
        mock_collection.get.return_value = {
            "documents": ["Test document"],
            "metadatas": [{"key": "value"}],
            "ids": ["test_id"]
        }
        
        # Search for documents
        results = self.ltm.search_by_metadata(
            filters={"key": "value"},
            collection_name="general",
            k=5
        )
        
        # Check that the search was performed
        mock_collection.get.assert_called_once()
        call_args = mock_collection.get.call_args[1]
        self.assertEqual(call_args["where"], {"key": "value"})
        self.assertEqual(call_args["limit"], 5)
        
        # Check the results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["text"], "Test document")
        self.assertEqual(results[0]["metadata"], {"key": "value"})
        self.assertEqual(results[0]["id"], "test_id")
    
    def test_multi_domain_search(self):
        """Test searching across multiple domains."""
        # Set up mock collections
        for domain in ["lbo", "ma"]:
            mock_collection = MagicMock()
            self.ltm.collections[domain] = mock_collection
            
            # Set up mock response
            mock_collection.query.return_value = {
                "documents": [[f"Test document for {domain}"]],
                "metadatas": [[{"domain": domain}]],
                "distances": [[0.1]]
            }
        
        # Search across domains
        results = self.ltm.multi_domain_search(
            query="Test query",
            domains=["lbo", "ma"],
            filters={"key": "value"},
            k_per_domain=3
        )
        
        # Check that the searches were performed
        for domain in ["lbo", "ma"]:
            self.ltm.collections[domain].query.assert_called_once()
            call_args = self.ltm.collections[domain].query.call_args[1]
            self.assertEqual(call_args["query_texts"], ["Test query"])
            self.assertEqual(call_args["n_results"], 3)
            self.assertEqual(call_args["where"], {"key": "value"})
        
        # Check the results
        self.assertEqual(len(results), 2)
        self.assertEqual(len(results["lbo"]), 1)
        self.assertEqual(len(results["ma"]), 1)
        self.assertEqual(results["lbo"][0]["text"], "Test document for lbo")
        self.assertEqual(results["ma"][0]["text"], "Test document for ma")
    
    def test_delete_document(self):
        """Test deleting a document."""
        # Set up mock collection
        mock_collection = MagicMock()
        self.ltm.collections["general"] = mock_collection
        
        # Delete a document
        self.ltm.delete_document(
            doc_id="test_id",
            collection_name="general"
        )
        
        # Check that the document was deleted
        mock_collection.delete.assert_called_once()
        call_args = mock_collection.delete.call_args[1]
        self.assertEqual(call_args["ids"], ["test_id"])
    
    def test_update_document(self):
        """Test updating a document."""
        # Set up mock collection
        mock_collection = MagicMock()
        self.ltm.collections["general"] = mock_collection
        
        # Update a document
        self.ltm.update_document(
            doc_id="test_id",
            text="Updated document",
            metadata={"key": "updated_value"},
            collection_name="general"
        )
        
        # Check that the document was updated
        mock_collection.update.assert_called_once()
        call_args = mock_collection.update.call_args[1]
        self.assertEqual(call_args["ids"], ["test_id"])
        self.assertEqual(call_args["documents"], ["Updated document"])
        self.assertEqual(call_args["metadatas"], [{"key": "updated_value"}])
    
    def test_get_document(self):
        """Test getting a document by ID."""
        # Set up mock collection
        mock_collection = MagicMock()
        self.ltm.collections["general"] = mock_collection
        
        # Set up mock response
        mock_collection.get.return_value = {
            "documents": ["Test document"],
            "metadatas": [{"key": "value"}],
            "ids": ["test_id"]
        }
        
        # Get a document
        result = self.ltm.get_document(
            doc_id="test_id",
            collection_name="general"
        )
        
        # Check that the document was retrieved
        mock_collection.get.assert_called_once()
        call_args = mock_collection.get.call_args[1]
        self.assertEqual(call_args["ids"], ["test_id"])
        
        # Check the result
        self.assertEqual(result["text"], "Test document")
        self.assertEqual(result["metadata"], {"key": "value"})
        self.assertEqual(result["id"], "test_id")
    
    def test_export_import_collection(self):
        """Test exporting and importing a collection."""
        # Set up mock collection
        mock_collection = MagicMock()
        self.ltm.collections["general"] = mock_collection
        
        # Set up mock response for export
        mock_collection.get.return_value = {
            "documents": ["Test document"],
            "metadatas": [{"key": "value"}],
            "ids": ["test_id"]
        }
        
        # Create a temporary file for export/import
        temp_file = os.path.join(self.temp_dir, "export.json")
        
        # Export the collection
        self.ltm.export_collection(
            collection_name="general",
            output_file=temp_file
        )
        
        # Check that the collection was exported
        mock_collection.get.assert_called_once()
        
        # Check that the file was created
        self.assertTrue(os.path.exists(temp_file))
        
        # Import the collection
        self.ltm.import_collection(
            collection_name="imported",
            input_file=temp_file
        )
        
        # Check that the collection was imported
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args[1]
        self.assertEqual(call_args["ids"], ["test_id"])
        self.assertEqual(call_args["documents"], ["Test document"])
        self.assertEqual(call_args["metadatas"], [{"key": "value"}])
    
    def test_get_collection_stats(self):
        """Test getting collection statistics."""
        # Set up mock collection
        mock_collection = MagicMock()
        self.ltm.collections["general"] = mock_collection
        mock_collection.metadata = {"domain": "general"}
        
        # Set up mock response
        mock_collection.get.return_value = {
            "documents": ["Test document 1", "Test document 2"],
            "metadatas": [{"key": "value1"}, {"key": "value2"}],
            "ids": ["test_id1", "test_id2"]
        }
        
        # Get collection statistics
        stats = self.ltm.get_collection_stats(
            collection_name="general"
        )
        
        # Check that the statistics were retrieved
        mock_collection.get.assert_called_once()
        
        # Check the statistics
        self.assertEqual(stats["count"], 2)
        self.assertEqual(stats["collection_name"], "general")
        self.assertEqual(stats["metadata"], {"domain": "general"})
    
    def test_get_all_collections(self):
        """Test getting all collection names."""
        # Get all collections
        collections = self.ltm.get_all_collections()
        
        # Check the collections
        self.assertEqual(len(collections), 7)
        self.assertIn("lbo", collections)
        self.assertIn("ma", collections)
        self.assertIn("debt", collections)
        self.assertIn("private_lending", collections)
        self.assertIn("general", collections)
        self.assertIn("preferences", collections)
        self.assertIn("sessions", collections)
    
    def test_clear_collection(self):
        """Test clearing a collection."""
        # Set up mock collection
        mock_collection = MagicMock()
        self.ltm.collections["general"] = mock_collection
        
        # Set up mock response
        mock_collection.get.return_value = {
            "documents": ["Test document 1", "Test document 2"],
            "metadatas": [{"key": "value1"}, {"key": "value2"}],
            "ids": ["test_id1", "test_id2"]
        }
        
        # Clear the collection
        self.ltm.clear_collection(
            collection_name="general"
        )
        
        # Check that the collection was cleared
        mock_collection.get.assert_called_once()
        mock_collection.delete.assert_called_once()
        call_args = mock_collection.delete.call_args[1]
        self.assertEqual(call_args["ids"], ["test_id1", "test_id2"])
    
    def test_delete_collection(self):
        """Test deleting a collection."""
        # Delete a collection
        self.ltm.delete_collection(
            collection_name="general"
        )
        
        # Check that the collection was deleted
        self.mock_client.delete_collection.assert_called_once_with("general")
        
        # Check that the collection was removed from the collections dict
        self.assertNotIn("general", self.ltm.collections)


if __name__ == "__main__":
    unittest.main()
