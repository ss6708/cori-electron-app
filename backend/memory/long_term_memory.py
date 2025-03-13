from typing import Dict, List, Optional, Any, Tuple
import uuid
import os
import json
from datetime import datetime

import chromadb
from chromadb.config import Settings

from .models.event import Event

class LongTermMemory:
    """
    Handles storing and retrieving information using ChromaDB.
    This is the third tier of the three-tier memory architecture.
    """
    
    def __init__(
        self,
        db_path: str,
        embedding_model,
        session_id: str,
        user_id: str
    ):
        """
        Initialize long-term memory.
        
        Args:
            db_path: Path to the ChromaDB database
            embedding_model: Model for generating embeddings
            session_id: Unique identifier for the session
            user_id: Identifier for the user
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create collections for each domain
        self.collections = {
            "lbo": self.client.get_or_create_collection("lbo"),
            "ma": self.client.get_or_create_collection("ma"),
            "debt": self.client.get_or_create_collection("debt"),
            "private_lending": self.client.get_or_create_collection("private_lending"),
            "general": self.client.get_or_create_collection("general")
        }
        
        self.embedding_model = embedding_model
        self.session_id = session_id
        self.user_id = user_id
        self.document_count = 0
    
    def add_event(self, event: Event) -> None:
        """
        Add an event to the appropriate collection.
        
        Args:
            event: The event to add
        """
        # Convert event to document format
        doc_id, text, metadata = self._event_to_document(event)
        
        # Determine which collection to use
        domain = getattr(event, "domain", "general") if hasattr(event, "domain") else "general"
        collection = self.collections.get(domain, self.collections["general"])
        
        # Generate embedding and add to collection
        embedding = self.embedding_model.embed_text(text)
        collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[text]
        )
        
        self.document_count += 1
    
    def _event_to_document(self, event: Event) -> Tuple[str, str, Dict[str, Any]]:
        """
        Convert an event to document format for vector storage.
        
        Args:
            event: The event to convert
            
        Returns:
            Tuple of (document_id, text, metadata)
        """
        # Use event ID as document ID
        doc_id = event.id
        
        # Convert event to text
        if hasattr(event, "to_document") and callable(event.to_document):
            doc = event.to_document()
            text = json.dumps(doc)
        else:
            doc = event.to_dict()
            text = json.dumps(doc)
        
        # Extract metadata
        metadata = {
            "timestamp": event.timestamp.isoformat(),
            "user_id": event.user_id,
            "session_id": event.session_id,
            "event_type": event.__class__.__name__
        }
        
        # Add domain if available
        if hasattr(event, "domain"):
            metadata["domain"] = getattr(event, "domain")
        
        # Add action_type if available
        if hasattr(event, "action_type"):
            metadata["action_type"] = getattr(event, "action_type")
        
        return doc_id, text, metadata
    
    def search(
        self, 
        query: str, 
        domain: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents.
        
        Args:
            query: The search query
            domain: Optional domain to search in
            filters: Optional metadata filters
            k: Number of results to return
            
        Returns:
            List of search results
        """
        # Determine which collection to search
        collection = self.collections.get(domain, None) if domain else None
        
        # If no specific domain, search all collections
        if collection is None:
            results = []
            for domain_name, coll in self.collections.items():
                domain_results = self._search_collection(
                    collection=coll,
                    query=query,
                    filters=filters,
                    k=k
                )
                for result in domain_results:
                    result["domain"] = domain_name
                results.extend(domain_results)
            
            # Sort by distance and take top k
            results.sort(key=lambda x: x["distance"])
            return results[:k]
        else:
            # Search specific collection
            return self._search_collection(
                collection=collection,
                query=query,
                filters=filters,
                k=k
            )
    
    def _search_collection(
        self,
        collection,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search a specific collection.
        
        Args:
            collection: The collection to search
            query: The search query
            filters: Optional metadata filters
            k: Number of results to return
            
        Returns:
            List of search results
        """
        # Generate query embedding
        query_embedding = self.embedding_model.embed_text(query)
        
        # Perform search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filters
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })
        
        return formatted_results
    
    def add_document(
        self,
        text: str,
        metadata: Dict[str, Any],
        domain: str = "general",
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add a document to the appropriate collection.
        
        Args:
            text: The document text
            metadata: Document metadata
            domain: The domain for the document
            doc_id: Optional document ID
            
        Returns:
            Document ID
        """
        # Generate document ID if not provided
        if doc_id is None:
            doc_id = str(uuid.uuid4())
        
        # Determine which collection to use
        collection = self.collections.get(domain, self.collections["general"])
        
        # Generate embedding and add to collection
        embedding = self.embedding_model.embed_text(text)
        collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[text]
        )
        
        self.document_count += 1
        return doc_id
    
    def delete_document(self, doc_id: str, domain: Optional[str] = None) -> bool:
        """
        Delete a document from the appropriate collection.
        
        Args:
            doc_id: The document ID
            domain: Optional domain to delete from
            
        Returns:
            True if document was deleted, False otherwise
        """
        if domain:
            # Delete from specific collection
            collection = self.collections.get(domain)
            if collection:
                collection.delete(ids=[doc_id])
                return True
        else:
            # Try to delete from all collections
            for collection in self.collections.values():
                try:
                    collection.delete(ids=[doc_id])
                    return True
                except:
                    pass
        
        return False
    
    def get_document(self, doc_id: str, domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.
        
        Args:
            doc_id: The document ID
            domain: Optional domain to get from
            
        Returns:
            Document if found, None otherwise
        """
        if domain:
            # Get from specific collection
            collection = self.collections.get(domain)
            if collection:
                try:
                    result = collection.get(ids=[doc_id])
                    if result["ids"]:
                        return {
                            "id": result["ids"][0],
                            "text": result["documents"][0],
                            "metadata": result["metadatas"][0]
                        }
                except:
                    pass
        else:
            # Try to get from all collections
            for domain_name, collection in self.collections.items():
                try:
                    result = collection.get(ids=[doc_id])
                    if result["ids"]:
                        return {
                            "id": result["ids"][0],
                            "text": result["documents"][0],
                            "metadata": result["metadatas"][0],
                            "domain": domain_name
                        }
                except:
                    pass
        
        return None
    
    def get_documents_by_metadata(
        self,
        metadata_filters: Dict[str, Any],
        domain: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get documents by metadata filters.
        
        Args:
            metadata_filters: Metadata filters
            domain: Optional domain to get from
            
        Returns:
            List of documents
        """
        if domain:
            # Get from specific collection
            collection = self.collections.get(domain)
            if collection:
                try:
                    result = collection.get(where=metadata_filters)
                    return self._format_get_results(result, domain)
                except:
                    return []
        else:
            # Get from all collections
            results = []
            for domain_name, collection in self.collections.items():
                try:
                    result = collection.get(where=metadata_filters)
                    results.extend(self._format_get_results(result, domain_name))
                except:
                    pass
            
            return results
    
    def _format_get_results(self, result, domain: str) -> List[Dict[str, Any]]:
        """
        Format get results.
        
        Args:
            result: ChromaDB get result
            domain: Domain name
            
        Returns:
            Formatted results
        """
        formatted_results = []
        for i in range(len(result["ids"])):
            formatted_results.append({
                "id": result["ids"][i],
                "text": result["documents"][i],
                "metadata": result["metadatas"][i],
                "domain": domain
            })
        
        return formatted_results
