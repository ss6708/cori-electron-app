# Mapping OpenHands Memory Mechanisms to Cori's Financial Domains

This document maps OpenHands' memory mechanisms to Cori's financial domain requirements, showing how each component can be adapted for financial modeling contexts.

## 1. Event-Based Memory System

OpenHands' event-based memory system can be mapped to financial modeling domains through specialized event types:

```python
# Base Financial Event
class FinancialModelingEvent(Event):
    """Base class for all financial modeling events."""
    domain: str  # "lbo", "ma", "debt", "private_lending"
    timestamp: datetime
    user_id: str
    session_id: str

# Domain-Specific Events
class LBOModelingAction(FinancialModelingEvent):
    """Actions related to LBO modeling."""
    action_type: str  # "transaction_structure", "debt_sizing", "exit_analysis"
    parameters: dict  # Transaction parameters, assumptions, etc.
    
class MAModelingAction(FinancialModelingEvent):
    """Actions related to M&A modeling."""
    action_type: str  # "valuation", "synergies", "accretion_dilution"
    parameters: dict  # Deal parameters, synergy assumptions, etc.
    
class DebtModelingAction(FinancialModelingEvent):
    """Actions related to debt modeling."""
    action_type: str  # "sizing", "covenants", "amortization"
    parameters: dict  # Debt parameters, covenant thresholds, etc.
    
class PrivateLendingAction(FinancialModelingEvent):
    """Actions related to private lending."""
    action_type: str  # "terms", "security", "returns", "risk"
    parameters: dict  # Loan terms, collateral details, etc.

# Excel Operation Events
class ExcelOperationEvent(FinancialModelingEvent):
    """Events related to Excel operations."""
    operation_type: str  # "set_formula", "create_table", "format_cells"
    worksheet: str
    range_reference: str
    content: str  # Formula, value, etc.
    domain_context: str  # Which financial domain this operation relates to

# User Preference Events
class UserPreferenceEvent(FinancialModelingEvent):
    """Events capturing user preferences."""
    preference_type: str  # "modeling", "analysis", "visualization"
    preference_value: any  # The actual preference value
    preference_context: str  # Context in which the preference was expressed
```

## 2. Memory Condensation Strategies

OpenHands' memory condensation strategies can be adapted for financial modeling contexts:

```python
class FinancialDomainCondenser(RollingCondenser):
    """Base condenser for financial domain contexts."""
    
    def __init__(self, llm: LLM, max_size: int = 100, keep_first: int = 1):
        super().__init__()
        self.max_size = max_size
        self.keep_first = keep_first
        self.llm = llm
        
    def identify_critical_events(self, events: list[Event]) -> list[Event]:
        """Identify domain-specific critical events to preserve."""
        raise NotImplementedError("Subclasses must implement this method")
        
    def condense(self, events: list[Event]) -> list[Event]:
        """Preserve critical financial modeling information while condensing history."""
        if len(events) <= self.max_size:
            return events
            
        # Keep initial user requirements
        head = events[:self.keep_first]
        
        # Identify domain-specific critical events
        critical_events = self.identify_critical_events(events)
        
        # Keep recent interactions with remaining slots
        remaining_slots = self.max_size - len(head) - len(critical_events)
        tail = events[-remaining_slots:] if remaining_slots > 0 else []
        
        return head + critical_events + tail

class LBOModelingCondenser(FinancialDomainCondenser):
    """Condenser specialized for LBO modeling contexts."""
    
    def identify_critical_events(self, events: list[Event]) -> list[Event]:
        """Identify critical LBO modeling events to preserve."""
        # Identify events by type and recency
        transaction_events = [e for e in events if isinstance(e, LBOModelingAction) 
                             and e.action_type == "transaction_structure"]
        debt_events = [e for e in events if isinstance(e, LBOModelingAction)
                      and e.action_type == "debt_sizing"]
        exit_events = [e for e in events if isinstance(e, LBOModelingAction)
                      and e.action_type == "exit_analysis"]
        
        # Keep the most recent of each critical event type
        critical_events = []
        if transaction_events:
            critical_events.append(transaction_events[-1])
        if debt_events:
            critical_events.append(debt_events[-1])
        if exit_events:
            critical_events.append(exit_events[-1])
            
        return critical_events
```

Similar condensers would be implemented for M&A, Debt Modeling, and Private Lending domains.

## 3. Financial LLM Summarizing Condenser

