from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime

from ...models.event import Event, CondensationEvent
from ..condenser import RollingCondenser

class LLMAttentionCondenser(RollingCondenser):
    """
    A condenser that uses an LLM to identify and prioritize important events.
    This is particularly useful for financial modeling contexts where
    some events are more critical than others for maintaining context.
    """
    
    def __init__(
        self, 
        llm_client,
        max_size: int = 100, 
        keep_first: int = 1,
        attention_prompt_template: Optional[str] = None,
        max_attention_events: int = 20
    ):
        """
        Initialize the LLM attention condenser.
        
        Args:
            llm_client: Client for LLM API calls
            max_size: Maximum number of events to keep
            keep_first: Number of initial events to always keep
            attention_prompt_template: Optional custom prompt template for attention scoring
            max_attention_events: Maximum number of events to score at once
        """
        super().__init__(max_size, keep_first)
        self.llm_client = llm_client
        self.attention_prompt_template = attention_prompt_template or self._default_attention_prompt()
        self.max_attention_events = max_attention_events
    
    def _default_attention_prompt(self) -> str:
        """
        Get the default attention prompt template.
        
        Returns:
            Default prompt template for attention scoring
        """
        return """You are maintaining the memory of a financial modeling assistant.
        Analyze these events and identify the most important ones for maintaining context.
        
        For each event, assign an importance score from 1-10 based on:
        - How critical the information is for financial modeling
        - How likely the information will be needed for future calculations
        - How unique or irreplaceable the information is
        
        PRIORITIZE events that contain:
        - Key financial parameters (rates, multiples, prices)
        - Model structure decisions
        - User preferences about modeling approaches
        - Critical assumptions that affect outputs
        
        FORMAT YOUR RESPONSE AS A JSON ARRAY:
        [
          {"event_id": "id1", "importance": 8, "reason": "Contains key transaction multiple"},
          {"event_id": "id2", "importance": 3, "reason": "Redundant information"},
          ...
        ]
        
        EVENTS TO ANALYZE:
        {events_to_analyze}
        """
    
    def _score_events(self, events: List[Event]) -> Dict[str, int]:
        """
        Use the LLM to score events by importance.
        
        Args:
            events: List of events to score
            
        Returns:
            Dictionary mapping event IDs to importance scores
        """
        if not events:
            return {}
        
        # Format events for the prompt
        events_text = "\n".join([
            f"EVENT {i} (ID: {event.id}):\n{str(event.to_dict())}\n"
            for i, event in enumerate(events)
        ])
        
        # Prepare the prompt
        prompt = self.attention_prompt_template.format(
            events_to_analyze=events_text
        )
        
        # Get scores from LLM
        response = self.llm_client.get_completion(
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        try:
            import json
            scores_data = json.loads(response.content)
            
            # Convert to dictionary
            scores = {}
            for item in scores_data:
                event_id = item.get("event_id")
                importance = item.get("importance")
                if event_id and importance:
                    scores[event_id] = importance
            
            return scores
        except Exception as e:
            # If parsing fails, return empty scores
            print(f"Error parsing attention scores: {e}")
            return {}
    
    def condense(self, events: List[Event]) -> List[Event]:
        """
        Keep the most important events based on LLM attention scoring.
        
        Args:
            events: List of events to condense
            
        Returns:
            Condensed list of events
        """
        if len(events) <= self.max_size:
            return events
        
        # Keep initial events
        head = events[:self.keep_first]
        
        # Score remaining events
        remaining_events = events[self.keep_first:]
        
        # If there are too many events, score them in batches
        if len(remaining_events) > self.max_attention_events:
            # Score the most recent events
            recent_events = remaining_events[-self.max_attention_events:]
            scores = self._score_events(recent_events)
            
            # For older events, use a simple heuristic (keep every other event)
            older_events = remaining_events[:-self.max_attention_events]
            older_events_to_keep = older_events[::2]  # Keep every other event
            
            # Combine scored recent events with heuristically selected older events
            scored_events = [(event, scores.get(event.id, 0)) for event in recent_events]
            scored_events.sort(key=lambda x: x[1], reverse=True)
            
            # Calculate how many recent events to keep
            recent_to_keep = min(len(scored_events), self.max_size - len(head) - len(older_events_to_keep))
            
            # Select the highest-scored recent events
            important_events = [event for event, _ in scored_events[:recent_to_keep]]
            
            # Combine with older events and preserve order
            all_events = older_events_to_keep + important_events
            all_events.sort(key=lambda x: events.index(x))
            
            return head + all_events
        else:
            # Score all remaining events
            scores = self._score_events(remaining_events)
            
            # Sort events by importance score
            scored_events = [(event, scores.get(event.id, 0)) for event in remaining_events]
            scored_events.sort(key=lambda x: x[1], reverse=True)
            
            # Select the highest-scored events
            important_events = [event for event, _ in scored_events[:self.max_size - len(head)]]
            
            # Preserve original order
            important_events.sort(key=lambda x: events.index(x))
            
            return head + important_events
