"""
Condenser module for Cori RAG++ system.
Condensers are responsible for reducing the size of the event history
while preserving important information.
"""

from .condenser import Condenser, RollingCondenser, RecentEventsCondenser
from .impl.financial_domain_condensers import (
    FinancialDomainCondenser,
    LBOModelingCondenser,
    MAModelingCondenser
)
from .impl.llm_summarizing_condenser import (
    LLMSummarizingCondenser,
    FinancialLLMSummarizingCondenser
)
from .impl.llm_attention_condenser import (
    LLMAttentionCondenser,
    FinancialLLMAttentionCondenser
)

__all__ = [
    'Condenser',
    'RollingCondenser',
    'RecentEventsCondenser',
    'FinancialDomainCondenser',
    'LBOModelingCondenser',
    'MAModelingCondenser',
    'LLMSummarizingCondenser',
    'FinancialLLMSummarizingCondenser',
    'LLMAttentionCondenser',
    'FinancialLLMAttentionCondenser'
]
