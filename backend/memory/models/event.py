"""
Event model for Cori RAG++ system.
Events represent interactions between the user and the system.
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import uuid
import json

class Event:
    """
    Event class representing an interaction between the user and the system.
    Events are the basic unit of conversation memory.
    """
    
    def __init__(
        self,
        id: Optional[str] = None,
        role: str = "user",
        content: str = "",
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an event.
        
        Args:
            id: Unique identifier for the event
            role: Role of the event sender (user, assistant, system)
            content: Content of the event
            timestamp: Timestamp of the event
            metadata: Additional metadata for the event
        """
        self.id = id or str(uuid.uuid4())
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.utcnow().isoformat() + "Z"
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dictionary representation of the event
        """
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """
        Convert the event to a JSON string.
        
        Returns:
            JSON string representation of the event
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """
        Create an event from a dictionary.
        
        Args:
            data: Dictionary representation of the event
            
        Returns:
            Event object
        """
        return cls(
            id=data.get("id"),
            role=data.get("role", "user"),
            content=data.get("content", ""),
            timestamp=data.get("timestamp"),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Event':
        """
        Create an event from a JSON string.
        
        Args:
            json_str: JSON string representation of the event
            
        Returns:
            Event object
        """
        return cls.from_dict(json.loads(json_str))
    
    def __eq__(self, other: object) -> bool:
        """
        Check if two events are equal.
        
        Args:
            other: Other event to compare with
            
        Returns:
            True if the events are equal, False otherwise
        """
        if not isinstance(other, Event):
            return False
        
        return (
            self.id == other.id and
            self.role == other.role and
            self.content == other.content and
            self.timestamp == other.timestamp and
            self.metadata == other.metadata
        )
    
    def __repr__(self) -> str:
        """
        Get a string representation of the event.
        
        Returns:
            String representation of the event
        """
        return f"Event(id={self.id}, role={self.role}, content={self.content[:20]}..., timestamp={self.timestamp})"
