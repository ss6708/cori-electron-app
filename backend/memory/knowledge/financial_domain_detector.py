"""
Financial domain detector for Cori RAG++ system.
Detects the financial domain of a query or conversation.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
import os
from openai import OpenAI
from ..models.event import Event

class FinancialDomainDetector:
    """
    Detects the financial domain of a query or conversation.
    Used to route queries to the appropriate domain-specific knowledge.
    """
    
    DOMAINS = ["lbo", "ma", "debt", "private_lending", "general"]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the financial domain detector.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def detect_domain(self, query: str) -> Tuple[str, float]:
        """
        Detect the financial domain of a query.
        
        Args:
            query: The query to detect the domain for
            
        Returns:
            Tuple of (domain, confidence)
        """
        prompt = f"""
        Determine which financial domain the following query is most related to.
        
        Query: {query}
        
        Choose from the following domains:
        - LBO (Leveraged Buyout): Acquisition of a company using significant debt
        - M&A (Mergers & Acquisitions): Combining or acquiring companies
        - Debt Modeling: Analyzing and structuring debt instruments
        - Private Lending: Direct lending to companies outside public markets
        - General: General financial topics not specific to the above
        
        Respond with only the domain name in lowercase (lbo, ma, debt, private_lending, or general)
        followed by a confidence score between 0 and 1, separated by a comma.
        For example: "lbo,0.85" or "general,0.6"
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a financial domain classification system."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse the result
            parts = result.split(",")
            if len(parts) != 2:
                return "general", 0.5
            
            domain = parts[0].strip().lower()
            try:
                confidence = float(parts[1].strip())
            except ValueError:
                confidence = 0.5
            
            # Validate domain
            if domain not in self.DOMAINS:
                return "general", 0.5
            
            return domain, confidence
            
        except Exception as e:
            print(f"Error detecting domain: {e}")
            return "general", 0.5
    
    def detect_domain_from_events(self, events: List[Event]) -> Tuple[str, float]:
        """
        Detect the financial domain from a list of events.
        
        Args:
            events: List of events to detect the domain from
            
        Returns:
            Tuple of (domain, confidence)
        """
        # Convert events to text
        events_text = "\n\n".join([
            f"Role: {event.role}\nContent: {event.content}"
            for event in events[-5:]  # Use last 5 events for efficiency
        ])
        
        prompt = f"""
        Determine which financial domain the following conversation is most related to.
        
        Conversation:
        {events_text}
        
        Choose from the following domains:
        - LBO (Leveraged Buyout): Acquisition of a company using significant debt
        - M&A (Mergers & Acquisitions): Combining or acquiring companies
        - Debt Modeling: Analyzing and structuring debt instruments
        - Private Lending: Direct lending to companies outside public markets
        - General: General financial topics not specific to the above
        
        Respond with only the domain name in lowercase (lbo, ma, debt, private_lending, or general)
        followed by a confidence score between 0 and 1, separated by a comma.
        For example: "lbo,0.85" or "general,0.6"
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a financial domain classification system."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse the result
            parts = result.split(",")
            if len(parts) != 2:
                return "general", 0.5
            
            domain = parts[0].strip().lower()
            try:
                confidence = float(parts[1].strip())
            except ValueError:
                confidence = 0.5
            
            # Validate domain
            if domain not in self.DOMAINS:
                return "general", 0.5
            
            return domain, confidence
            
        except Exception as e:
            print(f"Error detecting domain from events: {e}")
            return "general", 0.5
    
    def get_relevant_domains(self, query: str, threshold: float = 0.6) -> List[str]:
        """
        Get all relevant domains for a query above a confidence threshold.
        
        Args:
            query: The query to detect domains for
            threshold: Confidence threshold for including a domain
            
        Returns:
            List of relevant domains
        """
        prompt = f"""
        Determine which financial domains the following query is related to.
        
        Query: {query}
        
        For each domain, provide a confidence score between 0 and 1:
        - LBO (Leveraged Buyout): Acquisition of a company using significant debt
        - M&A (Mergers & Acquisitions): Combining or acquiring companies
        - Debt Modeling: Analyzing and structuring debt instruments
        - Private Lending: Direct lending to companies outside public markets
        - General: General financial topics not specific to the above
        
        Respond with only the domain names and scores in the format:
        lbo,0.85
        ma,0.45
        debt,0.2
        private_lending,0.1
        general,0.3
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a financial domain classification system."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse the result
            relevant_domains = []
            for line in result.split("\n"):
                parts = line.split(",")
                if len(parts) != 2:
                    continue
                
                domain = parts[0].strip().lower()
                try:
                    confidence = float(parts[1].strip())
                except ValueError:
                    continue
                
                # Validate domain
                if domain not in self.DOMAINS:
                    continue
                
                # Check threshold
                if confidence >= threshold:
                    relevant_domains.append(domain)
            
            # Always include general if no domains meet threshold
            if not relevant_domains:
                relevant_domains.append("general")
            
            return relevant_domains
            
        except Exception as e:
            print(f"Error getting relevant domains: {e}")
            return ["general"]
