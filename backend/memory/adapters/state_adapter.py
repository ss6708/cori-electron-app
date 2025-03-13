"""
State adapter for Cori RAG++ system.
Provides adapters for integrating RAG++ components with the core state management system.
"""

from typing import Dict, List, Any, Optional, Union, Callable
import threading
import logging

# Import core classes
from backend.core.state_management import AgentStateController, AgentState
from backend.core.event_system import event_bus, Event as CoreEvent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StateAwareComponent:
    """
    Base class for state-aware RAG++ components.
    Provides methods for interacting with the core state management system.
    """
    
    def __init__(self, state_controller: AgentStateController):
        """
        Initialize the state-aware component.
        
        Args:
            state_controller: Core AgentStateController instance
        """
        self.state_controller = state_controller
        self._lock = threading.Lock()
        
        # Subscribe to state transition events
        event_bus.subscribe("agent_state_changed", self._handle_state_transition)
        
        logger.info(f"StateAwareComponent initialized")
    
    def _handle_state_transition(self, event: CoreEvent) -> None:
        """
        Handle state transition events.
        
        Args:
            event: Core Event representing a state transition
        """
        if event.event_type != "agent_state_changed" or not isinstance(event.data, dict):
            return
        
        data = event.data
        from_state = data.get("from_state")
        to_state = data.get("to_state")
        reason = data.get("reason", "")
        
        logger.debug(f"State transition: {from_state} -> {to_state} ({reason})")
        
        # Call the appropriate handler method based on the new state
        if to_state == AgentState.ANALYZING.value:
            self.on_analyzing_state(data)
        elif to_state == AgentState.PLANNING.value:
            self.on_planning_state(data)
        elif to_state == AgentState.EXECUTING.value:
            self.on_executing_state(data)
        elif to_state == AgentState.REVIEWING.value:
            self.on_reviewing_state(data)
        elif to_state == AgentState.ERROR.value:
            self.on_error_state(data)
        elif to_state == AgentState.IDLE.value:
            self.on_idle_state(data)
        elif to_state == AgentState.AWAITING_INPUT.value:
            self.on_awaiting_input_state(data)
    
    def on_analyzing_state(self, metadata: Dict[str, Any]) -> None:
        """
        Handle transition to ANALYZING state.
        
        Args:
            metadata: State transition metadata
        """
        pass
    
    def on_planning_state(self, metadata: Dict[str, Any]) -> None:
        """
        Handle transition to PLANNING state.
        
        Args:
            metadata: State transition metadata
        """
        pass
    
    def on_executing_state(self, metadata: Dict[str, Any]) -> None:
        """
        Handle transition to EXECUTING state.
        
        Args:
            metadata: State transition metadata
        """
        pass
    
    def on_reviewing_state(self, metadata: Dict[str, Any]) -> None:
        """
        Handle transition to REVIEWING state.
        
        Args:
            metadata: State transition metadata
        """
        pass
    
    def on_error_state(self, metadata: Dict[str, Any]) -> None:
        """
        Handle transition to ERROR state.
        
        Args:
            metadata: State transition metadata
        """
        pass
    
    def on_idle_state(self, metadata: Dict[str, Any]) -> None:
        """
        Handle transition to IDLE state.
        
        Args:
            metadata: State transition metadata
        """
        pass
    
    def on_awaiting_input_state(self, metadata: Dict[str, Any]) -> None:
        """
        Handle transition to AWAITING_INPUT state.
        
        Args:
            metadata: State transition metadata
        """
        pass
    
    def check_valid_state(self, valid_states: List[AgentState]) -> bool:
        """
        Check if the current state is valid for an operation.
        
        Args:
            valid_states: List of valid states for the operation
            
        Returns:
            bool: True if the current state is valid, False otherwise
        """
        current_state = self.state_controller.get_current_state()
        return current_state in valid_states
    
    def transition_to(self, state: AgentState, reason: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Transition to a new state.
        
        Args:
            state: New state to transition to
            reason: Reason for the transition
            metadata: Optional metadata for the transition
            
        Returns:
            bool: True if the transition was successful, False otherwise
        """
        try:
            with self._lock:
                self.state_controller.transition_to(state, reason, metadata or {})
            return True
        except Exception as e:
            logger.error(f"Error transitioning to {state}: {e}")
            return False
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the current state.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        with self._lock:
            self.state_controller.set_metadata(key, value)
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the current state.
        
        Args:
            key: Metadata key
            default: Default value if key is not found
            
        Returns:
            Metadata value
        """
        return self.state_controller.get_metadata(key, default)
    
    def handle_error(self, error: Exception, context: str = "") -> None:
        """
        Handle an error by transitioning to the ERROR state.
        
        Args:
            error: Exception that occurred
            context: Context in which the error occurred
        """
        error_message = f"Error in {context}: {str(error)}"
        logger.error(error_message)
        
        self.transition_to(
            state=AgentState.ERROR,
            reason=error_message,
            metadata={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context
            }
        )

class StateAwareRAGHandler(StateAwareComponent):
    """
    State-aware RAG handler that integrates with the core state management system.
    Provides state-aware methods for RAG operations.
    """
    
    def __init__(
        self,
        state_controller: AgentStateController,
        domain_detector: Optional[Any] = None,
        knowledge_retriever: Optional[Any] = None,
        conversation_memory: Optional[Any] = None,
        long_term_memory: Optional[Any] = None
    ):
        """
        Initialize the state-aware RAG handler.
        
        Args:
            state_controller: Core AgentStateController instance
            domain_detector: Optional domain detector component
            knowledge_retriever: Optional knowledge retriever component
            conversation_memory: Optional conversation memory component
            long_term_memory: Optional long-term memory component
        """
        super().__init__(state_controller)
        
        self.domain_detector = domain_detector
        self.knowledge_retriever = knowledge_retriever
        self.conversation_memory = conversation_memory
        self.long_term_memory = long_term_memory
        
        logger.info("StateAwareRAGHandler initialized")
    
    def on_analyzing_state(self, metadata: Dict[str, Any]) -> None:
        """
        Handle transition to ANALYZING state.
        Perform domain detection and knowledge retrieval.
        
        Args:
            metadata: State transition metadata
        """
        session_id = metadata.get("session_id")
        query = metadata.get("query")
        
        if not query:
            logger.warning("No query found in metadata for ANALYZING state")
            return
        
        try:
            # Detect domain
            if self.domain_detector:
                domain = self.domain_detector.detect_domain(query)
                
                # Store domain in state metadata
                self.set_metadata("detected_domain", domain)
                
                # Publish domain detection event
                event_bus.publish(CoreEvent(
                    event_type="rag_domain_detected",
                    data={
                        "domain": domain,
                        "query": query,
                        "session_id": session_id
                    }
                ))
                
                logger.info(f"Detected domain: {domain}")
            
            # Retrieve knowledge
            if self.knowledge_retriever:
                domain = self.get_metadata("detected_domain")
                
                knowledge = self.knowledge_retriever.retrieve_for_query(
                    query=query,
                    domain=domain
                )
                
                # Store knowledge in state metadata
                self.set_metadata("rag_context", knowledge)
                self.set_metadata("rag_context_length", len(knowledge))
                
                # Publish knowledge retrieval event
                event_bus.publish(CoreEvent(
                    event_type="rag_knowledge_retrieved",
                    data={
                        "query": query,
                        "domain": domain,
                        "context_length": len(knowledge),
                        "session_id": session_id
                    }
                ))
                
                logger.info(f"Retrieved knowledge: {len(knowledge)} characters")
        
        except Exception as e:
            self.handle_error(e, "analyzing state")
    
    def on_planning_state(self, metadata: Dict[str, Any]) -> None:
        """
        Handle transition to PLANNING state.
        Prepare RAG context for response generation.
        
        Args:
            metadata: State transition metadata
        """
        session_id = metadata.get("session_id")
        
        try:
            # Get RAG context from state metadata
            rag_context = self.get_metadata("rag_context", "")
            
            # Get long-term memory if available
            long_term_context = ""
            if self.long_term_memory and session_id:
                query = metadata.get("query", "")
                
                if query:
                    long_term_context = self.long_term_memory.get_relevant_memories(
                        query=query,
                        session_id=session_id
                    )
                    
                    # Store long-term context in state metadata
                    self.set_metadata("long_term_context", long_term_context)
                    self.set_metadata("long_term_context_length", len(long_term_context))
            
            # Prepare system prompt with RAG context
            domain = self.get_metadata("detected_domain")
            system_prompt = self._create_system_prompt(rag_context, long_term_context, domain)
            
            # Store system prompt in state metadata
            self.set_metadata("system_prompt", system_prompt)
            
            # Publish context injection event
            event_bus.publish(CoreEvent(
                event_type="rag_context_injected",
                data={
                    "context_length": len(rag_context) + len(long_term_context),
                    "domain": domain,
                    "session_id": session_id
                }
            ))
            
            logger.info("Prepared RAG context for response generation")
        
        except Exception as e:
            self.handle_error(e, "planning state")
    
    def on_executing_state(self, metadata: Dict[str, Any]) -> None:
        """
        Handle transition to EXECUTING state.
        Generate response with RAG context.
        
        Args:
            metadata: State transition metadata
        """
        # This state is handled by the RAGEnhancedOpenAIHandler
        pass
    
    def on_reviewing_state(self, metadata: Dict[str, Any]) -> None:
        """
        Handle transition to REVIEWING state.
        Process feedback and update memory.
        
        Args:
            metadata: State transition metadata
        """
        session_id = metadata.get("session_id")
        
        if not session_id:
            logger.warning("No session ID found in metadata for REVIEWING state")
            return
        
        try:
            # Update long-term memory if available
            if self.long_term_memory and self.conversation_memory:
                # Get events from conversation memory
                events = self.conversation_memory.get_events(session_id)
                
                if events:
                    # Add conversation summary to long-term memory
                    self.long_term_memory.add_conversation_summary(
                        session_id=session_id,
                        events=events
                    )
                    
                    # Publish memory update event
                    event_bus.publish(CoreEvent(
                        event_type="rag_memory_updated",
                        data={
                            "session_id": session_id,
                            "event_count": len(events)
                        }
                    ))
                    
                    logger.info(f"Updated long-term memory with {len(events)} events")
        
        except Exception as e:
            self.handle_error(e, "reviewing state")
    
    def on_idle_state(self, metadata: Dict[str, Any]) -> None:
        """
        Handle transition to IDLE state.
        Condense conversation memory during idle time.
        
        Args:
            metadata: State transition metadata
        """
        session_id = metadata.get("session_id")
        
        if not session_id:
            return
        
        try:
            # Condense memory if available
            if self.long_term_memory and self.conversation_memory:
                # Get events from conversation memory
                events = self.conversation_memory.get_events(session_id)
                
                if events:
                    # Add conversation summary to long-term memory
                    self.long_term_memory.add_conversation_summary(
                        session_id=session_id,
                        events=events
                    )
                    
                    # Publish memory condensed event
                    event_bus.publish(CoreEvent(
                        event_type="rag_memory_condensed",
                        data={
                            "session_id": session_id,
                            "event_count": len(events)
                        }
                    ))
                    
                    logger.info(f"Condensed memory for session {session_id}")
        
        except Exception as e:
            logger.error(f"Error condensing memory: {e}")
            # Don't transition to ERROR state for background operations
    
    def _create_system_prompt(
        self,
        rag_context: str,
        long_term_context: str,
        domain: Optional[str]
    ) -> str:
        """
        Create a system prompt with RAG context.
        
        Args:
            rag_context: RAG context from knowledge retriever
            long_term_context: Long-term memory context
            domain: Detected financial domain
            
        Returns:
            System prompt with RAG context
        """
        system_prompt = """
You are Cori, an expert system for complex financial transaction modeling.
You provide detailed, accurate information about financial concepts and help users with financial modeling tasks.
"""
        
        # Add domain-specific instructions if domain is detected
        if domain:
            system_prompt += f"\nThe current conversation is about {domain}. Focus your expertise on this domain.\n"
        
        # Add RAG context if available
        if rag_context:
            system_prompt += "\n### RELEVANT FINANCIAL KNOWLEDGE ###\n"
            system_prompt += rag_context
            system_prompt += "\n\nUse the above knowledge to inform your responses. Cite specific concepts when appropriate.\n"
        
        # Add long-term memory context if available
        if long_term_context:
            system_prompt += "\n### RELEVANT PAST CONVERSATIONS ###\n"
            system_prompt += long_term_context
            system_prompt += "\n\nRefer to this context when it helps provide continuity with past interactions.\n"
        
        system_prompt += """
Always provide accurate, well-structured responses. For complex financial concepts:
1. Start with a clear definition
2. Explain key components
3. Provide practical examples when helpful
4. Highlight important considerations or limitations

When discussing financial models, be precise about formulas, assumptions, and methodologies.
"""
        
        return system_prompt
