"""
State management for Cori backend.
Provides a state controller for managing agent state transitions.
"""

from typing import Dict, List, Any, Optional, Union
import threading
import logging
import uuid
from datetime import datetime
from enum import Enum

# Import event system
from backend.core.event_system import event_bus, Event

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(Enum):
    """
    Enum for agent states.
    Represents the possible states of the agent.
    """
    IDLE = "idle"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    ERROR = "error"
    AWAITING_INPUT = "awaiting_input"

class AgentStateController:
    """
    State controller for managing agent state transitions.
    Provides thread-safe operations for concurrent access.
    """
    
    def __init__(self):
        """Initialize the state controller."""
        self.current_state = AgentState.IDLE
        self.previous_state = None
        self.state_history = []
        self.metadata = {}
        self._lock = threading.Lock()
        
        logger.info("AgentStateController initialized")
    
    def get_current_state(self) -> AgentState:
        """
        Get the current state.
        
        Returns:
            Current state
        """
        with self._lock:
            return self.current_state
    
    def get_previous_state(self) -> Optional[AgentState]:
        """
        Get the previous state.
        
        Returns:
            Previous state or None if there is no previous state
        """
        with self._lock:
            return self.previous_state
    
    def get_state_history(self) -> List[Dict[str, Any]]:
        """
        Get the state history.
        
        Returns:
            State history
        """
        with self._lock:
            return self.state_history.copy()
    
    def transition_to(self, state: AgentState, reason: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Transition to a new state.
        
        Args:
            state: New state to transition to
            reason: Reason for the transition
            metadata: Optional metadata for the transition
        """
        with self._lock:
            # Check if the state is already the current state
            if state == self.current_state:
                logger.warning(f"Already in state {state.value}")
                return
            
            # Update state
            self.previous_state = self.current_state
            self.current_state = state
            
            # Update metadata
            if metadata:
                self.metadata.update(metadata)
            
            # Create state transition record
            transition = {
                "from_state": self.previous_state.value if self.previous_state else None,
                "to_state": state.value,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # Add transition to history
            self.state_history.append(transition)
            
            # Publish state transition event
            event_bus.publish(Event(
                event_type="agent_state_changed",
                data=transition
            ))
            
            logger.info(f"Transitioned from {self.previous_state.value if self.previous_state else 'None'} to {state.value}: {reason}")
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the current state.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        with self._lock:
            self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the current state.
        
        Args:
            key: Metadata key
            default: Default value if key is not found
            
        Returns:
            Metadata value
        """
        with self._lock:
            return self.metadata.get(key, default)
    
    def clear_metadata(self) -> None:
        """Clear metadata for the current state."""
        with self._lock:
            self.metadata = {}
    
    def is_in_state(self, state: AgentState) -> bool:
        """
        Check if the agent is in a specific state.
        
        Args:
            state: State to check
            
        Returns:
            True if the agent is in the specified state, False otherwise
        """
        with self._lock:
            return self.current_state == state
    
    def reset(self) -> None:
        """Reset the state controller."""
        with self._lock:
            self.current_state = AgentState.IDLE
            self.previous_state = None
            self.state_history = []
            self.metadata = {}
            
            logger.info("AgentStateController reset")
