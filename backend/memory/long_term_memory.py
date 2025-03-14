"""
Long-term memory system for Cori RAG++ architecture.
This is the third tier of the three-tier memory architecture.
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from .models.event import Event
from .utils.embedding_model import EmbeddingModel

class LongTermMemory:
    """
    Handles storing and retrieving information using ChromaDB.
    This is the third tier of the three-tier memory architecture.
    """
    
    def __init__(
        self,
        vector_store_dir: str = "./data/vector_store",
        embedding_model_name: str = "text-embedding-ada-002",
        api_key: Optional[str] = None,
        create_domain_collections: bool = True
    ):
        """
        Initialize the long-term memory system.
        
        Args:
            vector_store_dir: Directory to store the vector database
            embedding_model_name: Name of the embedding model to use
            api_key: OpenAI API key (defaults to environment variable)
            create_domain_collections: Whether to create domain-specific collections
        """
        # Create vector store directory if it doesn't exist
        os.makedirs(vector_store_dir, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=vector_store_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = EmbeddingModel(
            model_name=embedding_model_name,
            api_key=api_key
        )
        
        # Set up embedding function for ChromaDB
        self.openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key or os.environ.get("OPENAI_API_KEY"),
            model_name=embedding_model_name
        )
        
        # Create collections
        self.collections = {}
        
        if create_domain_collections:
            self._create_domain_collections()
    
    def _create_domain_collections(self) -> None:
        """Create domain-specific collections."""
        # Financial domains
        domains = ["lbo", "ma", "debt", "private_lending", "general"]
        
        # Create collections for each domain
        for domain in domains:
            self.collections[domain] = self.client.get_or_create_collection(
                name=domain,
                embedding_function=self.openai_ef,
                metadata={"domain": domain}
            )
        
        # Create a collection for user preferences
        self.collections["preferences"] = self.client.get_or_create_collection(
            name="preferences",
            embedding_function=self.openai_ef,
            metadata={"type": "preferences"}
        )
        
        # Create a collection for session history
        self.collections["sessions"] = self.client.get_or_create_collection(
            name="sessions",
            embedding_function=self.openai_ef,
            metadata={"type": "sessions"}
        )
    
    def create_collection(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Create a new collection.
        
        Args:
            name: Name of the collection
            metadata: Metadata for the collection
        """
        if name in self.collections:
            return
        
        self.collections[name] = self.client.get_or_create_collection(
            name=name,
            embedding_function=self.openai_ef,
            metadata=metadata or {}
        )
    
    def add_document(
        self,
        collection_name: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add a document to a collection.
        
        Args:
            collection_name: Name of the collection
            text: Text content of the document
            metadata: Metadata for the document
            doc_id: Document ID (generated if not provided)
            
        Returns:
            Document ID
        """
        # Get collection
        collection = self._get_collection(collection_name)
        
        # Generate document ID if not provided
        if doc_id is None:
            doc_id = str(uuid.uuid4())
        
        # Add document to collection
        collection.add(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata or {}]
        )
        
        return doc_id
    
    def add_event(
        self,
        event: Event,
        domain: Optional[str] = "general",
        collection_name: Optional[str] = None
    ) -> str:
        """
        Add an event to the appropriate collection.
        
        Args:
            event: Event to add
            domain: Domain of the event
            collection_name: Name of the collection (defaults to domain)
            
        Returns:
            Document ID
        """
        # Convert event to document format
        doc_id, text, metadata = self._event_to_document(event)
        
        # Add domain to metadata
        metadata["domain"] = domain
        
        # Determine which collection to use
        collection = collection_name or domain
        
        # Add document to collection
        return self.add_document(
            collection_name=collection,
            text=text,
            metadata=metadata,
            doc_id=doc_id
        )
    
    def add_events(
        self,
        events: List[Event],
        domain: Optional[str] = "general",
        collection_name: Optional[str] = None
    ) -> List[str]:
        """
        Add multiple events to the appropriate collection.
        
        Args:
            events: Events to add
            domain: Domain of the events
            collection_name: Name of the collection (defaults to domain)
            
        Returns:
            List of document IDs
        """
        doc_ids = []
        for event in events:
            doc_id = self.add_event(
                event=event,
                domain=domain,
                collection_name=collection_name
            )
            doc_ids.append(doc_id)
        
        return doc_ids
    
    def search(
        self,
        query: str,
        collection_name: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents.
        
        Args:
            query: Query string
            collection_name: Name of the collection to search
            filters: Filters to apply to the search
            k: Number of results to return
            
        Returns:
            List of search results
        """
        # Get collection
        collection = self._get_collection(collection_name or "general")
        
        # Search collection
        results = collection.query(
            query_texts=[query],
            n_results=k,
            where=filters
        )
        
        # Format results
        formatted_results = []
        if results["documents"] and len(results["documents"]) > 0:
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "text": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] and i < len(results["metadatas"][0]) else {},
                    "distance": results["distances"][0][i] if results["distances"] and i < len(results["distances"][0]) else None
                })
        
        return formatted_results
    
    def search_by_metadata(
        self,
        filters: Dict[str, Any],
        collection_name: Optional[str] = None,
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for documents by metadata.
        
        Args:
            filters: Filters to apply to the search
            collection_name: Name of the collection to search
            k: Number of results to return
            
        Returns:
            List of search results
        """
        # Get collection
        collection = self._get_collection(collection_name or "general")
        
        # Search collection
        results = collection.get(
            where=filters,
            limit=k
        )
        
        # Format results
        formatted_results = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"]):
                formatted_results.append({
                    "text": doc,
                    "metadata": results["metadatas"][i] if results["metadatas"] and i < len(results["metadatas"]) else {},
                    "id": results["ids"][i] if results["ids"] and i < len(results["ids"]) else None
                })
        
        return formatted_results
    
    def multi_domain_search(
        self,
        query: str,
        domains: List[str],
        filters: Optional[Dict[str, Any]] = None,
        k_per_domain: int = 5
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across multiple domains.
        
        Args:
            query: Query string
            domains: List of domains to search
            filters: Filters to apply to the search
            k_per_domain: Number of results to return per domain
            
        Returns:
            Dictionary of domain to search results
        """
        results = {}
        
        for domain in domains:
            domain_results = self.search(
                query=query,
                collection_name=domain,
                filters=filters,
                k=k_per_domain
            )
            results[domain] = domain_results
        
        return results
    
    def delete_document(self, doc_id: str, collection_name: Optional[str] = None) -> None:
        """
        Delete a document from a collection.
        
        Args:
            doc_id: Document ID
            collection_name: Name of the collection
        """
        # Get collection
        collection = self._get_collection(collection_name or "general")
        
        # Delete document
        collection.delete(ids=[doc_id])
    
    def update_document(
        self,
        doc_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None
    ) -> None:
        """
        Update a document in a collection.
        
        Args:
            doc_id: Document ID
            text: New text content
            metadata: New metadata
            collection_name: Name of the collection
        """
        # Get collection
        collection = self._get_collection(collection_name or "general")
        
        # Update document
        collection.update(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata or {}]
        )
    
    def get_document(
        self,
        doc_id: str,
        collection_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.
        
        Args:
            doc_id: Document ID
            collection_name: Name of the collection
            
        Returns:
            Document or None if not found
        """
        # Get collection
        collection = self._get_collection(collection_name or "general")
        
        # Get document
        results = collection.get(ids=[doc_id])
        
        # Format result
        if results["documents"] and len(results["documents"]) > 0:
            return {
                "text": results["documents"][0],
                "metadata": results["metadatas"][0] if results["metadatas"] and len(results["metadatas"]) > 0 else {},
                "id": doc_id
            }
        
        return None
    
    def _get_collection(self, collection_name: str):
        """
        Get a collection by name.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection
        """
        if collection_name not in self.collections:
            self.create_collection(collection_name)
        
        return self.collections[collection_name]
    
    def _event_to_document(self, event: Event) -> Tuple[str, str, Dict[str, Any]]:
        """
        Convert an event to a document format.
        
        Args:
            event: Event to convert
            
        Returns:
            Tuple of (document ID, text, metadata)
        """
        # Use event ID as document ID
        doc_id = event.id
        
        # Use event content as text
        text = event.content
        
        # Create metadata
        metadata = {
            "role": event.role,
            "timestamp": event.timestamp,
            "type": "event"
        }
        
        # Add event metadata if available
        if hasattr(event, "metadata") and event.metadata:
            metadata.update(event.metadata)
        
        return doc_id, text, metadata
    
    def export_collection(self, collection_name: str, output_file: str) -> None:
        """
        Export a collection to a JSON file.
        
        Args:
            collection_name: Name of the collection
            output_file: Path to the output file
        """
        # Get collection
        collection = self._get_collection(collection_name)
        
        # Get all documents
        results = collection.get()
        
        # Format results
        formatted_results = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"]):
                formatted_results.append({
                    "text": doc,
                    "metadata": results["metadatas"][i] if results["metadatas"] and i < len(results["metadatas"]) else {},
                    "id": results["ids"][i] if results["ids"] and i < len(results["ids"]) else None
                })
        
        # Write to file
        with open(output_file, "w") as f:
            json.dump(formatted_results, f, indent=2)
    
    def import_collection(self, collection_name: str, input_file: str) -> None:
        """
        Import a collection from a JSON file.
        
        Args:
            collection_name: Name of the collection
            input_file: Path to the input file
        """
        # Read from file
        with open(input_file, "r") as f:
            documents = json.load(f)
        
        # Get collection
        collection = self._get_collection(collection_name)
        
        # Add documents
        for doc in documents:
            collection.add(
                ids=[doc["id"]],
                documents=[doc["text"]],
                metadatas=[doc["metadata"]]
            )
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection statistics
        """
        # Get collection
        collection = self._get_collection(collection_name)
        
        # Get all documents
        results = collection.get()
        
        # Calculate statistics
        stats = {
            "count": len(results["documents"]) if results["documents"] else 0,
            "collection_name": collection_name,
            "metadata": collection.metadata
        }
        
        return stats
    
    def get_all_collections(self) -> List[str]:
        """
        Get all collection names.
        
        Returns:
            List of collection names
        """
        return list(self.collections.keys())
    
    def clear_collection(self, collection_name: str) -> None:
        """
        Clear all documents from a collection.
        
        Args:
            collection_name: Name of the collection
        """
        # Get collection
        collection = self._get_collection(collection_name)
        
        # Get all document IDs
        results = collection.get()
        
        if results["ids"]:
            # Delete all documents
            collection.delete(ids=results["ids"])
    
    def delete_collection(self, collection_name: str) -> None:
        """
        Delete a collection.
        
        Args:
            collection_name: Name of the collection
        """
        # Delete collection
        self.client.delete_collection(collection_name)
        
        # Remove from collections dict
        if collection_name in self.collections:
            del self.collections[collection_name]
