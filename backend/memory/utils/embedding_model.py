"""
Embedding model for Cori RAG++ system.
"""

import os
from typing import List, Optional, Any, Dict, Union
import numpy as np
from openai import OpenAI

class EmbeddingModel:
    """
    Wrapper for embedding models.
    Currently supports OpenAI's embedding models.
    """
    
    def __init__(
        self,
        model_name: str = "text-embedding-ada-002",
        api_key: Optional[str] = None,
        dimensions: Optional[int] = None,
        cache_embeddings: bool = True
    ):
        """
        Initialize the embedding model.
        
        Args:
            model_name: Name of the embedding model
            api_key: API key for the model provider
            dimensions: Dimensions of the embeddings
            cache_embeddings: Whether to cache embeddings
        """
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found")
        
        self.client = OpenAI(api_key=self.api_key)
        self.dimensions = dimensions
        self.cache_embeddings = cache_embeddings
        self.embedding_cache: Dict[str, List[float]] = {}
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embeddings for a text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
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
            texts: Texts to embed
            
        Returns:
            List of embedding vectors
        """
        # Check cache for all texts
        if self.cache_embeddings:
            cached_embeddings = [self.embedding_cache.get(text) for text in texts]
            if all(cached_embeddings):
                return cached_embeddings
        
        # Generate embeddings
        response = self.client.embeddings.create(
            model=self.model_name,
            input=texts
        )
        
        embeddings = [data.embedding for data in response.data]
        
        # Cache embeddings
        if self.cache_embeddings:
            for text, embedding in zip(texts, embeddings):
                self.embedding_cache[text] = embedding
        
        return embeddings
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate the cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity
        """
        # Generate embeddings
        embedding1 = self.embed_text(text1)
        embedding2 = self.embed_text(text2)
        
        # Calculate cosine similarity
        return self._cosine_similarity(embedding1, embedding2)
    
    def similarities(self, query: str, texts: List[str]) -> List[float]:
        """
        Calculate the cosine similarities between a query and multiple texts.
        
        Args:
            query: Query text
            texts: Texts to compare
            
        Returns:
            List of cosine similarities
        """
        # Generate embeddings
        query_embedding = self.embed_text(query)
        text_embeddings = self.embed_texts(texts)
        
        # Calculate cosine similarities
        return [self._cosine_similarity(query_embedding, text_embedding) for text_embedding in text_embeddings]
    
    def _cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate the cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity
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
            Model information
        """
        return {
            "model_name": self.model_name,
            "dimensions": self.dimensions,
            "cache_size": len(self.embedding_cache) if self.cache_embeddings else 0
        }
