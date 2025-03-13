"""
Knowledge extraction utilities for financial domain knowledge.
"""

from typing import Dict, List, Optional, Any, Union
import os
from openai import OpenAI
from ..models.event import Event

class KnowledgeExtractor:
    """
    Extracts financial knowledge from conversations and events.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the knowledge extractor.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def extract_from_events(
        self,
        events: List[Event],
        domain: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract knowledge from events.
        
        Args:
            events: List of events to extract knowledge from
            domain: Domain for the knowledge
            
        Returns:
            Extracted knowledge item or None if extraction failed
        """
        # Ensure we have enough events
        if len(events) < 3:
            return None
        
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
            response = self.client.chat.completions.create(
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
            
            # Create knowledge item
            knowledge_item = {
                "title": title,
                "content": content,
                "metadata": {
                    "type": "financial_knowledge",
                    "domain": domain,
                    "topic": topic,
                    "subtopics": subtopics,
                    "source": "conversation",
                    "extracted": True
                }
            }
            
            return knowledge_item
            
        except Exception as e:
            print(f"Error extracting knowledge: {e}")
            return None
    
    def extract_from_text(
        self,
        text: str,
        domain: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract knowledge from text.
        
        Args:
            text: Text to extract knowledge from
            domain: Domain for the knowledge
            
        Returns:
            Extracted knowledge item or None if extraction failed
        """
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
            response = self.client.chat.completions.create(
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
            
            # Create knowledge item
            knowledge_item = {
                "title": title,
                "content": content,
                "metadata": {
                    "type": "financial_knowledge",
                    "domain": domain,
                    "topic": topic,
                    "subtopics": subtopics,
                    "source": "text",
                    "extracted": True
                }
            }
            
            return knowledge_item
            
        except Exception as e:
            print(f"Error extracting knowledge: {e}")
            return None
