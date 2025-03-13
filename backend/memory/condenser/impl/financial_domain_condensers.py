from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime

from ...models.event import Event, CondensationEvent
from ..condenser import FinancialDomainCondenser
from .llm_summarizing_condenser import LLMSummarizingCondenser

class MAModelingCondenser(FinancialDomainCondenser):
    """
    Condenser specialized for M&A modeling contexts.
    Preserves valuation methodology, deal structure, and synergies.
    """
    
    def identify_critical_events(self, events: List[Event]) -> List[Event]:
        """
        Identify critical M&A modeling events to preserve.
        
        Args:
            events: List of events to analyze
            
        Returns:
            List of critical events to preserve
        """
        # Group events by type
        valuation_events = []
        synergies_events = []
        accretion_dilution_events = []
        deal_structure_events = []
        
        for event in events:
            if hasattr(event, 'domain') and getattr(event, 'domain') == 'ma':
                if hasattr(event, 'action_type'):
                    action_type = getattr(event, 'action_type')
                    if action_type == 'valuation':
                        valuation_events.append(event)
                    elif action_type == 'synergies':
                        synergies_events.append(event)
                    elif action_type == 'accretion_dilution':
                        accretion_dilution_events.append(event)
                    elif action_type == 'deal_structure':
                        deal_structure_events.append(event)
        
        # Keep the most recent of each critical event type
        critical_events = []
        if valuation_events:
            critical_events.append(valuation_events[-1])
        if synergies_events:
            critical_events.append(synergies_events[-1])
        if accretion_dilution_events:
            critical_events.append(accretion_dilution_events[-1])
        if deal_structure_events:
            critical_events.append(deal_structure_events[-1])
        
        return critical_events

class DebtModelingCondenser(FinancialDomainCondenser):
    """
    Condenser specialized for debt modeling contexts.
    Preserves debt sizing, covenant analysis, and amortization schedules.
    """
    
    def identify_critical_events(self, events: List[Event]) -> List[Event]:
        """
        Identify critical debt modeling events to preserve.
        
        Args:
            events: List of events to analyze
            
        Returns:
            List of critical events to preserve
        """
        # Group events by type
        debt_sizing_events = []
        covenant_analysis_events = []
        amortization_events = []
        refinancing_events = []
        
        for event in events:
            if hasattr(event, 'domain') and getattr(event, 'domain') == 'debt':
                if hasattr(event, 'action_type'):
                    action_type = getattr(event, 'action_type')
                    if action_type == 'debt_sizing':
                        debt_sizing_events.append(event)
                    elif action_type == 'covenant_analysis':
                        covenant_analysis_events.append(event)
                    elif action_type == 'amortization':
                        amortization_events.append(event)
                    elif action_type == 'refinancing':
                        refinancing_events.append(event)
        
        # Keep the most recent of each critical event type
        critical_events = []
        if debt_sizing_events:
            critical_events.append(debt_sizing_events[-1])
        if covenant_analysis_events:
            critical_events.append(covenant_analysis_events[-1])
        if amortization_events:
            critical_events.append(amortization_events[-1])
        if refinancing_events:
            critical_events.append(refinancing_events[-1])
        
        return critical_events

class PrivateLendingCondenser(FinancialDomainCondenser):
    """
    Condenser specialized for private lending contexts.
    Preserves loan terms, security analysis, and returns calculation.
    """
    
    def identify_critical_events(self, events: List[Event]) -> List[Event]:
        """
        Identify critical private lending events to preserve.
        
        Args:
            events: List of events to analyze
            
        Returns:
            List of critical events to preserve
        """
        # Group events by type
        loan_terms_events = []
        security_analysis_events = []
        returns_calculation_events = []
        risk_assessment_events = []
        
        for event in events:
            if hasattr(event, 'domain') and getattr(event, 'domain') == 'private_lending':
                if hasattr(event, 'action_type'):
                    action_type = getattr(event, 'action_type')
                    if action_type == 'loan_terms':
                        loan_terms_events.append(event)
                    elif action_type == 'security_analysis':
                        security_analysis_events.append(event)
                    elif action_type == 'returns_calculation':
                        returns_calculation_events.append(event)
                    elif action_type == 'risk_assessment':
                        risk_assessment_events.append(event)
        
        # Keep the most recent of each critical event type
        critical_events = []
        if loan_terms_events:
            critical_events.append(loan_terms_events[-1])
        if security_analysis_events:
            critical_events.append(security_analysis_events[-1])
        if returns_calculation_events:
            critical_events.append(returns_calculation_events[-1])
        if risk_assessment_events:
            critical_events.append(risk_assessment_events[-1])
        
        return critical_events

class FinancialLLMSummarizingCondenser(LLMSummarizingCondenser):
    """
    A specialized LLM summarizing condenser for financial modeling contexts.
    Creates concise summaries of financial modeling history.
    """
    
    def _default_summary_prompt(self) -> str:
        """
        Get the default summary prompt template for financial modeling.
        
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
