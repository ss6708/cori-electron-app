"""
Embedding model for Cori RAG++ system.
This module provides an embedding model for generating embeddings.
"""

import os
from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np

from openai import OpenAI

class EmbeddingModel:
    """
    Embedding model for generating embeddings.
    Uses OpenAI's embedding API.
    """
    
    def __init__(
        self,
        model_name: str = "text-embedding-ada-002",
        api_key: Optional[str] = None,
        dimensions: int = 1536,
        cache_embeddings: bool = True
    ):
        """
        Initialize the embedding model.
        
        Args:
            model_name: Name of the embedding model
            api_key: API key for OpenAI
            dimensions: Dimensions of the embeddings
            cache_embeddings: Whether to cache embeddings
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model_name = model_name
        self.dimensions = dimensions
        self.cache_embeddings = cache_embeddings
        self.embedding_cache = {}
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate an embedding for a text.
        
        Args:
            text: Text to generate an embedding for
            
        Returns:
            Embedding for the text
        """
        # Check cache
        if self.cache_embeddings and text in self.embedding_cache:
            return self.embedding_cache[text]
        
        # Generate embedding
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text
        )
        
        embedding = response.data[0].embedding
        
        # Cache embedding
        if self.cache_embeddings:
            self.embedding_cache[text] = embedding
        
        return embedding
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: Texts to generate embeddings for
            
        Returns:
            Embeddings for the texts
        """
        # Check cache
        if self.cache_embeddings:
            cached_embeddings = []
            uncached_texts = []
            uncached_indices = []
            
            for i, text in enumerate(texts):
                if text in self.embedding_cache:
                    cached_embeddings.append((i, self.embedding_cache[text]))
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
            
            # If all texts are cached, return cached embeddings
            if len(uncached_texts) == 0:
                embeddings = [None] * len(texts)
                for i, embedding in cached_embeddings:
                    embeddings[i] = embedding
                return embeddings
        else:
            uncached_texts = texts
            uncached_indices = list(range(len(texts)))
        
        # Generate embeddings for uncached texts
        response = self.client.embeddings.create(
            model=self.model_name,
            input=uncached_texts
        )
        
        # Create embeddings list
        if self.cache_embeddings:
            embeddings = [None] * len(texts)
            for i, embedding in cached_embeddings:
                embeddings[i] = embedding
            
            for i, embedding_data in zip(uncached_indices, response.data):
                embedding = embedding_data.embedding
                embeddings[i] = embedding
                self.embedding_cache[uncached_texts[uncached_indices.index(i)]] = embedding
        else:
            embeddings = [embedding_data.embedding for embedding_data in response.data]
        
        return embeddings
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate the similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity between the texts
        """
        # Generate embeddings
        embedding1 = self.embed_text(text1)
        embedding2 = self.embed_text(text2)
        
        # Calculate similarity
        return self._cosine_similarity(embedding1, embedding2)
    
    def similarities(self, query: str, texts: List[str]) -> List[float]:
        """
        Calculate the similarities between a query and multiple texts.
        
        Args:
            query: Query text
            texts: Texts to calculate similarities with
            
        Returns:
            Similarities between the query and the texts
        """
        # Generate embeddings
        query_embedding = self.embed_text(query)
        text_embeddings = self.embed_texts(texts)
        
        # Calculate similarities
        return [self._cosine_similarity(query_embedding, text_embedding) for text_embedding in text_embeddings]
    
    def _cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate the cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity between the embeddings
        """
        # Convert to numpy arrays
        a = np.array(embedding1)
        b = np.array(embedding2)
        
        # Calculate cosine similarity
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self.embedding_cache = {}
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding model.
        
        Returns:
            Information about the embedding model
        """
        return {
            "model_name": self.model_name,
            "dimensions": self.dimensions,
            "cache_size": len(self.embedding_cache)
        }
