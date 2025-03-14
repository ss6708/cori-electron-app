"""
LLM-based attention condenser for Cori RAG++ system.
Uses OpenAI's GPT-4o to identify and preserve the most important events.
"""

from typing import Dict, List, Optional, Any, Union
import os
import json
from openai import OpenAI
from ...models.event import Event
from ..condenser import RollingCondenser

class LLMAttentionCondenser(RollingCondenser):
    """
    A condenser that uses an LLM to identify and preserve the most important events.
    This is particularly useful for preserving critical context while reducing the
    overall number of events.
    """
    
    def __init__(
        self,
        max_size: int = 100,
        keep_first: int = 1,
        keep_last: int = 10,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        attention_prompt_template: Optional[str] = None,
        max_tokens_per_batch: int = 8000,
        importance_threshold: float = 0.7
    ):
        """
        Initialize the LLM attention condenser.
        
        Args:
            max_size: Maximum number of events to keep
            keep_first: Number of initial events to always keep
            keep_last: Number of recent events to always keep
            api_key: OpenAI API key (defaults to environment variable)
            model: OpenAI model to use
            attention_prompt_template: Optional custom prompt template for attention scoring
            max_tokens_per_batch: Maximum tokens per batch for attention scoring
            importance_threshold: Threshold for determining important events
        """
        super().__init__(max_size, keep_first, keep_last)
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.attention_prompt_template = attention_prompt_template or self._default_attention_prompt()
        self.max_tokens_per_batch = max_tokens_per_batch
        self.importance_threshold = importance_threshold
    
    def _default_attention_prompt(self) -> str:
        """
        Get the default attention prompt template.
        
        Returns:
            Default attention prompt template
        """
        return """
        You are an expert financial analyst assistant tasked with identifying the most important events in a conversation about financial modeling.
        Your goal is to score each event based on its importance for understanding the financial context.
        
        Here are the events to score:
        
        {events}
        
        For each event, assign an importance score between 0 and 1, where:
        - 0: Not important at all, can be safely removed
        - 0.5: Moderately important, provides some context
        - 1: Critically important, contains key financial information
        
        Format your response as a JSON array with the following structure:
        [
            {
                "event_id": "id1",
                "importance": 0.8,
                "reason": "Brief explanation of why this event is important"
            },
            {
                "event_id": "id2",
                "importance": 0.3,
                "reason": "Brief explanation of why this event is less important"
            },
            ...
        ]
        
        Focus on events that contain:
        1. Key financial parameters and assumptions
        2. Important financial metrics and ratios
        3. Transaction structures and terms
        4. Valuation methodologies and multiples
        5. Debt and equity components
        6. Cash flow projections and sensitivities
        """
    
    def _events_to_json(self, events: List[Event]) -> str:
        """
        Convert events to a JSON string for the attention prompt.
        
        Args:
            events: List of events to convert
            
        Returns:
            JSON string of events
        """
        events_json = []
        for i, event in enumerate(events):
            events_json.append({
                "event_id": event.id,
                "index": i,
                "role": event.role,
                "content": event.content
            })
        return json.dumps(events_json, indent=2)
    
    def _score_events(self, events: List[Event]) -> List[Dict[str, Any]]:
        """
        Score events using the LLM.
        
        Args:
            events: List of events to score
            
        Returns:
            List of event scores
        """
        events_json = self._events_to_json(events)
        prompt = self.attention_prompt_template.format(events=events_json)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial attention scoring assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            scores_text = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                scores = json.loads(scores_text)
                return scores
            except json.JSONDecodeError:
                print(f"Error parsing scores: {scores_text}")
                # If not valid JSON, return empty scores
                return []
            
        except Exception as e:
            print(f"Error scoring events: {e}")
            return []
    
    def _condense_middle(self, events: List[Event]) -> List[Event]:
        """
        Condense the middle section by keeping the most important events.
        
        Args:
            events: List of events to condense
            
        Returns:
            Condensed list of events
        """
        if not events:
            return []
        
        # If we have very few events, don't condense
        if len(events) <= 3:
            return events
        
        # Score the events
        scores = self._score_events(events)
        
        # Create a mapping of event IDs to scores
        score_map = {score["event_id"]: score["importance"] for score in scores}
        
        # Identify important events
        important_events = []
        for event in events:
            importance = score_map.get(event.id, 0.0)
            if importance >= self.importance_threshold:
                important_events.append(event)
        
        # Calculate how many events to keep from the middle section
        middle_size = self.max_size - self.keep_first - self.keep_last
        
        # If we have fewer important events than the middle size, return all important events
        if len(important_events) <= middle_size:
            return important_events
        
        # Otherwise, prioritize the most important events
        # Sort by importance score (descending)
        important_events_with_scores = [(event, score_map.get(event.id, 0.0)) for event in important_events]
        important_events_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Take the top events
        top_events = [event for event, _ in important_events_with_scores[:middle_size]]
        
        # Sort back by original order
        event_indices = {event.id: i for i, event in enumerate(events)}
        top_events.sort(key=lambda event: event_indices.get(event.id, 0))
        
        return top_events


