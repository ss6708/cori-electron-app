"""
Long-term memory for Cori RAG++ system.
This module provides a long-term memory for storing and retrieving knowledge.
"""

import os
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime
import chromadb
from chromadb.config import Settings

from .utils.embedding_model import EmbeddingModel

class LongTermMemory:
    """
    Long-term memory for storing and retrieving knowledge.
    Uses ChromaDB as the vector database.
    """
    
    def __init__(
        self,
        persist_directory: str = "chroma_db",
        embedding_model: Optional[EmbeddingModel] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the long-term memory.
        
        Args:
            persist_directory: Directory for persisting the vector database
            embedding_model: Embedding model to use
            api_key: API key for the embedding model
        """
        self.persist_directory = persist_directory
        
        # Create embedding model if not provided
        if embedding_model:
            self.embedding_model = embedding_model
        else:
            self.embedding_model = EmbeddingModel(
                api_key=api_key,
                cache_embeddings=True
            )
        
        # Create ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # Create collections for each domain
        self.domains = ["lbo", "ma", "debt", "private_lending", "general", "preferences"]
        self.collections = {}
        
        for domain in self.domains:
            try:
                self.collections[domain] = self.client.get_or_create_collection(
                    name=domain,
                    metadata={"domain": domain}
                )
            except Exception as e:
                print(f"Error creating collection for domain {domain}: {e}")
    
    def add_document(
        self,
        collection_name: str,
        text: str,
        metadata: Dict[str, Any],
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add a document to the long-term memory.
        
        Args:
            collection_name: Name of the collection to add the document to
            text: Text of the document
            metadata: Metadata for the document
            doc_id: ID of the document
            
        Returns:
            ID of the added document
        """
        # Generate ID if not provided
        if not doc_id:
            doc_id = str(uuid.uuid4())
        
        # Get collection
        collection = self.collections.get(collection_name)
        if not collection:
            raise ValueError(f"Collection {collection_name} not found")
        
        # Generate embedding
        embedding = self.embedding_model.embed_text(text)
        
        # Add document to collection
        collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[text]
        )
        
        return doc_id
    
    def get_document(
        self,
        doc_id: str,
        collection_name: str
    ) -> Dict[str, Any]:
        """
        Get a document from the long-term memory.
        
        Args:
            doc_id: ID of the document
            collection_name: Name of the collection to get the document from
            
        Returns:
            Document data
        """
        # Get collection
        collection = self.collections.get(collection_name)
        if not collection:
            raise ValueError(f"Collection {collection_name} not found")
        
        # Get document
        result = collection.get(
            ids=[doc_id],
            include=["embeddings", "metadatas", "documents"]
        )
        
        if not result["ids"]:
            return {}
        
        return {
            "id": result["ids"][0],
            "text": result["documents"][0],
            "metadata": result["metadatas"][0],
            "embedding": result["embeddings"][0]
        }
    
    def search(
        self,
        query: str,
        collection_name: str,
        filters: Optional[Dict[str, Any]] = None,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for documents in the long-term memory.
        
        Args:
            query: Query to search for
            collection_name: Name of the collection to search in
            filters: Filters to apply to the search
            k: Number of results to return
            
        Returns:
            List of document data
        """
        # Get collection
        collection = self.collections.get(collection_name)
        if not collection:
            raise ValueError(f"Collection {collection_name} not found")
        
        # Generate embedding
        embedding = self.embedding_model.embed_text(query)
        
        # Search collection
        result = collection.query(
            query_embeddings=[embedding],
            n_results=k,
            where=filters,
            include=["metadatas", "documents", "distances"]
        )
        
        if not result["ids"]:
            return []
        
        # Format results
        formatted_results = []
        for i in range(len(result["ids"][0])):
            formatted_results.append({
                "id": result["ids"][0][i],
                "text": result["documents"][0][i],
                "metadata": result["metadatas"][0][i],
                "distance": result["distances"][0][i]
            })
        
        return formatted_results
    
    def search_by_metadata(
        self,
        collection_name: str,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Search for documents by metadata.
        
        Args:
            collection_name: Name of the collection to search in
            filters: Filters to apply to the search
            
        Returns:
            List of document data
        """
        # Get collection
        collection = self.collections.get(collection_name)
        if not collection:
            raise ValueError(f"Collection {collection_name} not found")
        
        # Search collection
        result = collection.get(
            where=filters,
            include=["metadatas", "documents"]
        )
        
        if not result["ids"]:
            return []
        
        # Format results
        formatted_results = []
        for i in range(len(result["ids"])):
            formatted_results.append({
                "id": result["ids"][i],
                "text": result["documents"][i],
                "metadata": result["metadatas"][i]
            })
        
        return formatted_results
    
    def update_document(
        self,
        doc_id: str,
        collection_name: str,
        text: str,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Update a document in the long-term memory.
        
        Args:
            doc_id: ID of the document
            collection_name: Name of the collection to update the document in
            text: Text of the document
            metadata: Metadata for the document
        """
        # Get collection
        collection = self.collections.get(collection_name)
        if not collection:
            raise ValueError(f"Collection {collection_name} not found")
        
        # Generate embedding
        embedding = self.embedding_model.embed_text(text)
        
        # Update document
        collection.update(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[text]
        )
    
    def delete_document(
        self,
        doc_id: str,
        collection_name: str
    ) -> None:
        """
        Delete a document from the long-term memory.
        
        Args:
            doc_id: ID of the document
            collection_name: Name of the collection to delete the document from
        """
        # Get collection
        collection = self.collections.get(collection_name)
        if not collection:
            raise ValueError(f"Collection {collection_name} not found")
        
        # Delete document
        collection.delete(
            ids=[doc_id]
        )
    
    def get_collection_stats(
        self,
        collection_name: str
    ) -> Dict[str, Any]:
        """
        Get statistics for a collection.
        
        Args:
            collection_name: Name of the collection to get statistics for
            
        Returns:
            Collection statistics
        """
        # Get collection
        collection = self.collections.get(collection_name)
        if not collection:
            raise ValueError(f"Collection {collection_name} not found")
        
        # Get collection count
        count = collection.count()
        
        return {
            "name": collection_name,
            "count": count
        }
    
    def get_all_collection_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all collections.
        
        Returns:
            Dictionary of collection statistics
        """
        stats = {}
        for domain in self.domains:
            try:
                stats[domain] = self.get_collection_stats(domain)
            except:
                stats[domain] = {"name": domain, "count": 0}
        
        return stats
    
    def clear_collection(
        self,
        collection_name: str
    ) -> None:
        """
        Clear a collection.
        
        Args:
            collection_name: Name of the collection to clear
        """
        # Get collection
        collection = self.collections.get(collection_name)
        if not collection:
            raise ValueError(f"Collection {collection_name} not found")
        
        # Clear collection
        collection.delete(
            where={}
        )
    
    def clear_all_collections(self) -> None:
        """Clear all collections."""
        for domain in self.domains:
            try:
                self.clear_collection(domain)
            except:
                pass
