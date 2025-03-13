"""
Tests for the embedding model.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from memory.utils.embedding_model import EmbeddingModel

class TestEmbeddingModel(unittest.TestCase):
    """Test cases for the EmbeddingModel class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the OpenAI client
        self.mock_openai_patcher = patch('memory.utils.embedding_model.OpenAI')
        self.mock_openai = self.mock_openai_patcher.start()
        
        # Set up mock client
        self.mock_client = MagicMock()
        self.mock_openai.return_value = self.mock_client
        
        # Set up mock response for embeddings
        mock_response = MagicMock()
        mock_data1 = MagicMock()
        mock_data1.embedding = [0.1, 0.2, 0.3]
        mock_data2 = MagicMock()
        mock_data2.embedding = [0.4, 0.5, 0.6]
        mock_response.data = [mock_data1, mock_data2]
        self.mock_client.embeddings.create.return_value = mock_response
        
        # Initialize the embedding model
        self.embedding_model = EmbeddingModel(
            model_name="text-embedding-ada-002",
            api_key="test_api_key",
            dimensions=3,
            cache_embeddings=True
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.mock_openai_patcher.stop()
    
    def test_initialization(self):
        """Test initialization of the embedding model."""
        # Check that the client was created
        self.mock_openai.assert_called_once_with(api_key="test_api_key")
        
        # Check that the model parameters were set
        self.assertEqual(self.embedding_model.model_name, "text-embedding-ada-002")
        self.assertEqual(self.embedding_model.dimensions, 3)
        self.assertTrue(self.embedding_model.cache_embeddings)
        self.assertEqual(len(self.embedding_model.embedding_cache), 0)
    
    def test_initialization_without_api_key(self):
        """Test initialization without an API key."""
        # Mock os.environ.get to return an API key
        with patch('os.environ.get', return_value="env_api_key"):
            # Initialize the embedding model without an API key
            embedding_model = EmbeddingModel(model_name="text-embedding-ada-002")
            
            # Check that the API key was retrieved from the environment
            self.assertEqual(embedding_model.api_key, "env_api_key")
    
    def test_initialization_without_api_key_raises_error(self):
        """Test initialization without an API key raises an error."""
        # Mock os.environ.get to return None
        with patch('os.environ.get', return_value=None):
            # Check that initialization without an API key raises an error
            with self.assertRaises(ValueError):
                EmbeddingModel(model_name="text-embedding-ada-002")
    
    def test_embed_text(self):
        """Test embedding a single text."""
        # Embed a text
        embedding = self.embedding_model.embed_text("Test text")
        
        # Check that the API was called with the right arguments
        self.mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-ada-002",
            input="Test text"
        )
        
        # Check that the embedding was returned
        self.assertEqual(embedding, [0.1, 0.2, 0.3])
        
        # Check that the embedding was cached
        self.assertEqual(len(self.embedding_model.embedding_cache), 1)
        self.assertEqual(self.embedding_model.embedding_cache["Test text"], [0.1, 0.2, 0.3])
        
        # Embed the same text again
        self.mock_client.embeddings.create.reset_mock()
        embedding = self.embedding_model.embed_text("Test text")
        
        # Check that the API was not called again
        self.mock_client.embeddings.create.assert_not_called()
        
        # Check that the cached embedding was returned
        self.assertEqual(embedding, [0.1, 0.2, 0.3])
    
    def test_embed_texts(self):
        """Test embedding multiple texts."""
        # Embed multiple texts
        embeddings = self.embedding_model.embed_texts(["Text 1", "Text 2"])
        
        # Check that the API was called with the right arguments
        self.mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-ada-002",
            input=["Text 1", "Text 2"]
        )
        
        # Check that the embeddings were returned
        self.assertEqual(embeddings, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        
        # Check that the embeddings were cached
        self.assertEqual(len(self.embedding_model.embedding_cache), 2)
        self.assertEqual(self.embedding_model.embedding_cache["Text 1"], [0.1, 0.2, 0.3])
        self.assertEqual(self.embedding_model.embedding_cache["Text 2"], [0.4, 0.5, 0.6])
        
        # Embed the same texts again
        self.mock_client.embeddings.create.reset_mock()
        embeddings = self.embedding_model.embed_texts(["Text 1", "Text 2"])
        
        # Check that the API was not called again
        self.mock_client.embeddings.create.assert_not_called()
        
        # Check that the cached embeddings were returned
        self.assertEqual(embeddings, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
    
    def test_similarity(self):
        """Test calculating similarity between two texts."""
        # Set up mock responses for embeddings
        self.mock_client.embeddings.create.side_effect = [
            MagicMock(data=[MagicMock(embedding=[1.0, 0.0, 0.0])]),
            MagicMock(data=[MagicMock(embedding=[0.0, 1.0, 0.0])])
        ]
        
        # Calculate similarity
        similarity = self.embedding_model.similarity("Text 1", "Text 2")
        
        # Check that the API was called twice
        self.assertEqual(self.mock_client.embeddings.create.call_count, 2)
        
        # Check that the similarity was calculated correctly
        self.assertEqual(similarity, 0.0)  # Orthogonal vectors have zero similarity
        
        # Set up mock responses for embeddings with parallel vectors
        self.mock_client.embeddings.create.side_effect = [
            MagicMock(data=[MagicMock(embedding=[1.0, 0.0, 0.0])]),
            MagicMock(data=[MagicMock(embedding=[1.0, 0.0, 0.0])])
        ]
        
        # Calculate similarity
        similarity = self.embedding_model.similarity("Text 3", "Text 4")
        
        # Check that the similarity was calculated correctly
        self.assertEqual(similarity, 1.0)  # Parallel vectors have similarity 1.0
    
    def test_similarities(self):
        """Test calculating similarities between a query and multiple texts."""
        # Set up mock responses for embeddings
        self.mock_client.embeddings.create.side_effect = [
            MagicMock(data=[MagicMock(embedding=[1.0, 0.0, 0.0])]),
            MagicMock(data=[
                MagicMock(embedding=[0.0, 1.0, 0.0]),
                MagicMock(embedding=[1.0, 0.0, 0.0])
            ])
        ]
        
        # Calculate similarities
        similarities = self.embedding_model.similarities("Query", ["Text 1", "Text 2"])
        
        # Check that the API was called twice
        self.assertEqual(self.mock_client.embeddings.create.call_count, 2)
        
        # Check that the similarities were calculated correctly
        self.assertEqual(similarities, [0.0, 1.0])
    
    def test_cosine_similarity(self):
        """Test calculating cosine similarity between two embeddings."""
        # Calculate cosine similarity
        similarity = self.embedding_model._cosine_similarity([1.0, 0.0, 0.0], [0.0, 1.0, 0.0])
        
        # Check that the similarity was calculated correctly
        self.assertEqual(similarity, 0.0)  # Orthogonal vectors have zero similarity
        
        # Calculate cosine similarity with parallel vectors
        similarity = self.embedding_model._cosine_similarity([1.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        
        # Check that the similarity was calculated correctly
        self.assertEqual(similarity, 1.0)  # Parallel vectors have similarity 1.0
        
        # Calculate cosine similarity with non-orthogonal vectors
        similarity = self.embedding_model._cosine_similarity([1.0, 1.0, 0.0], [1.0, 0.0, 0.0])
        
        # Check that the similarity was calculated correctly
        self.assertAlmostEqual(similarity, 0.7071067811865475)  # cos(45°) = 1/√2
    
    def test_clear_cache(self):
        """Test clearing the embedding cache."""
        # Embed a text to populate the cache
        self.embedding_model.embed_text("Test text")
        
        # Check that the cache was populated
        self.assertEqual(len(self.embedding_model.embedding_cache), 1)
        
        # Clear the cache
        self.embedding_model.clear_cache()
        
        # Check that the cache was cleared
        self.assertEqual(len(self.embedding_model.embedding_cache), 0)
    
    def test_get_model_info(self):
        """Test getting model information."""
        # Embed a text to populate the cache
        self.embedding_model.embed_text("Test text")
        
        # Get model information
        model_info = self.embedding_model.get_model_info()
        
        # Check that the model information was returned
        self.assertEqual(model_info["model_name"], "text-embedding-ada-002")
        self.assertEqual(model_info["dimensions"], 3)
        self.assertEqual(model_info["cache_size"], 1)
    
    def test_no_cache(self):
        """Test embedding without caching."""
        # Initialize the embedding model without caching
        embedding_model = EmbeddingModel(
            model_name="text-embedding-ada-002",
            api_key="test_api_key",
            cache_embeddings=False
        )
        
        # Embed a text
        embedding_model.embed_text("Test text")
        
        # Check that the cache is empty
        self.assertEqual(len(embedding_model.embedding_cache), 0)
        
        # Embed the same text again
        self.mock_client.embeddings.create.reset_mock()
        embedding_model.embed_text("Test text")
        
        # Check that the API was called again
        self.mock_client.embeddings.create.assert_called_once()

if __name__ == "__main__":
    unittest.main()
