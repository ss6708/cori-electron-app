"""
Knowledge retriever for Cori RAG++ system.
This module provides a retriever for financial domain knowledge.
"""

from typing import Dict, Any, List, Optional, Tuple
import math

from .financial_knowledge_base import FinancialKnowledgeBase

class KnowledgeRetriever:
    """
    Knowledge retriever for retrieving financial domain knowledge.
    """
    
    def __init__(
        self,
        financial_knowledge_base: FinancialKnowledgeBase
    ):
        """
        Initialize the knowledge retriever.
        
        Args:
            financial_knowledge_base: Financial knowledge base
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
        Retrieve knowledge for a query.
        
        Args:
            query: Query to retrieve knowledge for
            domain: Domain to retrieve knowledge from
            topic: Topic to retrieve knowledge from
            k: Number of results to return
            
        Returns:
            Retrieved knowledge as a formatted string
        """
        # Search for knowledge
        results = self.financial_knowledge_base.search_knowledge(
            query=query,
            domain=domain,
            topic=topic,
            k=k
        )
        
        # Format results
        if not results:
            return "NO RELEVANT FINANCIAL KNOWLEDGE FOUND"
        
        formatted_results = "RELEVANT FINANCIAL KNOWLEDGE:\n\n"
        for result in results:
            formatted_results += self._format_knowledge_item(result)
            formatted_results += "\n\n"
        
        return formatted_results
    
    def retrieve_by_topic(
        self,
        domain: str,
        topic: str
    ) -> str:
        """
        Retrieve knowledge by topic.
        
        Args:
            domain: Domain to retrieve knowledge from
            topic: Topic to retrieve knowledge from
            
        Returns:
            Retrieved knowledge as a formatted string
        """
        # Get knowledge by topic
        results = self.financial_knowledge_base.get_knowledge_by_topic(
            domain=domain,
            topic=topic
        )
        
        # Format results
        if not results:
            return f"NO KNOWLEDGE FOUND FOR TOPIC: {topic}"
        
        formatted_results = f"FINANCIAL KNOWLEDGE ON {topic.upper()}:\n\n"
        for result in results:
            formatted_results += f"[{result['title']}]\n"
            formatted_results += f"{result['content']}\n\n"
        
        return formatted_results
    
    def retrieve_multi_domain(
        self,
        query: str,
        domains: List[str],
        k_per_domain: int = 3
    ) -> str:
        """
        Retrieve knowledge across multiple domains.
        
        Args:
            query: Query to retrieve knowledge for
            domains: Domains to retrieve knowledge from
            k_per_domain: Number of results to return per domain
            
        Returns:
            Retrieved knowledge as a formatted string
        """
        all_results = {}
        
        # Search for knowledge in each domain
        for domain in domains:
            results = self.financial_knowledge_base.search_knowledge(
                query=query,
                domain=domain,
                k=k_per_domain
            )
            
            all_results[domain] = results
        
        # Check if any results were found
        total_results = sum(len(results) for results in all_results.values())
        if total_results == 0:
            return "NO RELEVANT FINANCIAL KNOWLEDGE FOUND ACROSS DOMAINS"
        
        # Format results
        formatted_results = "CROSS-DOMAIN FINANCIAL KNOWLEDGE:\n\n"
        for domain, results in all_results.items():
            formatted_results += f"[{domain.upper()} DOMAIN]\n"
            
            if not results:
                formatted_results += f"No relevant knowledge found for {domain.upper()} domain\n\n"
                continue
            
            for result in results:
                formatted_results += f"- {result['title']}:\n"
                formatted_results += f"  {result['content'][:200]}...\n\n"
        
        return formatted_results
    
    def _format_knowledge_item(self, knowledge_item: Dict[str, Any]) -> str:
        """
        Format a knowledge item.
        
        Args:
            knowledge_item: Knowledge item to format
            
        Returns:
            Formatted knowledge item
        """
        formatted_item = f"[{knowledge_item['title']}]\n"
        
        # Add relevance score if available
        if "distance" in knowledge_item:
            relevance = int((1 - knowledge_item["distance"]) * 100)
            formatted_item += f"(Relevance: {relevance}%)\n"
        
        formatted_item += f"{knowledge_item['content']}"
        
        return formatted_item
