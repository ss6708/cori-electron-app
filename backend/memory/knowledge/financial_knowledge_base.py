"""
Financial knowledge base for Cori RAG++ system.
This module provides a knowledge base for financial domain knowledge.
"""

import os
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime

from ..long_term_memory import LongTermMemory

class FinancialKnowledgeBase:
    """
    Financial knowledge base for storing and retrieving financial domain knowledge.
    """
    
    def __init__(
        self,
        long_term_memory: LongTermMemory,
        knowledge_dir: str = "knowledge"
    ):
        """
        Initialize the financial knowledge base.
        
        Args:
            long_term_memory: Long-term memory for storing knowledge
            knowledge_dir: Directory for storing knowledge files
        """
        self.long_term_memory = long_term_memory
        self.knowledge_dir = knowledge_dir
        
        # Create knowledge directory if it doesn't exist
        os.makedirs(knowledge_dir, exist_ok=True)
        
        # Create domain directories
        self.domains = ["lbo", "ma", "debt", "private_lending", "general"]
        for domain in self.domains:
            domain_dir = os.path.join(knowledge_dir, domain)
            os.makedirs(domain_dir, exist_ok=True)
    
    def add_knowledge(
        self,
        domain: str,
        topic: str,
        title: str,
        content: str,
        source: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add knowledge to the knowledge base.
        
        Args:
            domain: Domain of the knowledge (e.g., lbo, ma, debt, private_lending, general)
            topic: Topic of the knowledge
            title: Title of the knowledge
            content: Content of the knowledge
            source: Source of the knowledge
            metadata: Additional metadata for the knowledge
            
        Returns:
            ID of the added knowledge
        """
        # Validate domain
        if domain not in self.domains:
            domain = "general"
        
        # Create topic directory if it doesn't exist
        topic_dir = os.path.join(self.knowledge_dir, domain, topic)
        os.makedirs(topic_dir, exist_ok=True)
        
        # Create knowledge file
        knowledge_file = os.path.join(topic_dir, f"{title}.json")
        
        # Generate ID
        doc_id = str(uuid.uuid4())
        
        # Create knowledge data
        knowledge_data = {
            "id": doc_id,
            "domain": domain,
            "topic": topic,
            "title": title,
            "content": content,
            "source": source,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": metadata or {}
        }
        
        # Write knowledge to file
        with open(knowledge_file, "w") as f:
            json.dump(knowledge_data, f, indent=2)
        
        # Add knowledge to long-term memory
        doc_metadata = {
            "id": doc_id,
            "domain": domain,
            "topic": topic,
            "title": title,
            "source": source,
            "type": "knowledge",
            **(metadata or {})
        }
        
        self.long_term_memory.add_document(
            collection_name=domain,
            doc_id=doc_id,
            text=content,
            metadata=doc_metadata
        )
        
        return doc_id
    
    def get_knowledge(self, doc_id: str) -> Dict[str, Any]:
        """
        Get knowledge from the knowledge base.
        
        Args:
            doc_id: ID of the knowledge
            
        Returns:
            Knowledge data
        """
        # Get knowledge from long-term memory
        for domain in self.domains:
            try:
                doc = self.long_term_memory.get_document(
                    doc_id=doc_id,
                    collection_name=domain
                )
                
                if doc:
                    return {
                        "id": doc["id"],
                        "domain": doc["metadata"]["domain"],
                        "topic": doc["metadata"]["topic"],
                        "title": doc["metadata"]["title"],
                        "content": doc["text"],
                        "source": doc["metadata"].get("source", ""),
                        "timestamp": doc["metadata"].get("timestamp", datetime.utcnow().isoformat() + "Z"),
                        "metadata": {k: v for k, v in doc["metadata"].items() if k not in ["id", "domain", "topic", "title", "source", "type", "timestamp"]}
                    }
            except:
                continue
        
        return {}
    
    def search_knowledge(
        self,
        query: str,
        domain: Optional[str] = None,
        topic: Optional[str] = None,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for knowledge in the knowledge base.
        
        Args:
            query: Query to search for
            domain: Domain to search in
            topic: Topic to search in
            k: Number of results to return
            
        Returns:
            List of knowledge data
        """
        # Validate domain
        if domain and domain not in self.domains:
            domain = "general"
        
        # Create filters
        filters = {"type": "knowledge"}
        if topic:
            filters["topic"] = topic
        
        # Search in long-term memory
        results = self.long_term_memory.search(
            query=query,
            collection_name=domain or "general",
            filters=filters,
            k=k
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result["id"],
                "domain": result["metadata"]["domain"],
                "topic": result["metadata"]["topic"],
                "title": result["metadata"]["title"],
                "content": result["text"],
                "source": result["metadata"].get("source", ""),
                "timestamp": result["metadata"].get("timestamp", datetime.utcnow().isoformat() + "Z"),
                "metadata": {k: v for k, v in result["metadata"].items() if k not in ["id", "domain", "topic", "title", "source", "type", "timestamp"]},
                "distance": result.get("distance", 0.0)
            })
        
        return formatted_results
    
    def get_knowledge_by_topic(
        self,
        domain: str,
        topic: str
    ) -> List[Dict[str, Any]]:
        """
        Get knowledge by topic.
        
        Args:
            domain: Domain of the knowledge
            topic: Topic of the knowledge
            
        Returns:
            List of knowledge data
        """
        # Validate domain
        if domain not in self.domains:
            domain = "general"
        
        # Create filters
        filters = {"topic": topic, "type": "knowledge"}
        
        # Search in long-term memory
        results = self.long_term_memory.search_by_metadata(
            collection_name=domain,
            filters=filters
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result["id"],
                "domain": result["metadata"]["domain"],
                "topic": result["metadata"]["topic"],
                "title": result["metadata"]["title"],
                "content": result["text"],
                "source": result["metadata"].get("source", ""),
                "timestamp": result["metadata"].get("timestamp", datetime.utcnow().isoformat() + "Z"),
                "metadata": {k: v for k, v in result["metadata"].items() if k not in ["id", "domain", "topic", "title", "source", "type", "timestamp"]}
            })
        
        return formatted_results
    
    def update_knowledge(
        self,
        doc_id: str,
        domain: str,
        topic: str,
        title: str,
        content: str,
        source: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update knowledge in the knowledge base.
        
        Args:
            doc_id: ID of the knowledge
            domain: Domain of the knowledge
            topic: Topic of the knowledge
            title: Title of the knowledge
            content: Content of the knowledge
            source: Source of the knowledge
            metadata: Additional metadata for the knowledge
        """
        # Validate domain
        if domain not in self.domains:
            domain = "general"
        
        # Create topic directory if it doesn't exist
        topic_dir = os.path.join(self.knowledge_dir, domain, topic)
        os.makedirs(topic_dir, exist_ok=True)
        
        # Create knowledge file
        knowledge_file = os.path.join(topic_dir, f"{title}.json")
        
        # Create knowledge data
        knowledge_data = {
            "id": doc_id,
            "domain": domain,
            "topic": topic,
            "title": title,
            "content": content,
            "source": source,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": metadata or {}
        }
        
        # Write knowledge to file
        with open(knowledge_file, "w") as f:
            json.dump(knowledge_data, f, indent=2)
        
        # Update knowledge in long-term memory
        doc_metadata = {
            "id": doc_id,
            "domain": domain,
            "topic": topic,
            "title": title,
            "source": source,
            "type": "knowledge",
            **(metadata or {})
        }
        
        self.long_term_memory.update_document(
            doc_id=doc_id,
            collection_name=domain,
            text=content,
            metadata=doc_metadata
        )
    
    def delete_knowledge(self, doc_id: str) -> None:
        """
        Delete knowledge from the knowledge base.
        
        Args:
            doc_id: ID of the knowledge
        """
        # Get knowledge
        knowledge = self.get_knowledge(doc_id)
        
        if not knowledge:
            return
        
        # Delete knowledge file
        knowledge_file = os.path.join(
            self.knowledge_dir,
            knowledge["domain"],
            knowledge["topic"],
            f"{knowledge['title']}.json"
        )
        
        if os.path.exists(knowledge_file):
            os.remove(knowledge_file)
        
        # Delete knowledge from long-term memory
        self.long_term_memory.delete_document(
            doc_id=doc_id,
            collection_name=knowledge["domain"]
        )
    
    def load_knowledge_from_file(self, file_path: str) -> str:
        """
        Load knowledge from a file.
        
        Args:
            file_path: Path to the knowledge file
            
        Returns:
            ID of the loaded knowledge
        """
        # Read knowledge file
        with open(file_path, "r") as f:
            knowledge_data = json.load(f)
        
        # Add knowledge to knowledge base
        return self.add_knowledge(
            domain=knowledge_data["domain"],
            topic=knowledge_data["topic"],
            title=knowledge_data["title"],
            content=knowledge_data["content"],
            source=knowledge_data.get("source", ""),
            metadata=knowledge_data.get("metadata", {})
        )
    
    def load_knowledge_directory(self, directory: str) -> List[str]:
        """
        Load knowledge from a directory.
        
        Args:
            directory: Path to the knowledge directory
            
        Returns:
            List of IDs of the loaded knowledge
        """
        # Get knowledge files
        knowledge_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".json"):
                    knowledge_files.append(os.path.join(root, file))
        
        # Load knowledge files
        doc_ids = []
        for file in knowledge_files:
            doc_id = self.load_knowledge_from_file(file)
            doc_ids.append(doc_id)
        
        return doc_ids
    
    def get_all_topics(self) -> List[Tuple[str, str]]:
        """
        Get all topics in the knowledge base.
        
        Returns:
            List of (domain, topic) tuples
        """
        topics = []
        for domain in self.domains:
            domain_dir = os.path.join(self.knowledge_dir, domain)
            if os.path.exists(domain_dir):
                for topic in os.listdir(domain_dir):
                    topic_dir = os.path.join(domain_dir, topic)
                    if os.path.isdir(topic_dir):
                        topics.append((domain, topic))
        
        return topics
    
    def get_topics_by_domain(self, domain: str) -> List[str]:
        """
        Get topics by domain.
        
        Args:
            domain: Domain to get topics for
            
        Returns:
            List of topics
        """
        # Validate domain
        if domain not in self.domains:
            domain = "general"
        
        # Get topics
        domain_dir = os.path.join(self.knowledge_dir, domain)
        topics = []
        
        if os.path.exists(domain_dir):
            for topic in os.listdir(domain_dir):
                topic_dir = os.path.join(domain_dir, topic)
                if os.path.isdir(topic_dir):
                    topics.append(topic)
        
        return topics
