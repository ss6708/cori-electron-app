"""
Example of using condensers in the Cori RAG++ system.
"""

import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from memory.models.event import Event
from memory.conversation_memory import ConversationMemory
from memory.condenser.condenser import RecentEventsCondenser
from memory.condenser.impl.financial_domain_condensers import (
    FinancialDomainCondenser,
    LBOModelingCondenser
)
from memory.condenser.impl.llm_summarizing_condenser import (
    LLMSummarizingCondenser,
    FinancialLLMSummarizingCondenser
)
from memory.condenser.impl.llm_attention_condenser import (
    LLMAttentionCondenser,
    FinancialLLMAttentionCondenser
)

def create_sample_events() -> List[Event]:
    """Create sample events for demonstration."""
    events = [
        Event(
            id="1",
            role="user",
            content="I'm looking to model an LBO for a software company with $50M in revenue and $15M in EBITDA.",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="2",
            role="assistant",
            content="Great, I can help you model an LBO for a software company. Let's start with some key assumptions. What EBITDA multiple are you considering for the purchase price?",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="3",
            role="user",
            content="I'm thinking of a 10x EBITDA multiple, so a $150M purchase price.",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="4",
            role="assistant",
            content="A 10x EBITDA multiple is reasonable for a software company with good growth prospects. For a $150M purchase price, let's consider the capital structure. Typically, software LBOs can support 5-6x EBITDA in debt due to recurring revenue. That would be $75-90M in debt, with the remainder as equity.",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="5",
            role="user",
            content="That sounds good. Let's use 5.5x EBITDA for debt, so $82.5M in debt and $67.5M in equity.",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="6",
            role="assistant",
            content="Perfect. With $82.5M in debt (5.5x EBITDA) and $67.5M in equity, your capital structure is 55% debt and 45% equity, which is reasonable for a software LBO. Now, let's consider the debt tranches. Typically, you might have a senior secured term loan, a second lien, and potentially a revolver for working capital.",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="7",
            role="user",
            content="How would you recommend structuring the debt tranches?",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="8",
            role="assistant",
            content="For the $82.5M in debt, I would recommend:\n\n1. Senior Secured Term Loan: $60M (4.0x EBITDA) at L+350-400 bps\n2. Second Lien: $22.5M (1.5x EBITDA) at L+700-750 bps\n3. Revolver: $10M (undrawn at close) at L+350 bps\n\nThis structure gives you a blended interest rate of approximately 6-7% depending on the current LIBOR/SOFR rate.",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="9",
            role="user",
            content="That makes sense. What about the exit multiple? Should we assume the same 10x or something different?",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="10",
            role="assistant",
            content="For conservative modeling, it's often prudent to assume the same exit multiple as the entry multiple (10x in this case). However, if you expect to significantly improve the business during your holding period (through organic growth, margin expansion, or bolt-on acquisitions), you could justify a slightly higher exit multiple, perhaps 11-12x. For base case modeling, I'd suggest using the same 10x multiple.",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="11",
            role="user",
            content="Let's use 10x for the base case. What IRR and MOIC would you expect with a 5-year holding period?",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="12",
            role="assistant",
            content="To calculate the expected IRR and MOIC with a 5-year holding period, we need to project the EBITDA growth. Assuming:\n\n- Initial EBITDA: $15M\n- Annual EBITDA growth: 10% (typical for a growing software company)\n- Exit multiple: 10x\n- Holding period: 5 years\n\nYear 5 EBITDA would be approximately $24.2M. At a 10x multiple, that's an enterprise value of $242M. After repaying the debt (assuming some paydown over the period), the equity value would be significantly higher than your initial $67.5M investment.\n\nThis could result in:\n- MOIC: ~2.5-3.0x\n- IRR: ~20-25%\n\nThese returns are in line with typical private equity expectations for a successful software LBO.",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="13",
            role="user",
            content="That's helpful. What about the debt covenants? What should we include in the model?",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="14",
            role="assistant",
            content="For debt covenants in your LBO model, you should include the following:\n\n1. Leverage Ratio Covenant: Maximum Total Debt / EBITDA, typically starting at 5.5-6.0x and stepping down by 0.25-0.5x annually. For your software company, it might start at 5.5x and step down to 3.5-4.0x by year 5.\n\n2. Interest Coverage Ratio: Minimum EBITDA / Interest Expense, typically 2.0-2.5x. For software companies with strong cash flow, this might be set at 2.0x initially.\n\n3. Fixed Charge Coverage Ratio: Minimum (EBITDA - CapEx - Taxes) / (Interest + Principal Payments), typically 1.1-1.25x.\n\n4. Maximum Capital Expenditure: Limits on annual CapEx spending, though this is less restrictive for software companies with limited CapEx needs.\n\nYou should model covenant compliance in your financial projections to ensure the company maintains adequate headroom throughout the investment period.",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="15",
            role="user",
            content="Great. Can you help me understand how to model the debt paydown over the 5-year period?",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="16",
            role="assistant",
            content="For modeling debt paydown over the 5-year period, you'll need to consider both mandatory and optional repayments:\n\n1. Mandatory Amortization:\n   - Senior Term Loan: Typically 1-5% per year (let's use 2.5% or $1.5M per year)\n   - Second Lien: Often no mandatory amortization (interest-only)\n\n2. Excess Cash Flow Sweep:\n   - Typically 50-75% of excess cash flow must be used to repay debt\n   - This percentage often steps down as leverage decreases\n   - For modeling, calculate: (EBITDA - CapEx - Interest - Taxes - Mandatory Amortization) * Sweep Percentage\n\n3. Optional Prepayments:\n   - Any additional cash can be used for optional prepayments\n   - Typically applied to the highest interest rate debt first\n\nFor your model, I'd suggest:\n\nYear 1: $1.5M mandatory + ~$3-4M from excess cash flow\nYear 2: $1.5M mandatory + ~$4-5M from excess cash flow\nYear 3: $1.5M mandatory + ~$5-6M from excess cash flow\nYear 4: $1.5M mandatory + ~$6-7M from excess cash flow\nYear 5: $1.5M mandatory + ~$7-8M from excess cash flow\n\nThis would reduce your $82.5M debt to approximately $40-45M by exit, significantly increasing the equity value and returns.",
            timestamp=datetime.now().isoformat()
        )
    ]
    return events