class FinancialLLMAttentionCondenser(LLMAttentionCondenser):
    """
    A specialized LLM attention condenser for financial modeling contexts.
    Uses a domain-specific prompt template to identify important financial events.
    """
    
    def __init__(
        self,
        domain: str = "general",
        max_size: int = 100,
        keep_first: int = 1,
        keep_last: int = 10,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        max_tokens_per_batch: int = 8000,
        importance_threshold: float = 0.7
    ):
        """
        Initialize the financial LLM attention condenser.
        
        Args:
            domain: Financial domain (lbo, ma, debt, private_lending, general)
            max_size: Maximum number of events to keep
            keep_first: Number of initial events to always keep
            keep_last: Number of recent events to always keep
            api_key: OpenAI API key (defaults to environment variable)
            model: OpenAI model to use
            max_tokens_per_batch: Maximum tokens per batch for attention scoring
            importance_threshold: Threshold for determining important events
        """
        self.domain = domain
        attention_prompt_template = self._get_domain_specific_prompt(domain)
        
        super().__init__(
            max_size=max_size,
            keep_first=keep_first,
            keep_last=keep_last,
            api_key=api_key,
            model=model,
            attention_prompt_template=attention_prompt_template,
            max_tokens_per_batch=max_tokens_per_batch,
            importance_threshold=importance_threshold
        )
    
    def _get_domain_specific_prompt(self, domain: str) -> str:
        """
        Get a domain-specific prompt template.
        
        Args:
            domain: Financial domain
            
        Returns:
            Domain-specific prompt template
        """
        if domain == "lbo":
            return """
            You are an expert LBO modeling analyst tasked with identifying the most important events in a conversation about leveraged buyout modeling.
            Your goal is to score each event based on its importance for understanding the LBO context.
            
            Here are the events to score:
            
            {events}
            
            For each event, assign an importance score between 0 and 1, where:
            - 0: Not important at all, can be safely removed
            - 0.5: Moderately important, provides some context
            - 1: Critically important, contains key LBO information
            
            Format your response as a JSON array with the following structure:
            [
                {
                    "event_id": "id1",
                    "importance": 0.8,
                    "reason": "Brief explanation of why this event is important"
                },
                {
                    "event_id": "id2",
                    "importance": 0.3,
                    "reason": "Brief explanation of why this event is less important"
                },
                ...
            ]
            
            Focus on events that contain:
            1. Transaction structure and purchase price
            2. Debt and equity components
            3. Leverage ratios and debt tranches
            4. EBITDA multiples (entry and exit)
            5. Financial projections and assumptions
            6. Returns (IRR, MOIC)
            7. Debt paydown and refinancing
            8. Covenants and terms
            """
        elif domain == "ma":
            return """
            You are an expert M&A analyst tasked with identifying the most important events in a conversation about mergers and acquisitions modeling.
            Your goal is to score each event based on its importance for understanding the M&A context.
            
            Here are the events to score:
            
            {events}
            
            For each event, assign an importance score between 0 and 1, where:
            - 0: Not important at all, can be safely removed
            - 0.5: Moderately important, provides some context
            - 1: Critically important, contains key M&A information
            
            Format your response as a JSON array with the following structure:
            [
                {
                    "event_id": "id1",
                    "importance": 0.8,
                    "reason": "Brief explanation of why this event is important"
                },
                {
                    "event_id": "id2",
                    "importance": 0.3,
                    "reason": "Brief explanation of why this event is less important"
                },
                ...
            ]
            
            Focus on events that contain:
            1. Transaction structure and purchase price
            2. Valuation multiples and methodologies
            3. Synergies (cost and revenue)
            4. Pro forma financials
            5. Accretion/dilution analysis
            6. Financing structure
            7. Deal terms and conditions
            8. Integration considerations
            """
        elif domain == "debt":
            return """
            You are an expert debt modeling analyst tasked with identifying the most important events in a conversation about debt modeling.
            Your goal is to score each event based on its importance for understanding the debt modeling context.
            
            Here are the events to score:
            
            {events}
            
            For each event, assign an importance score between 0 and 1, where:
            - 0: Not important at all, can be safely removed
            - 0.5: Moderately important, provides some context
            - 1: Critically important, contains key debt information
            
            Format your response as a JSON array with the following structure:
            [
                {
                    "event_id": "id1",
                    "importance": 0.8,
                    "reason": "Brief explanation of why this event is important"
                },
                {
                    "event_id": "id2",
                    "importance": 0.3,
                    "reason": "Brief explanation of why this event is less important"
                },
                ...
            ]
            
            Focus on events that contain:
            1. Debt structure and tranches
            2. Interest rates and terms
            3. Amortization schedules
            4. Covenants and conditions
            5. Refinancing considerations
            6. Credit metrics and ratios
            7. Cash flow available for debt service
            8. Default scenarios and sensitivities
            """
        elif domain == "private_lending":
            return """
            You are an expert private lending analyst tasked with identifying the most important events in a conversation about private lending.
            Your goal is to score each event based on its importance for understanding the private lending context.
            
            Here are the events to score:
            
            {events}
            
            For each event, assign an importance score between 0 and 1, where:
            - 0: Not important at all, can be safely removed
            - 0.5: Moderately important, provides some context
            - 1: Critically important, contains key private lending information
            
            Format your response as a JSON array with the following structure:
            [
                {
                    "event_id": "id1",
                    "importance": 0.8,
                    "reason": "Brief explanation of why this event is important"
                },
                {
                    "event_id": "id2",
                    "importance": 0.3,
                    "reason": "Brief explanation of why this event is less important"
                },
                ...
            ]
            
            Focus on events that contain:
            1. Loan structure and size
            2. Interest rates and fees
            3. Security and collateral
            4. Covenants and conditions
            5. Borrower profile and credit quality
            6. Risk assessment and mitigants
            7. Expected returns and yield
            8. Exit strategies and refinancing
            """
        else:  # general
            return self._default_attention_prompt()
