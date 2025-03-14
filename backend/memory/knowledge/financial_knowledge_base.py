"""
Financial knowledge base for Cori RAG++ system.
Manages domain-specific financial knowledge for LBO, M&A, Debt Modeling, and Private Lending.
"""

from typing import Dict, List, Optional, Any, Union
import os
import json
import uuid
from datetime import datetime
from pathlib import Path

from ..utils.embedding_model import EmbeddingModel
from ..long_term_memory import LongTermMemory
from ..models.event import Event
from .domain_specific_knowledge import LBOKnowledge, MAKnowledge, DebtKnowledge, PrivateLendingKnowledge

class FinancialKnowledgeBase:
    """
    Manages the financial domain knowledge base for Cori.
    This component extends the long-term memory with specialized
    financial domain knowledge and retrieval mechanisms.
    
    Supports the following financial domains:
    - LBO (Leveraged Buyout)
    - M&A (Mergers & Acquisitions)
    - Debt Modeling
    - Private Lending
    """
    
    def __init__(
        self,
        long_term_memory: LongTermMemory,
        knowledge_dir: str = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the financial knowledge base.
        
        Args:
            long_term_memory: Long-term memory instance
            knowledge_dir: Directory containing financial knowledge files
            api_key: OpenAI API key for knowledge extraction
        """
        self.long_term_memory = long_term_memory
        self.knowledge_dir = knowledge_dir or os.path.join(os.getcwd(), "data", "financial_knowledge")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        # Ensure knowledge directory exists
        os.makedirs(self.knowledge_dir, exist_ok=True)
        
        # Track loaded knowledge
        self.loaded_knowledge = {
            "lbo": False,
            "ma": False,
            "debt": False,
            "private_lending": False
        }
    
    def load_domain_knowledge(self, domain: str) -> int:
        """
        Load domain-specific knowledge from files.
        
        Args:
            domain: Domain to load knowledge for
            
        Returns:
            Number of knowledge items loaded
        """
        if self.loaded_knowledge.get(domain, False):
            return 0  # Already loaded
        
        domain_dir = os.path.join(self.knowledge_dir, domain)
        
        # If domain directory doesn't exist, create it and load default knowledge
        if not os.path.exists(domain_dir):
            os.makedirs(domain_dir, exist_ok=True)
            return self._load_default_knowledge(domain)
        
        # Load knowledge from files
        count = 0
        for file_path in Path(domain_dir).glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    knowledge_items = json.load(f)
                
                for item in knowledge_items:
                    self._add_knowledge_item(item, domain)
                    count += 1
            except Exception as e:
                print(f"Error loading knowledge from {file_path}: {e}")
        
        # If no files found, load default knowledge
        if count == 0:
            count = self._load_default_knowledge(domain)
        
        self.loaded_knowledge[domain] = True
        return count
    
    def _load_default_knowledge(self, domain: str) -> int:
        """
        Load default knowledge for a domain.
        
        Args:
            domain: Domain to load knowledge for
            
        Returns:
            Number of knowledge items loaded
        """
        count = 0
        
        if domain == "lbo":
            count = self._load_default_lbo_knowledge()
        elif domain == "ma":
            count = self._load_default_ma_knowledge()
        elif domain == "debt":
            count = self._load_default_debt_knowledge()
        elif domain == "private_lending":
            count = self._load_default_private_lending_knowledge()
        
        return count
        
    def _load_default_lbo_knowledge(self) -> int:
        """
        Load default LBO knowledge.
        
        Returns:
            Number of knowledge items loaded
        """
        knowledge_items = LBOKnowledge.get_default_knowledge()
        
        count = 0
        for item in knowledge_items:
            self._add_knowledge_item(item, "lbo")
            count += 1
        
        return count
    
    def _load_default_ma_knowledge(self) -> int:
        """
        Load default M&A knowledge.
        
        Returns:
            Number of knowledge items loaded
        """
        knowledge_items = MAKnowledge.get_default_knowledge()
        
        count = 0
        for item in knowledge_items:
            self._add_knowledge_item(item, "ma")
            count += 1
        
        return count
    
    def _load_default_debt_knowledge(self) -> int:
        """
        Load default debt modeling knowledge.
        
        Returns:
            Number of knowledge items loaded
        """
        knowledge_items = DebtKnowledge.get_default_knowledge()
        
        count = 0
        for item in knowledge_items:
            self._add_knowledge_item(item, "debt")
            count += 1
        
        return count
    
    def _load_default_private_lending_knowledge(self) -> int:
        """
        Load default private lending knowledge.
        
        Returns:
            Number of knowledge items loaded
        """
        knowledge_items = PrivateLendingKnowledge.get_default_knowledge()
        
        count = 0
        for item in knowledge_items:
            self._add_knowledge_item(item, "private_lending")
            count += 1
        
        return count
    
    def _add_knowledge_item(self, item: Dict[str, Any], domain: str) -> str:
        """
        Add a knowledge item to the long-term memory.
        
        Args:
            item: Knowledge item
            domain: Domain for the knowledge
            
        Returns:
            Document ID
        """
        # Extract content and metadata
        content = item.get("content", "")
        metadata = item.get("metadata", {})
        
        # Add title to metadata if available
        if "title" in item:
            metadata["title"] = item["title"]
        
        # Add to long-term memory
        doc_id = self.long_term_memory.add_document(
            text=content,
            metadata=metadata,
            domain=domain
        )
        
        return doc_id
    
    def save_domain_knowledge(self, domain: str) -> bool:
        """
        Save domain knowledge to file.
        
        Args:
            domain: Domain to save knowledge for
            
        Returns:
            True if successful, False otherwise
        """
        domain_dir = os.path.join(self.knowledge_dir, domain)
        os.makedirs(domain_dir, exist_ok=True)
        
        # Get all documents for the domain
        documents = self.long_term_memory.get_documents_by_metadata(
            metadata_filters={"type": "financial_knowledge", "domain": domain},
            domain=domain
        )
        
        if not documents:
            return False
        
        # Convert to knowledge items
        knowledge_items = []
        for doc in documents:
            item = {
                "content": doc["text"],
                "metadata": doc["metadata"]
            }
            
            # Add title if available
            if "title" in doc["metadata"]:
                item["title"] = doc["metadata"]["title"]
            
            knowledge_items.append(item)
        
        # Save to file
        file_path = os.path.join(domain_dir, f"{domain}_knowledge.json")
        try:
            with open(file_path, 'w') as f:
                json.dump(knowledge_items, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving knowledge to {file_path}: {e}")
            return False
    
    def add_knowledge_item(
        self,
        title: str,
        content: str,
        domain: str,
        topic: str,
        subtopics: List[str] = None
    ) -> str:
        """
        Add a knowledge item to the knowledge base.
        
        Args:
            title: Knowledge item title
            content: Knowledge item content
            domain: Domain for the knowledge
            topic: Topic for the knowledge
            subtopics: Optional list of subtopics
            
        Returns:
            Document ID
        """
        # Create metadata
        metadata = {
            "type": "financial_knowledge",
            "domain": domain,
            "topic": topic,
            "title": title
        }
        
        # Add subtopics if provided
        if subtopics:
            metadata["subtopics"] = subtopics
        
        # Add to long-term memory
        doc_id = self.long_term_memory.add_document(
            text=content,
            metadata=metadata,
            domain=domain
        )
        
        return doc_id
    
    def search_knowledge(
        self,
        query: str,
        domain: Optional[str] = None,
        topic: Optional[str] = None,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant knowledge.
        
        Args:
            query: The search query
            domain: Optional domain to search in
            topic: Optional topic to filter by
            k: Number of results to return
            
        Returns:
            List of search results
        """
        # Ensure domain knowledge is loaded
        if domain and not self.loaded_knowledge.get(domain, False):
            self.load_domain_knowledge(domain)
        
        # Create filters
        filters = {"type": "financial_knowledge"}
        
        if topic:
            filters["topic"] = topic
        
        # Search for relevant knowledge
        results = self.long_term_memory.search(
            query=query,
            domain=domain,
            filters=filters,
            k=k
        )
        
        return results
    
    def get_knowledge_by_topic(
        self,
        domain: str,
        topic: str
    ) -> List[Dict[str, Any]]:
        """
        Get knowledge items by topic.
        
        Args:
            domain: Domain to search in
            topic: Topic to filter by
            
        Returns:
            List of knowledge items
        """
        # Ensure domain knowledge is loaded
        if not self.loaded_knowledge.get(domain, False):
            self.load_domain_knowledge(domain)
        
        # Get documents by metadata
        documents = self.long_term_memory.get_documents_by_metadata(
            metadata_filters={"type": "financial_knowledge", "domain": domain, "topic": topic},
            domain=domain
        )
        
        return documents
    
    def extract_knowledge_from_events(
        self,
        events: List[Event],
        domain: str
    ) -> Optional[str]:
        """
        Extract knowledge from events and add to knowledge base.
        
        Args:
            events: List of events to extract knowledge from
            domain: Domain for the knowledge
            
        Returns:
            Document ID if knowledge was extracted, None otherwise
        """
        # Ensure we have enough events
        if len(events) < 3:
            return None
        
        # Use OpenAI to extract knowledge
        from openai import OpenAI
        
        client = OpenAI(api_key=self.api_key)
        
        # Convert events to text
        events_text = "\n\n".join([
            f"Role: {event.role}\nContent: {event.content}"
            for event in events
        ])
        
        # Create prompt
        prompt = f"""
        Extract financial knowledge from the following conversation about {domain} modeling:
        
        {events_text}
        
        Please identify key financial concepts, parameters, methodologies, or best practices
        that could be useful for future reference. Format your response as:
        
        Title: [Concise title for this knowledge]
        
        Content: [Detailed explanation of the financial knowledge]
        
        Topic: [Specific topic within {domain}]
        
        Subtopics: [Comma-separated list of relevant subtopics]
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a financial knowledge extraction system."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            extracted_text = response.choices[0].message.content
            
            # Parse the extracted knowledge
            lines = extracted_text.strip().split("\n")
            
            title = ""
            content = ""
            topic = ""
            subtopics = []
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith("Title:"):
                    title = line[6:].strip()
                    current_section = "title"
                elif line.startswith("Content:"):
                    content = line[8:].strip()
                    current_section = "content"
                elif line.startswith("Topic:"):
                    topic = line[6:].strip()
                    current_section = "topic"
                elif line.startswith("Subtopics:"):
                    subtopics_str = line[10:].strip()
                    subtopics = [s.strip() for s in subtopics_str.split(",")]
                    current_section = "subtopics"
                elif current_section == "content":
                    content += "\n" + line
            
            # Validate extracted knowledge
            if not title or not content or not topic:
                return None
            
            # Add to knowledge base
            doc_id = self.add_knowledge_item(
                title=title,
                content=content,
                domain=domain,
                topic=topic,
                subtopics=subtopics
            )
            
            return doc_id
        
        except Exception as e:
            print(f"Error extracting knowledge: {e}")
            return None
    
    def extract_knowledge_from_text(
        self,
        text: str,
        domain: str
    ) -> Optional[str]:
        """
        Extract knowledge from text and add to knowledge base.
        
        Args:
            text: Text to extract knowledge from
            domain: Domain for the knowledge
            
        Returns:
            Document ID if knowledge was extracted, None otherwise
        """
        # Use OpenAI to extract knowledge
        from openai import OpenAI
        
        client = OpenAI(api_key=self.api_key)
        
        # Create prompt
        prompt = f"""
        Extract financial knowledge from the following text about {domain}:
        
        {text}
        
        Please identify key financial concepts, parameters, methodologies, or best practices
        that could be useful for future reference. Format your response as:
        
        Title: [Concise title for this knowledge]
        
        Content: [Detailed explanation of the financial knowledge]
        
        Topic: [Specific topic within {domain}]
        
        Subtopics: [Comma-separated list of relevant subtopics]
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a financial knowledge extraction system."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            extracted_text = response.choices[0].message.content
            
            # Parse the extracted knowledge (same as extract_from_events)
            lines = extracted_text.strip().split("\n")
            
            title = ""
            content = ""
            topic = ""
            subtopics = []
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith("Title:"):
                    title = line[6:].strip()
                    current_section = "title"
                elif line.startswith("Content:"):
                    content = line[8:].strip()
                    current_section = "content"
                elif line.startswith("Topic:"):
                    topic = line[6:].strip()
                    current_section = "topic"
                elif line.startswith("Subtopics:"):
                    subtopics_str = line[10:].strip()
                    subtopics = [s.strip() for s in subtopics_str.split(",")]
                    current_section = "subtopics"
                elif current_section == "content":
                    content += "\n" + line
            
            # Validate extracted knowledge
            if not title or not content or not topic:
                return None
            
            # Add to knowledge base
            doc_id = self.add_knowledge_item(
                title=title,
                content=content,
                domain=domain,
                topic=topic,
                subtopics=subtopics
            )
            
            return doc_id
            
        except Exception as e:
            print(f"Error extracting knowledge: {e}")
            return None
