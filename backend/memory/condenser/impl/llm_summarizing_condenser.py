"""
LLM-based summarizing condenser for Cori RAG++ system.
Uses OpenAI's GPT-4o to create concise summaries of past events.
"""

from typing import Dict, List, Optional, Any, Union
import os
import json
from openai import OpenAI
from ...models.event import Event
from ..condenser import RollingCondenser

class LLMSummarizingCondenser(RollingCondenser):
    """
    A condenser that creates concise summaries of past events using an LLM.
    This is particularly useful for financial modeling contexts where
    preserving key parameters and assumptions is essential.
    """
    
    def __init__(
        self,
        max_size: int = 100,
        keep_first: int = 1,
        keep_last: int = 10,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        summary_prompt_template: Optional[str] = None,
        max_tokens_per_batch: int = 8000,
        max_summary_tokens: int = 1000
    ):
        """
        Initialize the LLM summarizing condenser.
        
        Args:
            max_size: Maximum number of events to keep
            keep_first: Number of initial events to always keep
            keep_last: Number of recent events to always keep
            api_key: OpenAI API key (defaults to environment variable)
            model: OpenAI model to use
            summary_prompt_template: Optional custom prompt template for summarization
            max_tokens_per_batch: Maximum tokens per batch for summarization
            max_summary_tokens: Maximum tokens for the summary
        """
        super().__init__(max_size, keep_first, keep_last)
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.summary_prompt_template = summary_prompt_template or self._default_summary_prompt()
        self.max_tokens_per_batch = max_tokens_per_batch
        self.max_summary_tokens = max_summary_tokens
    
    def _default_summary_prompt(self) -> str:
        """
        Get the default summary prompt template.
        
        Returns:
            Default summary prompt template
        """
        return """
        You are an expert financial analyst assistant tasked with summarizing a conversation about financial modeling.
        Your goal is to create a concise summary that preserves all critical financial information, including:
        
        1. Key financial parameters and assumptions
        2. Important financial metrics and ratios
        3. Transaction structures and terms
        4. Valuation methodologies and multiples
        5. Debt and equity components
        6. Cash flow projections and sensitivities
        
        Here is the conversation to summarize:
        
        {conversation}
        
        Create a concise summary that preserves all critical financial information.
        Format your response as a JSON object with the following structure:
        {
            "summary": "The concise summary text",
            "key_parameters": {
                "parameter1": "value1",
                "parameter2": "value2",
                ...
            },
            "financial_metrics": {
                "metric1": "value1",
                "metric2": "value2",
                ...
            }
        }
        
        Only include parameters and metrics that were explicitly mentioned in the conversation.
        """
    
    def _events_to_conversation(self, events: List[Event]) -> str:
        """
        Convert events to a conversation format.
        
        Args:
            events: List of events to convert
            
        Returns:
            Conversation string
        """
        conversation = ""
        for event in events:
            role = event.role.capitalize()
            conversation += f"{role}: {event.content}\n\n"
        return conversation
    
    def _create_summary(self, events: List[Event]) -> Dict[str, Any]:
        """
        Create a summary of events using the LLM.
        
        Args:
            events: List of events to summarize
            
        Returns:
            Summary as a dictionary
        """
        conversation = self._events_to_conversation(events)
        prompt = self.summary_prompt_template.format(conversation=conversation)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial summarization assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=self.max_summary_tokens
            )
            
            summary_text = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                summary_data = json.loads(summary_text)
                return summary_data
            except json.JSONDecodeError:
                # If not valid JSON, just use the text as summary
                return {"summary": summary_text, "key_parameters": {}, "financial_metrics": {}}
            
        except Exception as e:
            print(f"Error creating summary: {e}")
            return {"summary": "Error creating summary", "key_parameters": {}, "financial_metrics": {}}
    
    def _create_summary_event(self, events: List[Event], summary_data: Dict[str, Any]) -> Event:
        """
        Create a summary event from the summary data.
        
        Args:
            events: Original events being summarized
            summary_data: Summary data from the LLM
            
        Returns:
            Summary event
        """
        # Get the first event's timestamp for reference
        first_timestamp = events[0].timestamp if events else None
        
        # Create the summary content
        summary_content = f"[SUMMARY OF {len(events)} EVENTS]\n\n{summary_data['summary']}"
        
        # Add key parameters if available
        if summary_data.get("key_parameters"):
            summary_content += "\n\nKey Parameters:\n"
            for param, value in summary_data["key_parameters"].items():
                summary_content += f"- {param}: {value}\n"
        
        # Add financial metrics if available
        if summary_data.get("financial_metrics"):
            summary_content += "\n\nFinancial Metrics:\n"
            for metric, value in summary_data["financial_metrics"].items():
                summary_content += f"- {metric}: {value}\n"
        
        # Create the summary event
        return Event(
            id=f"summary_{events[0].id if events else 'unknown'}",
            role="assistant",
            content=summary_content,
            timestamp=first_timestamp,
            metadata={
                "type": "summary",
                "summarized_events": len(events),
                "first_event_id": events[0].id if events else None,
                "last_event_id": events[-1].id if events else None
            }
        )
    
    def _condense_middle(self, events: List[Event]) -> List[Event]:
        """
        Condense the middle section by creating a summary.
        
        Args:
            events: List of events to condense
            
        Returns:
            Condensed list of events
        """
        if not events:
            return []
        
        # If we have very few events, don't summarize
        if len(events) <= 3:
            return events
        
        # Create a summary of the events
        summary_data = self._create_summary(events)
        
        # Create a summary event
        summary_event = self._create_summary_event(events, summary_data)
        
        # Store the summary data in the condenser's metadata
        self.add_metadata("last_summary", summary_data)
        
        # Return the summary event
        return [summary_event]


