"""
Preference model for Cori RAG++ system.
Preferences represent user-specific settings and preferences.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import json

class Preference:
    """
    Preference class representing a user-specific setting or preference.
    Preferences are stored in the user preference store.
    """
    
    def __init__(
        self,
        id: Optional[str] = None,
        user_id: str = "",
        domain: str = "general",
        key: str = "",
        value: Any = None,
        description: str = "",
        timestamp: Optional[str] = None
    ):
        """
        Initialize a preference.
        
        Args:
            id: Unique identifier for the preference
            user_id: ID of the user who owns the preference
            domain: Domain of the preference (e.g., lbo, ma, debt, private_lending, general)
            key: Key of the preference
            value: Value of the preference
            description: Description of the preference
            timestamp: Timestamp of the preference
        """
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.domain = domain
        self.key = key
        self.value = value
        self.description = description
        self.timestamp = timestamp or datetime.utcnow().isoformat() + "Z"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the preference to a dictionary.
        
        Returns:
            Dictionary representation of the preference
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "domain": self.domain,
            "key": self.key,
            "value": self.value,
            "description": self.description,
            "timestamp": self.timestamp
        }
    
    def to_json(self) -> str:
        """
        Convert the preference to a JSON string.
        
        Returns:
            JSON string representation of the preference
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Preference':
        """
        Create a preference from a dictionary.
        
        Args:
            data: Dictionary representation of the preference
            
        Returns:
            Preference object
        """
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id", ""),
            domain=data.get("domain", "general"),
            key=data.get("key", ""),
            value=data.get("value"),
            description=data.get("description", ""),
            timestamp=data.get("timestamp")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Preference':
        """
        Create a preference from a JSON string.
        
        Args:
            json_str: JSON string representation of the preference
            
        Returns:
            Preference object
        """
        return cls.from_dict(json.loads(json_str))
    
    def __eq__(self, other: object) -> bool:
        """
        Check if two preferences are equal.
        
        Args:
            other: Other preference to compare with
            
        Returns:
            True if the preferences are equal, False otherwise
        """
        if not isinstance(other, Preference):
            return False
        
        return (
            self.id == other.id and
            self.user_id == other.user_id and
            self.domain == other.domain and
            self.key == other.key and
            self.value == other.value and
            self.description == other.description and
            self.timestamp == other.timestamp
        )
    
    def __repr__(self) -> str:
        """
        Get a string representation of the preference.
        
        Returns:
            String representation of the preference
        """
        return f"Preference(id={self.id}, user_id={self.user_id}, domain={self.domain}, key={self.key}, value={self.value})"


