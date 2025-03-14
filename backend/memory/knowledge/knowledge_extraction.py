"""
Knowledge extraction for Cori RAG++ system.
This module provides extractors for financial domain knowledge.
"""

import os
from typing import Dict, Any, List, Optional, Tuple
import json

from openai import OpenAI
from ..models.event import Event

class KnowledgeExtractor:
    """
    Knowledge extractor for extracting financial domain knowledge.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o"
    ):
        """
        Initialize the knowledge extractor.
        
        Args:
            api_key: API key for OpenAI
            model: Model to use for knowledge extraction
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
    
    def extract_knowledge_from_text(
        self,
        text: str,
        domain: str,
        topic: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract knowledge from text.
        
        Args:
            text: Text to extract knowledge from
            domain: Domain of the knowledge
            topic: Topic of the knowledge
            
        Returns:
            List of extracted knowledge items
        """
        try:
            # Create prompt
            prompt = f"""
            Extract financial knowledge from the following text.
            Return a JSON array of knowledge items, where each item has the following structure:
            {{
                "title": "Title of the knowledge item",
                "content": "Content of the knowledge item",
                "domain": "{domain}",
                "topic": "Topic of the knowledge item",
                "source": "Source of the knowledge item"
            }}
            
            Text: {text}
            """
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.1
            )
            
            # Parse response
            result = response.choices[0].message.content.strip()
            knowledge_items = json.loads(result)
            
            # Set topic if provided
            if topic:
                for item in knowledge_items:
                    item["topic"] = topic
            
            return knowledge_items
        
        except Exception as e:
            # Return empty list on error
            return []
    
    def extract_knowledge_from_events(
        self,
        events: List[Event],
        domain: str,
        topic: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract knowledge from events.
        
        Args:
            events: Events to extract knowledge from
            domain: Domain of the knowledge
            topic: Topic of the knowledge
            
        Returns:
            List of extracted knowledge items
        """
        try:
            # Create prompt
            prompt = "Extract financial knowledge from the following conversation.\n"
            prompt += "Return a JSON array of knowledge items, where each item has the following structure:\n"
            prompt += "{\n"
            prompt += f'    "title": "Title of the knowledge item",\n'
            prompt += '    "content": "Content of the knowledge item",\n'
            prompt += f'    "domain": "{domain}",\n'
            prompt += '    "topic": "Topic of the knowledge item",\n'
            prompt += '    "source": "Conversation"\n'
            prompt += "}\n\n"
            prompt += "Conversation:\n"
            
            for event in events:
                role = "User" if event.role == "user" else "Assistant"
                prompt += f"{role}: {event.content}\n"
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.1
            )
            
            # Parse response
            result = response.choices[0].message.content.strip()
            knowledge_items = json.loads(result)
            
            # Set topic if provided
            if topic:
                for item in knowledge_items:
                    item["topic"] = topic
            
            return knowledge_items
        
        except Exception as e:
            # Return empty list on error
            return []
    
    def extract_knowledge_from_document(
        self,
        document_path: str,
        domain: str,
        topic: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract knowledge from a document.
        
        Args:
            document_path: Path to the document
            domain: Domain of the knowledge
            topic: Topic of the knowledge
            
        Returns:
            List of extracted knowledge items
        """
        try:
            # Read document
            with open(document_path, "r") as f:
                text = f.read()
            
            # Extract knowledge from text
            knowledge_items = self.extract_knowledge_from_text(
                text=text,
                domain=domain,
                topic=topic
            )
            
            # Set source to document path
            for item in knowledge_items:
                item["source"] = document_path
            
            return knowledge_items
        
        except Exception as e:
            # Return empty list on error
            return []
    
    def extract_structured_knowledge(
        self,
        text: str,
        schema: Dict[str, Any],
        domain: str,
        topic: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract structured knowledge from text.
        
        Args:
            text: Text to extract knowledge from
            schema: Schema for the structured knowledge
            domain: Domain of the knowledge
            topic: Topic of the knowledge
            
        Returns:
            List of extracted knowledge items
        """
        try:
            # Create prompt
            prompt = f"""
            Extract structured financial knowledge from the following text.
            Return a JSON array of knowledge items, where each item follows this schema:
            {json.dumps(schema, indent=2)}
            
            Additionally, each item should have the following fields:
            {{
                "title": "Title of the knowledge item",
                "content": "Content of the knowledge item",
                "domain": "{domain}",
                "topic": "Topic of the knowledge item",
                "source": "Source of the knowledge item"
            }}
            
            Text: {text}
            """
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.1
            )
            
            # Parse response
            result = response.choices[0].message.content.strip()
            knowledge_items = json.loads(result)
            
            # Set topic if provided
            if topic:
                for item in knowledge_items:
                    item["topic"] = topic
            
            return knowledge_items
        
        except Exception as e:
            # Return empty list on error
            return []
