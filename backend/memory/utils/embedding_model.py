from typing import List, Dict, Any, Optional, Union
import os
import numpy as np
from openai import OpenAI

class EmbeddingModel:
    """
    Handles generating embeddings for text using OpenAI's embedding API.
    """
    
    def __init__(self, model_name: str = "text-embedding-3-small"):
        """
        Initialize the embedding model.
        
        Args:
            model_name: Name of the OpenAI embedding model to use
        """
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model_name = model_name
        self.embedding_cache = {}
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate an embedding for the given text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        # Check cache first
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        # Generate embedding
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text
        )
        
        embedding = response.data[0].embedding
        
        # Cache embedding
        self.embedding_cache[text] = embedding
        
        return embedding
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        # Check which texts are not in cache
        uncached_texts = []
        uncached_indices = []
        
        for i, text in enumerate(texts):
            if text not in self.embedding_cache:
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # If all texts are cached, return from cache
        if not uncached_texts:
            return [self.embedding_cache[text] for text in texts]
        
        # Generate embeddings for uncached texts
        response = self.client.embeddings.create(
            model=self.model_name,
            input=uncached_texts
        )
        
        embeddings = [data.embedding for data in response.data]
        
        # Cache embeddings
        for text, embedding in zip(uncached_texts, embeddings):
            self.embedding_cache[text] = embedding
        
        # Combine cached and new embeddings
        result = []
        uncached_idx = 0
        
        for i in range(len(texts)):
            if i in uncached_indices:
                result.append(embeddings[uncached_idx])
                uncached_idx += 1
            else:
                result.append(self.embedding_cache[texts[i]])
        
        return result
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate the cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity (0-1)
        """
        embedding1 = self.embed_text(text1)
        embedding2 = self.embed_text(text2)
        
        return self._cosine_similarity(embedding1, embedding2)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity (0-1)
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        return dot_product / (norm1 * norm2)
    
    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self.embedding_cache = {}
