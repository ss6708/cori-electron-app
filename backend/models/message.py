from typing import Literal, Optional, List, Dict, Any
from datetime import datetime
import json

class Message:
    """Base message class for chat interactions."""
    def __init__(
        self, 
        role: Literal["user", "system", "assistant"], 
        content: str,
        timestamp: Optional[str] = None,
        displayed: bool = True,
        thinking_time: Optional[int] = None
    ):
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now().isoformat()
        self.displayed = displayed
        self.thinking_time = thinking_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for JSON serialization."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "displayed": self.displayed,
            **({"thinkingTime": self.thinking_time} if self.thinking_time is not None else {})
        }
    
    def to_openai_format(self) -> Dict[str, str]:
        """Convert to OpenAI API message format."""
        return {
            "role": self.role,
            "content": self.content
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create a Message instance from a dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=data.get("timestamp"),
            displayed=data.get("displayed", True),
            thinking_time=data.get("thinkingTime")
        )
