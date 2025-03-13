from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field

class UserPreference(BaseModel):
    """Base class for user preferences in Cori."""
    id: str
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    preference_type: Literal["modeling", "analysis", "visualization", "workflow"]
    domain: Optional[Literal["lbo", "ma", "debt", "private_lending", "general"]] = "general"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert preference to dictionary for serialization."""
        return self.model_dump()

class ModelingPreference(UserPreference):
    """User preferences for financial modeling approaches."""
    preference_type: Literal["modeling", "analysis", "visualization", "workflow"] = "modeling"
    approach: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    description: str
    
    class Config:
        schema_extra = {
            "example": {
                "id": "pref-123",
                "user_id": "user-456",
                "domain": "lbo",
                "approach": "bottom-up",
                "parameters": {
                    "exit_multiple": 8.0,
                    "debt_to_ebitda": 6.0
                },
                "description": "Prefer bottom-up LBO modeling with conservative exit multiples"
            }
        }

class AnalysisPreference(UserPreference):
    """User preferences for financial analysis methods."""
    preference_type: Literal["modeling", "analysis", "visualization", "workflow"] = "analysis"
    method: str
    metrics: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    description: str
    
    class Config:
        schema_extra = {
            "example": {
                "id": "pref-789",
                "user_id": "user-456",
                "domain": "ma",
                "method": "accretion-dilution",
                "metrics": ["eps", "fcf"],
                "parameters": {
                    "synergy_ramp": "gradual",
                    "tax_rate": 0.21
                },
                "description": "Prefer accretion-dilution analysis with gradual synergy ramp"
            }
        }

class VisualizationPreference(UserPreference):
    """User preferences for financial visualization styles."""
    preference_type: Literal["modeling", "analysis", "visualization", "workflow"] = "visualization"
    chart_type: str
    color_scheme: Optional[str] = None
    formatting: Dict[str, Any] = Field(default_factory=dict)
    description: str
    
    class Config:
        schema_extra = {
            "example": {
                "id": "pref-101",
                "user_id": "user-456",
                "domain": "general",
                "chart_type": "waterfall",
                "color_scheme": "blue-green",
                "formatting": {
                    "decimal_places": 1,
                    "show_values": True
                },
                "description": "Prefer waterfall charts for bridge analysis with blue-green color scheme"
            }
        }

class WorkflowPreference(UserPreference):
    """User preferences for financial modeling workflow."""
    preference_type: Literal["modeling", "analysis", "visualization", "workflow"] = "workflow"
    workflow_steps: List[str] = Field(default_factory=list)
    automation_level: str
    description: str
    
    class Config:
        schema_extra = {
            "example": {
                "id": "pref-202",
                "user_id": "user-456",
                "domain": "debt",
                "workflow_steps": ["sizing", "terms", "amortization", "covenants"],
                "automation_level": "high",
                "description": "Prefer automated debt schedule creation with covenant analysis"
            }
        }
