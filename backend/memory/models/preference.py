"""
Preference model for Cori RAG++ system.
Preferences represent user-specific settings and preferences.
"""

from typing import Dict, Any, Optional
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