class FinancialLLMSummarizingCondenser(LLMSummarizingCondenser):
    """
    A specialized LLM summarizing condenser for financial modeling contexts.
    Uses a domain-specific prompt template to preserve critical financial information.
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
        max_summary_tokens: int = 1000
    ):
        """
        Initialize the financial LLM summarizing condenser.
        
        Args:
            domain: Financial domain (lbo, ma, debt, private_lending, general)
            max_size: Maximum number of events to keep
            keep_first: Number of initial events to always keep
            keep_last: Number of recent events to always keep
            api_key: OpenAI API key (defaults to environment variable)
            model: OpenAI model to use
            max_tokens_per_batch: Maximum tokens per batch for summarization
            max_summary_tokens: Maximum tokens for the summary
        """
        self.domain = domain
        summary_prompt_template = self._get_domain_specific_prompt(domain)
        
        super().__init__(
            max_size=max_size,
            keep_first=keep_first,
            keep_last=keep_last,
            api_key=api_key,
            model=model,
            summary_prompt_template=summary_prompt_template,
            max_tokens_per_batch=max_tokens_per_batch,
            max_summary_tokens=max_summary_tokens
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
            You are an expert LBO modeling analyst tasked with summarizing a conversation about leveraged buyout modeling.
            Your goal is to create a concise summary that preserves all critical LBO information, including:
            
            1. Transaction structure and purchase price
            2. Debt and equity components
            3. Leverage ratios and debt tranches
            4. EBITDA multiples (entry and exit)
            5. Financial projections and assumptions
            6. Returns (IRR, MOIC)
            7. Debt paydown and refinancing
            8. Covenants and terms
            
            Here is the conversation to summarize:
            
            {conversation}
            
            Create a concise summary that preserves all critical LBO information.
            Format your response as a JSON object with the following structure:
            {
                "summary": "The concise summary text",
                "transaction_structure": {
                    "purchase_price": "value",
                    "entry_multiple": "value",
                    "exit_multiple": "value",
                    "equity_contribution": "value",
                    "debt_financing": "value"
                },
                "debt_structure": {
                    "total_leverage": "value",
                    "senior_debt": "value",
                    "subordinated_debt": "value",
                    "other_debt": "value"
                },
                "financial_projections": {
                    "revenue_growth": "value",
                    "ebitda_margin": "value",
                    "capex": "value"
                },
                "returns": {
                    "irr": "value",
                    "moic": "value",
                    "exit_year": "value"
                }
            }
            
            Only include parameters and metrics that were explicitly mentioned in the conversation.
            """
        elif domain == "ma":
            return """
            You are an expert M&A analyst tasked with summarizing a conversation about mergers and acquisitions modeling.
            Your goal is to create a concise summary that preserves all critical M&A information, including:
            
            1. Transaction structure and purchase price
            2. Valuation multiples and methodologies
            3. Synergies (cost and revenue)
            4. Pro forma financials
            5. Accretion/dilution analysis
            6. Financing structure
            7. Deal terms and conditions
            8. Integration considerations
            
            Here is the conversation to summarize:
            
            {conversation}
            
            Create a concise summary that preserves all critical M&A information.
            Format your response as a JSON object with the following structure:
            {
                "summary": "The concise summary text",
                "transaction_structure": {
                    "purchase_price": "value",
                    "premium": "value",
                    "consideration_mix": "value",
                    "transaction_multiple": "value"
                },
                "synergies": {
                    "cost_synergies": "value",
                    "revenue_synergies": "value",
                    "integration_costs": "value",
                    "synergy_timeline": "value"
                },
                "financial_impact": {
                    "accretion_dilution": "value",
                    "eps_impact": "value",
                    "pro_forma_metrics": "value"
                },
                "deal_terms": {
                    "closing_conditions": "value",
                    "breakup_fee": "value",
                    "regulatory_considerations": "value"
                }
            }
            
            Only include parameters and metrics that were explicitly mentioned in the conversation.
            """
        elif domain == "debt":
            return """
            You are an expert debt modeling analyst tasked with summarizing a conversation about debt modeling.
            Your goal is to create a concise summary that preserves all critical debt information, including:
            
            1. Debt structure and tranches
            2. Interest rates and terms
            3. Amortization schedules
            4. Covenants and conditions
            5. Refinancing considerations
            6. Credit metrics and ratios
            7. Cash flow available for debt service
            8. Default scenarios and sensitivities
            
            Here is the conversation to summarize:
            
            {conversation}
            
            Create a concise summary that preserves all critical debt information.
            Format your response as a JSON object with the following structure:
            {
                "summary": "The concise summary text",
                "debt_structure": {
                    "total_debt": "value",
                    "senior_debt": "value",
                    "subordinated_debt": "value",
                    "other_debt": "value"
                },
                "terms": {
                    "interest_rates": "value",
                    "maturity": "value",
                    "amortization": "value",
                    "fees": "value"
                },
                "covenants": {
                    "leverage_covenant": "value",
                    "interest_coverage": "value",
                    "fixed_charge_coverage": "value"
                },
                "credit_metrics": {
                    "debt_to_ebitda": "value",
                    "interest_coverage_ratio": "value",
                    "dscr": "value"
                }
            }
            
            Only include parameters and metrics that were explicitly mentioned in the conversation.
            """
        elif domain == "private_lending":
            return """
            You are an expert private lending analyst tasked with summarizing a conversation about private lending.
            Your goal is to create a concise summary that preserves all critical private lending information, including:
            
            1. Loan structure and size
            2. Interest rates and fees
            3. Security and collateral
            4. Covenants and conditions
            5. Borrower profile and credit quality
            6. Risk assessment and mitigants
            7. Expected returns and yield
            8. Exit strategies and refinancing
            
            Here is the conversation to summarize:
            
            {conversation}
            
            Create a concise summary that preserves all critical private lending information.
            Format your response as a JSON object with the following structure:
            {
                "summary": "The concise summary text",
                "loan_structure": {
                    "loan_size": "value",
                    "loan_type": "value",
                    "term": "value",
                    "amortization": "value"
                },
                "economics": {
                    "interest_rate": "value",
                    "fees": "value",
                    "all_in_yield": "value",
                    "expected_return": "value"
                },
                "security": {
                    "collateral": "value",
                    "guarantees": "value",
                    "lien_position": "value"
                },
                "covenants": {
                    "financial_covenants": "value",
                    "reporting_requirements": "value",
                    "restrictions": "value"
                }
            }
            
            Only include parameters and metrics that were explicitly mentioned in the conversation.
            """
        else:  # general
            return self._default_summary_prompt()