def demonstrate_recent_events_condenser():
    """Demonstrate the RecentEventsCondenser."""
    print("\n=== RecentEventsCondenser Demonstration ===")
    
    # Create sample events
    events = create_sample_events()
    print(f"Original event count: {len(events)}")
    
    # Create condenser
    condenser = RecentEventsCondenser(max_size=10, keep_first=2, keep_last=3)
    
    # Condense events
    condensed_events = condenser.condense(events)
    print(f"Condensed event count: {len(condensed_events)}")
    
    # Print preserved events
    print("\nPreserved events:")
    for i, event in enumerate(condensed_events):
        print(f"Event {i+1} (ID: {event.id}): {event.role} - {event.content[:50]}...")

def demonstrate_financial_domain_condenser():
    """Demonstrate the FinancialDomainCondenser."""
    print("\n=== FinancialDomainCondenser Demonstration ===")
    
    # Create sample events
    events = create_sample_events()
    print(f"Original event count: {len(events)}")
    
    # Create condenser
    condenser = FinancialDomainCondenser(max_size=10, keep_first=2, keep_last=3, importance_threshold=0.7)
    
    # Condense events
    condensed_events = condenser.condense(events)
    print(f"Condensed event count: {len(condensed_events)}")
    
    # Print preserved events
    print("\nPreserved events:")
    for i, event in enumerate(condensed_events):
        print(f"Event {i+1} (ID: {event.id}): {event.role} - {event.content[:50]}...")
        
    # Print importance scores for all events
    print("\nImportance scores:")
    for event in events:
        importance = condenser._calculate_importance(event)
        print(f"Event {event.id}: {importance:.2f} - {event.content[:50]}...")

