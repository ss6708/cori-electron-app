"""
Financial domain condensers for Cori RAG++ system.
This module provides condensers for financial domain knowledge.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from ...models.event import Event
from ..condenser import Condenser

class FinancialDomainCondenser(Condenser):
    """
    Financial domain condenser for condensing financial domain events.
    """
    
    def __init__(
        self,
        max_events: int = 50,
        domain: str = "financial"
    ):
        """
        Initialize the financial domain condenser.
        
        Args:
            max_events: Maximum number of events to keep
            domain: Financial domain
        """
        super().__init__(max_events=max_events)
        self.domain = domain
    
    def condense(self, events: List[Event]) -> List[Event]:
        """
        Condense events.
        
        Args:
            events: Events to condense
            
        Returns:
            Condensed events
        """
        # If there are fewer events than the maximum, return all events
        if len(events) <= self.max_events:
            return events
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda event: event.timestamp)
        
        # Keep the first event
        condensed_events = [sorted_events[0]]
        
        # Keep the most recent events
        condensed_events.extend(sorted_events[-(self.max_events - 1):])
        
        return condensed_events
    
    def condense_by_importance(
        self,
        events: List[Event],
        importance_threshold: float = 0.5
    ) -> List[Event]:
        """
        Condense events by importance.
        
        Args:
            events: Events to condense
            importance_threshold: Importance threshold
            
        Returns:
            Condensed events
        """
        # If there are fewer events than the maximum, return all events
        if len(events) <= self.max_events:
            return events
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda event: event.timestamp)
        
        # Calculate importance for each event
        events_with_importance = []
        for event in sorted_events:
            importance = self._calculate_importance(event)
            events_with_importance.append((event, importance))
        
        # Filter events by importance
        important_events = [
            event for event, importance in events_with_importance
            if importance >= importance_threshold
        ]
        
        # If there are fewer important events than the maximum, add more events
        if len(important_events) < self.max_events:
            # Sort events by importance
            events_with_importance.sort(key=lambda x: x[1], reverse=True)
            
            # Add events until we reach the maximum
            for event, _ in events_with_importance:
                if event not in important_events:
                    important_events.append(event)
                    
                    if len(important_events) >= self.max_events:
                        break
        
        # Sort events by timestamp
        important_events.sort(key=lambda event: event.timestamp)
        
        return important_events
    
    def _calculate_importance(self, event: Event) -> float:
        """
        Calculate importance of an event.
        
        Args:
            event: Event to calculate importance for
            
        Returns:
            Importance score
        """
        # Calculate importance based on role
        role_importance = 0.5
        if event.role == "user":
            role_importance = 0.7
        elif event.role == "system":
            role_importance = 0.9
        
        # Calculate importance based on content length
        content_length = len(event.content)
        length_importance = min(content_length / 1000, 1.0)
        
        # Calculate importance based on financial keywords
        keyword_importance = self._calculate_keyword_importance(event.content)
        
        # Calculate overall importance
        importance = (role_importance + length_importance + keyword_importance) / 3
        
        return importance
    
    def _calculate_keyword_importance(self, content: str) -> float:
        """
        Calculate importance based on financial keywords.
        
        Args:
            content: Content to calculate importance for
            
        Returns:
            Keyword importance score
        """
        # Define financial keywords
        financial_keywords = [
            "lbo", "leveraged buyout", "m&a", "merger", "acquisition",
            "debt", "equity", "capital", "finance", "financial",
            "model", "modeling", "ebitda", "revenue", "profit",
            "balance sheet", "income statement", "cash flow", "dcf",
            "valuation", "multiple", "irr", "moic", "return", "investment"
        ]
        
        # Count keywords in content
        content_lower = content.lower()
        keyword_count = sum(1 for keyword in financial_keywords if keyword in content_lower)
        
        # Calculate importance
        importance = min(keyword_count / 10, 1.0)
        
        return importance


class LBOModelingCondenser(FinancialDomainCondenser):
    """
    LBO modeling condenser for condensing LBO modeling events.
    """
    
    def __init__(
        self,
        max_events: int = 50
    ):
        """
        Initialize the LBO modeling condenser.
        
        Args:
            max_events: Maximum number of events to keep
        """
        super().__init__(max_events=max_events, domain="lbo")
    
    def _calculate_keyword_importance(self, content: str) -> float:
        """
        Calculate importance based on LBO keywords.
        
        Args:
            content: Content to calculate importance for
            
        Returns:
            Keyword importance score
        """
        # Define LBO keywords
        lbo_keywords = [
            "lbo", "leveraged buyout", "debt", "equity", "capital",
            "leverage", "multiple", "ebitda", "cash flow", "dcf",
            "valuation", "irr", "moic", "return", "investment",
            "sponsor", "private equity", "exit", "entry", "transaction"
        ]
        
        # Count keywords in content
        content_lower = content.lower()
        keyword_count = sum(1 for keyword in lbo_keywords if keyword in content_lower)
        
        # Calculate importance
        importance = min(keyword_count / 10, 1.0)
        
        return importance


class MAModelingCondenser(FinancialDomainCondenser):
    """
    M&A modeling condenser for condensing M&A modeling events.
    """
    
    def __init__(
        self,
        max_events: int = 50
    ):
        """
        Initialize the M&A modeling condenser.
        
        Args:
            max_events: Maximum number of events to keep
        """
        super().__init__(max_events=max_events, domain="ma")
    
    def _calculate_keyword_importance(self, content: str) -> float:
        """
        Calculate importance based on M&A keywords.
        
        Args:
            content: Content to calculate importance for
            
        Returns:
            Keyword importance score
        """
        # Define M&A keywords
        ma_keywords = [
            "m&a", "merger", "acquisition", "synergy", "integration",
            "target", "acquirer", "buyer", "seller", "transaction",
            "valuation", "multiple", "premium", "discount", "accretion",
            "dilution", "pro forma", "combined", "standalone", "deal"
        ]
        
        # Count keywords in content
        content_lower = content.lower()
        keyword_count = sum(1 for keyword in ma_keywords if keyword in content_lower)
        
        # Calculate importance
        importance = min(keyword_count / 10, 1.0)
        
        return importance
