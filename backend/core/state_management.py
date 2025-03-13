"""
State management system for Cori backend.
Provides a state machine for tracking agent status.
"""
from typing import Dict, List, Any, Optional, Set
from enum import Enum
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentState(str, Enum):
    """Enum for agent states."""
    IDLE = "idle"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    ERROR = "error"
    AWAITING_INPUT = "awaiting_input"

class StateTransitionError(Exception):
    """Exception raised for invalid state transitions."""
    pass

class AgentStateController:
    """
    Controller for managing agent state transitions.
    Enforces valid state transitions and tracks state history.
    """
    def __init__(self, initial_state: AgentState = AgentState.IDLE):
        # Define allowed transitions between states
        self._allowed_transitions: Dict[AgentState, Set[AgentState]] = {
            AgentState.IDLE: {AgentState.ANALYZING, AgentState.ERROR},
            AgentState.ANALYZING: {AgentState.PLANNING, AgentState.ERROR, AgentState.AWAITING_INPUT},
            AgentState.PLANNING: {AgentState.EXECUTING, AgentState.ERROR, AgentState.AWAITING_INPUT},
            AgentState.EXECUTING: {AgentState.REVIEWING, AgentState.ERROR, AgentState.AWAITING_INPUT},
            AgentState.REVIEWING: {AgentState.IDLE, AgentState.ERROR, AgentState.AWAITING_INPUT},
            AgentState.ERROR: {AgentState.IDLE},
            AgentState.AWAITING_INPUT: {
                AgentState.ANALYZING, AgentState.PLANNING, 
                AgentState.EXECUTING, AgentState.REVIEWING
            }
        }
        
        self._current_state = initial_state
        self._state_history: List[Dict[str, Any]] = [
            {"state": initial_state, "timestamp": datetime.now().isoformat()}
        ]
        self._metadata: Dict[str, Any] = {}
        
        logger.info(f"AgentStateController initialized with state: {initial_state}")
    
    @property
    def current_state(self) -> AgentState:
        """Get the current agent state."""
        return self._current_state
    
    @property
    def state_history(self) -> List[Dict[str, Any]]:
        """Get the state transition history."""
        return self._state_history.copy()
    
    def can_transition_to(self, new_state: AgentState) -> bool:
        """
        Check if a transition to the new state is allowed.
        
        Args:
            new_state: The state to transition to
            
        Returns:
            bool: True if the transition is allowed, False otherwise
        """
        return new_state in self._allowed_transitions.get(self._current_state, set())
    
    def set_state(self, new_state: AgentState, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Attempt to transition to a new state.
        
        Args:
            new_state: The state to transition to
            metadata: Optional metadata to associate with this state
            
        Returns:
            bool: True if the transition was successful
            
        Raises:
            StateTransitionError: If the transition is not allowed
        """
        if not self.can_transition_to(new_state):
            error_msg = f"Cannot transition from {self._current_state} to {new_state}"
            logger.error(error_msg)
            raise StateTransitionError(error_msg)
        
        # Update current state
        self._current_state = new_state
        
        # Update metadata
        if metadata:
            self._metadata.update(metadata)
        
        # Record in history
        self._state_history.append({
            "state": new_state,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
        
        logger.info(f"State changed to: {new_state}")
        return True
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get the current metadata."""
        return self._metadata.copy()
    
    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Update the metadata without changing state.
        
        Args:
            metadata: Metadata to update
        """
        self._metadata.update(metadata)
        logger.debug(f"Metadata updated: {metadata}")
    
    def clear_history(self, keep_current: bool = True) -> None:
        """
        Clear the state history.
        
        Args:
            keep_current: Whether to keep the current state in history
        """
        if keep_current:
            self._state_history = [self._state_history[-1]]
        else:
            self._state_history = []
        logger.info("State history cleared")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert controller state to dictionary for serialization."""
        return {
            "current_state": self._current_state,
            "state_history": self._state_history,
            "metadata": self._metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentStateController':
        """Create a controller instance from a dictionary."""
        controller = cls(initial_state=data["current_state"])
        controller._state_history = data["state_history"]
        controller._metadata = data["metadata"]
        return controller
    
    def save_to_file(self, file_path: str) -> None:
        """
        Save controller state to a file.
        
        Args:
            file_path: Path to save the state to
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            logger.info(f"State saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Load controller state from a file.
        
        Args:
            file_path: Path to load the state from
            
        Returns:
            bool: True if successfully loaded, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self._current_state = data["current_state"]
            self._state_history = data["state_history"]
            self._metadata = data["metadata"]
            
            logger.info(f"State loaded from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return False

# Create a global state controller instance
state_controller = AgentStateController()