def demonstrate_lbo_modeling_condenser():
    """Demonstrate the LBOModelingCondenser."""
    print("\n=== LBOModelingCondenser Demonstration ===")
    
    # Create sample events
    events = create_sample_events()
    print(f"Original event count: {len(events)}")
    
    # Create condenser
    condenser = LBOModelingCondenser(max_size=10, keep_first=2, keep_last=3, importance_threshold=0.7)
    
    # Condense events
    condensed_events = condenser.condense(events)
    print(f"Condensed event count: {len(condensed_events)}")
    
    # Print preserved events
    print("\nPreserved events:")
    for i, event in enumerate(condensed_events):
        print(f"Event {i+1} (ID: {event.id}): {event.role} - {event.content[:50]}...")
        
    # Print importance scores for all events
    print("\nImportance scores (LBO-specific):")
    for event in events:
        importance = condenser._calculate_importance(event)
        print(f"Event {event.id}: {importance:.2f} - {event.content[:50]}...")

def demonstrate_llm_summarizing_condenser():
    """Demonstrate the LLMSummarizingCondenser."""
    print("\n=== LLMSummarizingCondenser Demonstration ===")
    print("Note: This requires an OpenAI API key to run.")
    
    # Check if API key is available
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OpenAI API key not found. Skipping LLM-based condenser demonstration.")
        return
    
    # Create sample events
    events = create_sample_events()
    print(f"Original event count: {len(events)}")
    
    try:
        # Create condenser
        condenser = LLMSummarizingCondenser(
            max_size=10,
            keep_first=2,
            keep_last=3,
            api_key=api_key,
            model="gpt-4o"
        )
        
        # Condense events
        condensed_events = condenser.condense(events)
        print(f"Condensed event count: {len(condensed_events)}")
        
        # Print preserved events
        print("\nPreserved events:")
        for i, event in enumerate(condensed_events):
            if "type" in event.metadata and event.metadata["type"] == "summary":
                print(f"Event {i+1} (ID: {event.id}): [SUMMARY EVENT]")
                print(f"Summary content: {event.content}")
            else:
                print(f"Event {i+1} (ID: {event.id}): {event.role} - {event.content[:50]}...")
    
    except Exception as e:
        print(f"Error demonstrating LLM summarizing condenser: {e}")

def demonstrate_financial_llm_condenser():
    """Demonstrate the FinancialLLMSummarizingCondenser."""
    print("\n=== FinancialLLMSummarizingCondenser Demonstration ===")
    print("Note: This requires an OpenAI API key to run.")
    
    # Check if API key is available
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OpenAI API key not found. Skipping LLM-based condenser demonstration.")
        return
    
    # Create sample events
    events = create_sample_events()
    print(f"Original event count: {len(events)}")
    
    try:
        # Create condenser
        condenser = FinancialLLMSummarizingCondenser(
            domain="lbo",
            max_size=10,
            keep_first=2,
            keep_last=3,
            api_key=api_key,
            model="gpt-4o"
        )
        
        # Condense events
        condensed_events = condenser.condense(events)
        print(f"Condensed event count: {len(condensed_events)}")
        
        # Print preserved events
        print("\nPreserved events:")
        for i, event in enumerate(condensed_events):
            if "type" in event.metadata and event.metadata["type"] == "summary":
                print(f"Event {i+1} (ID: {event.id}): [LBO-SPECIFIC SUMMARY EVENT]")
                print(f"Summary content: {event.content}")
            else:
                print(f"Event {i+1} (ID: {event.id}): {event.role} - {event.content[:50]}...")
    
    except Exception as e:
        print(f"Error demonstrating financial LLM summarizing condenser: {e}")

def main():
    """Run the condenser examples."""
    print("Cori RAG++ System - Condenser Examples")
    print("======================================")
    
    # Demonstrate different condensers
    demonstrate_recent_events_condenser()
    demonstrate_financial_domain_condenser()
    demonstrate_lbo_modeling_condenser()
    
    # LLM-based condensers (require API key)
    demonstrate_llm_summarizing_condenser()
    demonstrate_financial_llm_condenser()

if __name__ == "__main__":
    main()
