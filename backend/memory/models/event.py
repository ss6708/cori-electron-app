from abc import ABC
from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field

class Event(BaseModel):
    """Base class for all events in Cori."""
    id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: str
    session_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return self.model_dump()
    
    def to_document(self) -> Dict[str, Any]:
        """Convert event to document format for vector storage."""
        doc = self.to_dict()
        # Add any additional processing for vector storage
        return doc

class FinancialModelingEvent(Event):
    """Base class for all financial modeling events."""
    domain: Literal["lbo", "ma", "debt", "private_lending", "general"] = "general"
    context: Dict[str, Any] = Field(default_factory=dict)

class UserMessageEvent(FinancialModelingEvent):
    """Event for user messages."""
    content: str
    
    def to_message(self) -> Dict[str, Any]:
        """Convert to message format for LLM."""
        return {
            "role": "user",
            "content": self.content
        }

class AssistantMessageEvent(FinancialModelingEvent):
    """Event for assistant messages."""
    content: str
    thinking_time: Optional[int] = None
    
    def to_message(self) -> Dict[str, Any]:
        """Convert to message format for LLM."""
        return {
            "role": "assistant",
            "content": self.content
        }

class LBOModelingEvent(FinancialModelingEvent):
    """Events related to LBO modeling."""
    domain: Literal["lbo", "ma", "debt", "private_lending", "general"] = "lbo"
    action_type: Literal["transaction_structure", "debt_sizing", "exit_analysis", "operational_projections"]
    parameters: Dict[str, Any] = Field(default_factory=dict)

class MAModelingEvent(FinancialModelingEvent):
    """Events related to M&A modeling."""
    domain: Literal["lbo", "ma", "debt", "private_lending", "general"] = "ma"
    action_type: Literal["valuation", "synergies", "accretion_dilution", "deal_structure"]
    parameters: Dict[str, Any] = Field(default_factory=dict)

class DebtModelingEvent(FinancialModelingEvent):
    """Events related to debt modeling."""
    domain: Literal["lbo", "ma", "debt", "private_lending", "general"] = "debt"
    action_type: Literal["debt_sizing", "covenant_analysis", "amortization", "refinancing"]
    parameters: Dict[str, Any] = Field(default_factory=dict)

class PrivateLendingEvent(FinancialModelingEvent):
    """Events related to private lending."""
    domain: Literal["lbo", "ma", "debt", "private_lending", "general"] = "private_lending"
    action_type: Literal["loan_terms", "security_analysis", "returns_calculation", "risk_assessment"]
    parameters: Dict[str, Any] = Field(default_factory=dict)

class ExcelOperationEvent(FinancialModelingEvent):
    """Events related to Excel operations."""
    operation_type: Literal["set_formula", "create_table", "format_cells", "create_worksheet", "create_chart"]
    worksheet: str
    range_reference: Optional[str] = None
    content: Optional[str] = None
    formatting: Optional[Dict[str, Any]] = None
    domain_context: Literal["lbo", "ma", "debt", "private_lending", "general"] = "general"

class UserPreferenceEvent(FinancialModelingEvent):
    """Events capturing user preferences."""
    preference_type: Literal["modeling", "analysis", "visualization", "workflow"]
    preference_value: Any
    preference_context: str
    domain_specific: bool = False
    domain: Optional[Literal["lbo", "ma", "debt", "private_lending", "general"]] = None

class CondensationEvent(Event):
    """Event representing a condensation of previous events."""
    content: str
    original_event_ids: List[str]
    domain: Optional[Literal["lbo", "ma", "debt", "private_lending", "general"]] = None
    
    def to_message(self) -> Dict[str, Any]:
        """Convert to message format for LLM."""
        return {
            "role": "system",
            "content": self.content
        }
