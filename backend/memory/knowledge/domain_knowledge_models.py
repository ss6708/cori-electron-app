"""
Domain-specific knowledge models for financial domains.
"""

from typing import Dict, List, Optional, Any, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class KnowledgeItem(BaseModel):
    """Base class for knowledge items in the financial knowledge base."""
    id: str
    title: str
    content: str
    domain: Literal["lbo", "ma", "debt", "private_lending", "general"]
    topic: str
    subtopics: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    source: str = "manual"
    extracted: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert knowledge item to dictionary for serialization."""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeItem":
        """Create knowledge item from dictionary."""
        return cls(**data)

class LBOKnowledgeItem(KnowledgeItem):
    """Knowledge item for LBO domain."""
    domain: Literal["lbo", "ma", "debt", "private_lending", "general"] = "lbo"
    
    class Config:
        schema_extra = {
            "example": {
                "id": "lbo-123",
                "title": "LBO Debt Sizing Guidelines",
                "content": "LBO Debt Sizing Guidelines:\n\n1. Total Leverage Metrics...",
                "topic": "debt_sizing",
                "subtopics": ["leverage", "tranches", "coverage_ratios"],
                "source": "manual",
                "extracted": False
            }
        }

class MAKnowledgeItem(KnowledgeItem):
    """Knowledge item for M&A domain."""
    domain: Literal["lbo", "ma", "debt", "private_lending", "general"] = "ma"
    
    class Config:
        schema_extra = {
            "example": {
                "id": "ma-123",
                "title": "M&A Valuation Methodologies",
                "content": "M&A Valuation Methodologies:\n\n1. Comparable Company Analysis...",
                "topic": "valuation_methodologies",
                "subtopics": ["comps", "precedents", "dcf"],
                "source": "manual",
                "extracted": False
            }
        }

class DebtKnowledgeItem(KnowledgeItem):
    """Knowledge item for debt modeling domain."""
    domain: Literal["lbo", "ma", "debt", "private_lending", "general"] = "debt"
    
    class Config:
        schema_extra = {
            "example": {
                "id": "debt-123",
                "title": "Debt Covenant Analysis Framework",
                "content": "Debt Covenant Analysis Framework:\n\n1. Leverage Ratio Covenant...",
                "topic": "covenant_analysis",
                "subtopics": ["leverage_ratio", "interest_coverage", "fixed_charge"],
                "source": "manual",
                "extracted": False
            }
        }

class PrivateLendingKnowledgeItem(KnowledgeItem):
    """Knowledge item for private lending domain."""
    domain: Literal["lbo", "ma", "debt", "private_lending", "general"] = "private_lending"
    
    class Config:
        schema_extra = {
            "example": {
                "id": "pl-123",
                "title": "Private Lending Risk Assessment Framework",
                "content": "Private Lending Risk Assessment Framework:\n\n1. Credit Risk Analysis...",
                "topic": "risk_assessment",
                "subtopics": ["credit_risk", "structural_mitigants", "portfolio_risk"],
                "source": "manual",
                "extracted": False
            }
        }
