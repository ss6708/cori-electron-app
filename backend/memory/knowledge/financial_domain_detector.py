"""
Financial domain detector for Cori RAG++ system.
This module provides a detector for financial domains.
"""

from typing import Dict, Any, List, Optional, Tuple
import os

from openai import OpenAI
from ..models.event import Event

class FinancialDomainDetector:
    """
    Financial domain detector for detecting financial domains.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o"
    ):
        """
        Initialize the financial domain detector.
        
        Args:
            api_key: API key for OpenAI
            model: Model to use for domain detection
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        
        # Define financial domains
        self.domains = ["lbo", "ma", "debt", "private_lending", "general"]
    
    def detect_domain(self, query: str) -> Tuple[str, float]:
        """
        Detect the financial domain of a query.
        
        Args:
            query: Query to detect domain for
            
        Returns:
            Tuple of (domain, confidence)
        """
        try:
            # Create prompt
            prompt = f"""
            Analyze the following query and determine which financial domain it belongs to.
            Return the domain and a confidence score (0-1) in the format: domain,confidence
            
            Available domains:
            - lbo: Leveraged Buyout modeling and analysis
            - ma: Mergers and Acquisitions modeling and analysis
            - debt: Debt modeling and analysis
            - private_lending: Private lending modeling and analysis
            - general: General financial modeling or non-specific domain
            
            Query: {query}
            """
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.1
            )
            
            # Parse response
            result = response.choices[0].message.content.strip()
            parts = result.split(",")
            
            if len(parts) == 2 and parts[0] in self.domains:
                domain = parts[0]
                confidence = float(parts[1])
                return domain, confidence
            
            # Default to general domain with medium confidence
            return "general", 0.5
        
        except Exception as e:
            # Default to general domain with medium confidence
            return "general", 0.5
    
    def detect_domain_from_events(self, events: List[Event]) -> Tuple[str, float]:
        """
        Detect the financial domain from a list of events.
        
        Args:
            events: List of events to detect domain from
            
        Returns:
            Tuple of (domain, confidence)
        """
        try:
            # Create prompt
            prompt = "Analyze the following conversation and determine which financial domain it belongs to.\n"
            prompt += "Return the domain and a confidence score (0-1) in the format: domain,confidence\n\n"
            prompt += "Available domains:\n"
            prompt += "- lbo: Leveraged Buyout modeling and analysis\n"
            prompt += "- ma: Mergers and Acquisitions modeling and analysis\n"
            prompt += "- debt: Debt modeling and analysis\n"
            prompt += "- private_lending: Private lending modeling and analysis\n"
            prompt += "- general: General financial modeling or non-specific domain\n\n"
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
            parts = result.split(",")
            
            if len(parts) == 2 and parts[0] in self.domains:
                domain = parts[0]
                confidence = float(parts[1])
                return domain, confidence
            
            # Default to general domain with medium confidence
            return "general", 0.5
        
        except Exception as e:
            # Default to general domain with medium confidence
            return "general", 0.5
    
    def get_relevant_domains(self, query: str, threshold: float = 0.5) -> List[str]:
        """
        Get relevant domains for a query.
        
        Args:
            query: Query to get relevant domains for
            threshold: Confidence threshold for including a domain
            
        Returns:
            List of relevant domains
        """
        try:
            # Create prompt
            prompt = f"""
            Analyze the following query and determine which financial domains it is relevant to.
            Return each domain and a confidence score (0-1) in the format: domain1,score1\\ndomain2,score2\\n...
            
            Available domains:
            - lbo: Leveraged Buyout modeling and analysis
            - ma: Mergers and Acquisitions modeling and analysis
            - debt: Debt modeling and analysis
            - private_lending: Private lending modeling and analysis
            - general: General financial modeling or non-specific domain
            
            Query: {query}
            """
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.1
            )
            
            # Parse response
            result = response.choices[0].message.content.strip()
            lines = result.split("\n")
            
            relevant_domains = []
            for line in lines:
                parts = line.split(",")
                if len(parts) == 2 and parts[0] in self.domains:
                    domain = parts[0]
                    confidence = float(parts[1])
                    if confidence >= threshold:
                        relevant_domains.append(domain)
            
            # If no domains are relevant, return general
            if not relevant_domains:
                return ["general"]
            
            return relevant_domains
        
        except Exception as e:
            # Default to general domain
            return ["general"]
