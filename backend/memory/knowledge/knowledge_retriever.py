"""
Knowledge retrieval utilities for financial domain knowledge.
"""

from typing import Dict, List, Optional, Any, Union
import os
from ..long_term_memory import LongTermMemory
from .financial_knowledge_base import FinancialKnowledgeBase

class KnowledgeRetriever:
    """
    Retrieves and formats financial knowledge for use in RAG contexts.
    """
    
    def __init__(
        self,
        financial_knowledge_base: FinancialKnowledgeBase
    ):
        """
        Initialize the knowledge retriever.
        
        Args:
            financial_knowledge_base: Financial knowledge base instance
        """
        self.financial_knowledge_base = financial_knowledge_base
    
    def retrieve_for_query(
        self,
        query: str,
        domain: Optional[str] = None,
        topic: Optional[str] = None,
        k: int = 5
    ) -> str:
        """
        Retrieve knowledge formatted for inclusion in a prompt.
        
        Args:
            query: The search query
            domain: Optional domain to search in
            topic: Optional topic to filter by
            k: Number of results to return
            
        Returns:
            Formatted knowledge string for inclusion in a prompt
        """
        # Search for relevant knowledge
        results = self.financial_knowledge_base.search_knowledge(
            query=query,
            domain=domain,
            topic=topic,
            k=k
        )
        
        if not results:
            return ""
        
        # Format results
        formatted_knowledge = "RELEVANT FINANCIAL KNOWLEDGE:\n\n"
        
        for i, result in enumerate(results):
            # Extract title from metadata if available
            title = result.get("metadata", {}).get("title", f"Knowledge Item {i+1}")
            
            # Add title and content
            formatted_knowledge += f"[{title}]\n"
            formatted_knowledge += f"{result['text']}\n\n"
        
        return formatted_knowledge
    
    def retrieve_by_topic(
        self,
        domain: str,
        topic: str
    ) -> str:
        """
        Retrieve knowledge by topic formatted for inclusion in a prompt.
        
        Args:
            domain: Domain to search in
            topic: Topic to filter by
            
        Returns:
            Formatted knowledge string for inclusion in a prompt
        """
        # Get knowledge by topic
        results = self.financial_knowledge_base.get_knowledge_by_topic(
            domain=domain,
            topic=topic
        )
        
        if not results:
            return ""
        
        # Format results
        formatted_knowledge = f"FINANCIAL KNOWLEDGE ON {topic.upper()}:\n\n"
        
        for i, result in enumerate(results):
            # Extract title from metadata if available
            title = result.get("metadata", {}).get("title", f"Knowledge Item {i+1}")
            
            # Add title and content
            formatted_knowledge += f"[{title}]\n"
            formatted_knowledge += f"{result['text']}\n\n"
        
        return formatted_knowledge
    
    def retrieve_multi_domain(
        self,
        query: str,
        domains: List[str],
        k_per_domain: int = 2
    ) -> str:
        """
        Retrieve knowledge across multiple domains.
        
        Args:
            query: The search query
            domains: List of domains to search in
            k_per_domain: Number of results to return per domain
            
        Returns:
            Formatted knowledge string for inclusion in a prompt
        """
        formatted_knowledge = "CROSS-DOMAIN FINANCIAL KNOWLEDGE:\n\n"
        
        for domain in domains:
            # Search for relevant knowledge in this domain
            results = self.financial_knowledge_base.search_knowledge(
                query=query,
                domain=domain,
                k=k_per_domain
            )
            
            if not results:
                continue
            
            # Add domain header
            formatted_knowledge += f"[{domain.upper()} DOMAIN]\n"
            
            for result in results:
                # Extract title from metadata if available
                title = result.get("metadata", {}).get("title", "Knowledge Item")
                
                # Add title and content
                formatted_knowledge += f"- {title}:\n"
                
                # Add a condensed version of the content (first 200 chars)
                content = result['text']
                if len(content) > 200:
                    content = content[:200] + "..."
                
                formatted_knowledge += f"  {content}\n\n"
        
        return formatted_knowledge
