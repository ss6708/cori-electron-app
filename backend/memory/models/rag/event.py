"""
RAG-specific Event models for Cori RAG++ system.
These models extend the base Event model with RAG-specific functionality.
"""

from abc import ABC
from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field

class Event(BaseModel):
    """Base class for all RAG events in Cori."""
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

class SystemMessageEvent(FinancialModelingEvent):
    """Event for system messages."""
    content: str
    
    def to_message(self) -> Dict[str, Any]:
        """Convert to message format for LLM."""
        return {
            "role": "system",
            "content": self.content
        }

class ToolCallEvent(FinancialModelingEvent):
    """Event for tool calls."""
    tool_name: str
    input_parameters: Dict[str, Any] = Field(default_factory=dict)
    output: Optional[Dict[str, Any]] = None
    
    def to_message(self) -> Dict[str, Any]:
        """Convert to message format for LLM."""
        return {
            "role": "tool",
            "content": str(self.output),
            "tool_call_id": self.id,
            "name": self.tool_name
        }
