"""
RAG-specific preference models for Cori RAG++ system.
These models extend the base preference model with RAG-specific functionality.
"""

from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field

class UserPreference(BaseModel):
    """User preference model for RAG system."""
    user_id: str
    preference_id: str
    category: str
    name: str
    value: Any
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert preference to dictionary for serialization."""
        return self.model_dump()

class MemoryPreference(UserPreference):
    """Memory-specific user preference."""
    category: Literal["memory"] = "memory"

class ConversationMemoryPreference(MemoryPreference):
    """Conversation memory preference."""
    name: Literal["max_events", "condenser_type", "auto_condense"] 
    
class LongTermMemoryPreference(MemoryPreference):
    """Long-term memory preference."""
    name: Literal["enabled", "retrieval_count", "similarity_threshold"]

class DomainPreference(UserPreference):
    """Domain-specific user preference."""
    category: Literal["domain"] = "domain"
    domain: Literal["lbo", "ma", "debt", "private_lending", "general"] = "general"

class ModelPreference(UserPreference):
    """Model-specific user preference."""
    category: Literal["model"] = "model"
    name: Literal["temperature", "max_tokens", "model_name"]
