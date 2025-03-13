from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime

from ...models.event import Event, CondensationEvent
from ..condenser import RollingCondenser

class LLMSummarizingCondenser(RollingCondenser):
    """
    A condenser that creates concise summaries of past events using an LLM.
    This is particularly useful for financial modeling contexts where
    preserving key parameters and assumptions is essential.
    """
    
    def __init__(
        self, 
        llm_client, 
        max_size: int = 100, 
        keep_first: int = 1,
        summary_prompt_template: Optional[str] = None
    ):
        """
        Initialize the LLM summarizing condenser.
        
        Args:
            llm_client: Client for LLM API calls
            max_size: Maximum number of events to keep
            keep_first: Number of initial events to always keep
            summary_prompt_template: Optional custom prompt template for summarization
        """
        super().__init__(max_size, keep_first)
        self.llm_client = llm_client
        self.summary_prompt_template = summary_prompt_template or self._default_summary_prompt()
    
    def _default_summary_prompt(self) -> str:
        """
        Get the default summary prompt template.
        
        Returns:
            Default prompt template for summarization
        """
        return """You are maintaining the memory of a financial modeling assistant. 
        Summarize the key information from these events, preserving:

        TRANSACTION PARAMETERS: Purchase price, valuation multiples, deal structure, financing terms
        FINANCIAL PROJECTIONS: Growth rates, margins, working capital, capital expenditures
        DEBT STRUCTURE: Tranches, interest rates, amortization schedules, covenants
        RETURNS ANALYSIS: Exit assumptions, IRR calculations, sensitivity analysis
        USER PREFERENCES: Modeling approaches, analysis methods, visualization preferences

        FORMAT YOUR SUMMARY AS:
        TRANSACTION: {Key transaction parameters}
        PROJECTIONS: {Key projection assumptions}
        DEBT: {Key debt structure and terms}
        RETURNS: {Key return metrics and assumptions}
        PREFERENCES: {User's preferred approaches}

        PRIORITIZE information that affects model outputs and financial conclusions.
        
        PREVIOUS SUMMARY:
        {previous_summary}
        
        EVENTS TO SUMMARIZE:
        {events_to_summarize}
        """
    
    def _summarize_events(self, events: List[Event], previous_summary: Optional[str] = None) -> str:
        """
        Use the LLM to summarize a list of events.
        
        Args:
            events: List of events to summarize
            previous_summary: Optional previous summary to build upon
            
        Returns:
            Summarized content
        """
        if not events:
            return previous_summary or ""
        
        # Format events for the prompt
        events_text = "\n".join([str(event.to_dict()) for event in events])
        
        # Prepare the prompt
        prompt = self.summary_prompt_template.format(
            previous_summary=previous_summary or "No previous summary available.",
            events_to_summarize=events_text
        )
        
        # Get summary from LLM
        response = self.llm_client.get_completion(
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content
    
    def condense(self, events: List[Event]) -> List[Event]:
        """
        If the history is too long, summarize forgotten events.
        
        Args:
            events: List of events to condense
            
        Returns:
            Condensed list of events
        """
        if len(events) <= self.max_size:
            return events
        
        # Keep initial events
        head = events[:self.keep_first]
        
        # Keep recent events
        target_size = self.max_size // 2
        events_from_tail = target_size - len(head)
        tail = events[-events_from_tail:] if events_from_tail > 0 else []
        
        # Identify events to be forgotten
        forgotten_events = events[self.keep_first:-events_from_tail] if events_from_tail > 0 else events[self.keep_first:]
        
        # Check if we already have a summary event
        previous_summary = None
        if len(events) > self.keep_first and isinstance(events[self.keep_first], CondensationEvent):
            previous_summary = events[self.keep_first].content
        
        # Summarize forgotten events
        summary = self._summarize_events(forgotten_events, previous_summary)
        
        # Create condensation event
        condensation_event = CondensationEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_id=forgotten_events[0].user_id if forgotten_events else "system",
            session_id=forgotten_events[0].session_id if forgotten_events else "system",
            content=summary,
            original_event_ids=[event.id for event in forgotten_events]
        )
        
        return head + [condensation_event] + tail