class UserPreference(Preference):
    """
    User preference class representing a user-specific setting or preference.
    Base class for all user preferences.
    """
    
    def __init__(
        self,
        id: Optional[str] = None,
        user_id: str = "",
        domain: str = "general",
        key: str = "",
        value: Any = None,
        description: str = "",
        timestamp: Optional[str] = None,
        preference_type: str = "general"
    ):
        """
        Initialize a user preference.
        
        Args:
            id: Unique identifier for the preference
            user_id: ID of the user who owns the preference
            domain: Domain of the preference
            key: Key of the preference
            value: Value of the preference
            description: Description of the preference
            timestamp: Timestamp of the preference
            preference_type: Type of the preference
        """
        super().__init__(id, user_id, domain, key, value, description, timestamp)
        self.preference_type = preference_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the preference to a dictionary."""
        data = super().to_dict()
        data.update({
            "preference_type": self.preference_type
        })
        return data


class ModelingPreference(UserPreference):
    """
    Modeling preference class representing preferences for financial modeling.
    Used for storing modeling approaches and parameters.
    """
    
    def __init__(
        self,
        id: Optional[str] = None,
        user_id: str = "",
        domain: str = "general",
        description: str = "",
        timestamp: Optional[str] = None,
        approach: str = "",
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a modeling preference.
        
        Args:
            id: Unique identifier for the preference
            user_id: ID of the user who owns the preference
            domain: Domain of the preference
            description: Description of the preference
            timestamp: Timestamp of the preference
            approach: Modeling approach
            parameters: Modeling parameters
        """
        super().__init__(id, user_id, domain, "modeling", parameters or {}, description, timestamp, "modeling")
        self.approach = approach
        self.parameters = parameters or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the preference to a dictionary."""
        data = super().to_dict()
        data.update({
            "preference_type": "modeling",
            "approach": self.approach,
            "parameters": self.parameters
        })
        return data


class AnalysisPreference(UserPreference):
    """
    Analysis preference class representing preferences for financial analysis.
    Used for storing analysis methods, metrics, and parameters.
    """
    
    def __init__(
        self,
        id: Optional[str] = None,
        user_id: str = "",
        domain: str = "general",
        description: str = "",
        timestamp: Optional[str] = None,
        method: str = "",
        metrics: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an analysis preference.
        
        Args:
            id: Unique identifier for the preference
            user_id: ID of the user who owns the preference
            domain: Domain of the preference
            description: Description of the preference
            timestamp: Timestamp of the preference
            method: Analysis method
            metrics: Analysis metrics
            parameters: Analysis parameters
        """
        super().__init__(id, user_id, domain, "analysis", parameters or {}, description, timestamp, "analysis")
        self.method = method
        self.metrics = metrics or []
        self.parameters = parameters or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the preference to a dictionary."""
        data = super().to_dict()
        data.update({
            "preference_type": "analysis",
            "method": self.method,
            "metrics": self.metrics,
            "parameters": self.parameters
        })
        return data


class VisualizationPreference(UserPreference):
    """
    Visualization preference class representing preferences for data visualization.
    Used for storing visualization types, styles, and parameters.
    """
    
    def __init__(
        self,
        id: Optional[str] = None,
        user_id: str = "",
        domain: str = "general",
        description: str = "",
        timestamp: Optional[str] = None,
        chart_type: str = "",
        style: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a visualization preference.
        
        Args:
            id: Unique identifier for the preference
            user_id: ID of the user who owns the preference
            domain: Domain of the preference
            description: Description of the preference
            timestamp: Timestamp of the preference
            chart_type: Type of chart or visualization
            style: Visualization style settings
            parameters: Visualization parameters
        """
        super().__init__(id, user_id, domain, "visualization", parameters or {}, description, timestamp, "visualization")
        self.chart_type = chart_type
        self.style = style or {}
        self.parameters = parameters or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the preference to a dictionary."""
        data = super().to_dict()
        data.update({
            "preference_type": "visualization",
            "chart_type": self.chart_type,
            "style": self.style,
            "parameters": self.parameters
        })
        return data


class WorkflowPreference(UserPreference):
    """
    Workflow preference class representing preferences for financial workflows.
    Used for storing workflow steps, configurations, and parameters.
    """
    
    def __init__(
        self,
        id: Optional[str] = None,
        user_id: str = "",
        domain: str = "general",
        description: str = "",
        timestamp: Optional[str] = None,
        workflow_type: str = "",
        steps: Optional[List[Dict[str, Any]]] = None,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a workflow preference.
        
        Args:
            id: Unique identifier for the preference
            user_id: ID of the user who owns the preference
            domain: Domain of the preference
            description: Description of the preference
            timestamp: Timestamp of the preference
            workflow_type: Type of workflow
            steps: Workflow steps
            parameters: Workflow parameters
        """
        super().__init__(id, user_id, domain, "workflow", parameters or {}, description, timestamp, "workflow")
        self.workflow_type = workflow_type
        self.steps = steps or []
        self.parameters = parameters or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the preference to a dictionary."""
        data = super().to_dict()
        data.update({
            "preference_type": "workflow",
            "workflow_type": self.workflow_type,
            "steps": self.steps,
            "parameters": self.parameters
        })
        return data