```python
class FinancialLLMSummarizingCondenser(RollingCondenser):
    """A condenser that creates concise summaries of financial modeling history."""
    
    def condense(self, events: list[Event]) -> list[Event]:
        """Summarize forgotten financial modeling events."""
        if len(events) <= self.max_size:
            return events
            
        # Identify events to be forgotten
        head = events[:self.keep_first]
        target_size = self.max_size // 2
        events_from_tail = target_size - len(head)
        tail = events[-events_from_tail:]
        forgotten_events = events[self.keep_first:-events_from_tail]
        
        # Construct domain-specific prompt for summarization
        prompt = """You are maintaining the memory of a financial modeling assistant. Summarize the key information from these events, preserving:

TRANSACTION PARAMETERS: Purchase price, valuation multiples, deal structure, financing terms
FINANCIAL PROJECTIONS: Growth rates, margins, working capital, capital expenditures
DEBT STRUCTURE: Tranches, interest rates, amortization schedules, covenants
RETURNS ANALYSIS: Exit assumptions, IRR calculations, sensitivity analysis
USER PREFERENCES: Modeling approaches, analysis methods, visualization preferences"""
        
        # Add previous summary if it exists
        summary_event = None
        for event in events[self.keep_first:self.keep_first+1]:
            if isinstance(event, AgentCondensationObservation):
                summary_event = event
                prompt += f"\n\nPREVIOUS SUMMARY:\n{summary_event.message}"
                
        # Add forgotten events to the prompt
        prompt += "\n\nEVENTS TO SUMMARIZE:"
        for event in forgotten_events:
            prompt += f"\n{str(event)}"
            
        # Get summary from LLM
        response = self.llm.completion(
            messages=[{"content": prompt, "role": "user"}]
        )
        summary = response.choices[0].message.content
        
        return head + [AgentCondensationObservation(summary)] + tail
```

## 4. Long-Term Memory Vector Storage

OpenHands' long-term memory system can be adapted for financial domains through specialized collections:

```python
FINANCIAL_COLLECTIONS = {
    "lbo": {
        "description": "Leveraged Buyout modeling knowledge",
        "subcollections": {
            "structure": {
                "description": "Transaction structure knowledge",
                "metadata_schema": {
                    "purchase_price_range": "string",  # e.g., "100M-500M"
                    "entry_multiple_range": "string",  # e.g., "8x-12x"
                    "leverage_range": "string",  # e.g., "4x-6x"
                    "industry": "string"  # e.g., "Technology", "Healthcare"
                }
            },
            "returns": {
                "description": "Returns analysis knowledge",
                "metadata_schema": {
                    "holding_period_range": "string",  # e.g., "3-5 years"
                    "exit_multiple_range": "string",  # e.g., "8x-12x"
                    "target_irr_range": "string"  # e.g., "20%-25%"
                }
            },
            "debt": {
                "description": "LBO debt structure knowledge",
                "metadata_schema": {
                    "debt_type": "string",  # e.g., "Term Loan B", "Senior Notes"
                    "interest_rate_type": "string",  # e.g., "Fixed", "Floating"
                    "maturity_range": "string"  # e.g., "5-7 years"
                }
            }
        }
    },
    "ma": {
        "description": "Mergers & Acquisitions modeling knowledge",
        "subcollections": {
            "valuation": {
                "description": "Valuation methodology knowledge",
                "metadata_schema": {
                    "valuation_method": "string",  # e.g., "DCF", "Multiples"
                    "industry": "string"
                }
            },
            "synergies": {
                "description": "Synergy analysis knowledge",
                "metadata_schema": {
                    "synergy_type": "string",  # e.g., "Revenue", "Cost"
                    "industry": "string"
                }
            }
        }
    }
}
```

Similar subcollections would be defined for Debt Modeling and Private Lending domains.

## 5. Financial Search Function

```python
def search_financial_knowledge(
    query: str,
    domain: str = None,
    subcollection: str = None,
    metadata_filters: dict = None,
    k: int = 10
) -> list[Document]:
    """Search for financial knowledge with domain-specific filtering."""
    # Select the appropriate collection based on domain
    collection = db.get_collection(domain) if domain else db.get_collection("all_financial")
    
    # Build metadata filters
    filter_conditions = {}
    if subcollection:
        filter_conditions["subcollection"] = subcollection
    if metadata_filters:
        for key, value in metadata_filters.items():
            filter_conditions[f"metadata.{key}"] = value
    
    # Perform vector similarity search
    results = collection.query(
        query_texts=[query],
        n_results=k,
        where=filter_conditions if filter_conditions else None
    )
    
    return results
```

## 6. Microagent System for Financial Expertise

OpenHands' microagent system can be adapted for financial domain expertise:

```markdown
---
name: lbo_expert
type: knowledge
triggers:
  - leveraged buyout
  - LBO
  - debt multiple
  - exit multiple
  - sponsor returns
---

# LBO Modeling Best Practices

## Transaction Structure
- Purchase price typically expressed as a multiple of EBITDA (8-12x)
- Sources of funds include equity contribution (40-60%), debt financing (40-60%)
- Pro forma capital structure should be optimized for target returns

## Operational Projections
- Revenue growth assumptions should be based on historical performance
- EBITDA margin expansion opportunities should be realistic
- Working capital requirements typically 10-15% of revenue

## Debt Structure
- Senior debt typically 3-5x EBITDA with 5-7 year maturity
- Subordinated debt can add 1-2x additional leverage
- Financial covenants include leverage ratio and interest coverage ratio

## Returns Analysis
- Target IRR for private equity sponsors typically 20-25%
- Multiple of Invested Capital (MOIC) target typically 2.0-3.0x
- Exit typically modeled at similar or slightly lower multiple than entry
```

Similar microagents would be created for M&A, Debt Modeling, and Private Lending domains.
