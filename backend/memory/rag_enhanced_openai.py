"""
RAG-enhanced OpenAI handler for Cori RAG++ system.
Provides enhanced OpenAI API integration with RAG capabilities.
"""

from typing import Dict, List, Any, Optional, Union
import os
import time
import threading
import logging
from datetime import datetime

# Import OpenAI
from openai import OpenAI

# Import core classes
from backend.ai_services.openai_handler import OpenAIHandler
from backend.models.message import Message as CoreMessage
from backend.core.event_system import event_bus, Event as CoreEvent

# Import RAG++ classes
from backend.memory.conversation_memory import ConversationMemory
from backend.memory.knowledge.knowledge_retriever import KnowledgeRetriever
from backend.memory.knowledge.financial_domain_detector import FinancialDomainDetector
from backend.memory.long_term_memory import LongTermMemory

# Import adapters
from backend.memory.adapters.message_adapter import MessageAdapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGEnhancedOpenAIHandler:
    """
    RAG-enhanced OpenAI handler that integrates with the core infrastructure.
    Uses composition pattern to combine core OpenAIHandler with RAG capabilities.
    Maintains API compatibility with the existing OpenAIHandler.
    """
    
    def __init__(
        self,
        core_handler: Optional[OpenAIHandler] = None,
        conversation_memory: Optional[ConversationMemory] = None,
        long_term_memory: Optional[LongTermMemory] = None,
        knowledge_retriever: Optional[KnowledgeRetriever] = None,
        domain_detector: Optional[FinancialDomainDetector] = None,
        rag_enabled: bool = True,
        default_model: str = "gpt-4o"
    ):
        """
        Initialize the RAG-enhanced OpenAI handler.
        
        Args:
            core_handler: Core OpenAIHandler instance
            conversation_memory: RAG++ ConversationMemory instance
            long_term_memory: RAG++ LongTermMemory instance
            knowledge_retriever: RAG++ KnowledgeRetriever instance
            domain_detector: RAG++ FinancialDomainDetector instance
            rag_enabled: Whether RAG enhancement is enabled
            default_model: Default model to use
        """
        # Initialize core handler
        self.core_handler = core_handler or OpenAIHandler()
        
        # Initialize RAG++ components
        self.conversation_memory = conversation_memory
        self.long_term_memory = long_term_memory
        self.knowledge_retriever = knowledge_retriever
        self.domain_detector = domain_detector
        
        # Initialize adapters
        self.message_adapter = MessageAdapter()
        
        # Configuration
        self.rag_enabled = rag_enabled
        self.default_model = default_model
        
        # Thread safety
        self._lock = threading.Lock()
        
        logger.info("RAGEnhancedOpenAIHandler initialized")
    
    def get_completion(
        self,
        messages: List[CoreMessage],
        session_id: Optional[str] = None,
        model: Optional[str] = None,
        rag_enabled: Optional[bool] = None
    ) -> CoreMessage:
        """
        Get a completion from the OpenAI API with RAG enhancement.
        Maintains API compatibility with the core OpenAIHandler.
        
        Args:
            messages: List of Message objects representing the conversation history
            session_id: Optional session ID for memory retrieval
            model: Optional model override
            rag_enabled: Optional override for RAG enhancement
            
        Returns:
            Message: The assistant's response
        """
        # Determine if RAG is enabled for this request
        use_rag = self.rag_enabled if rag_enabled is None else rag_enabled
        
        # If RAG is disabled or components are missing, fall back to core handler
        if not use_rag or not all([
            self.conversation_memory,
            self.knowledge_retriever,
            self.domain_detector
        ]):
            logger.info("Using core OpenAIHandler (RAG disabled)")
            return self.core_handler.get_completion(
                messages=messages,
                model=model or self.default_model
            )
        
        # Record start time for thinking duration
        start_time = time.time()
        
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Get last user message
            last_user_message = next(
                (msg for msg in reversed(messages) if msg.role == "user"),
                None
            )
            
            if not last_user_message:
                logger.warning("No user message found in conversation history")
                return self.core_handler.get_completion(
                    messages=messages,
                    model=model or self.default_model
                )
            
            # Detect domain
            domain = None
            if self.domain_detector:
                domain = self.domain_detector.detect_domain(last_user_message.content)
                
                # Publish domain detection event
                event_bus.publish(CoreEvent(
                    event_type="rag_domain_detected",
                    data={
                        "domain": domain,
                        "query": last_user_message.content,
                        "session_id": session_id
                    }
                ))
            
            # Retrieve knowledge
            rag_context = ""
            if self.knowledge_retriever:
                rag_context = self.knowledge_retriever.retrieve_for_query(
                    query=last_user_message.content,
                    domain=domain
                )
                
                # Publish knowledge retrieval event
                event_bus.publish(CoreEvent(
                    event_type="rag_knowledge_retrieved",
                    data={
                        "query": last_user_message.content,
                        "domain": domain,
                        "context_length": len(rag_context),
                        "session_id": session_id
                    }
                ))
            
            # Retrieve long-term memory if available
            long_term_context = ""
            if self.long_term_memory and session_id:
                long_term_context = self.long_term_memory.get_relevant_memories(
                    query=last_user_message.content,
                    session_id=session_id
                )
            
            # Store messages in conversation memory if available
            if self.conversation_memory and session_id:
                # Convert core Messages to RAG++ Events
                events = self.message_adapter.core_to_rag_batch(messages)
                
                # Add events to conversation memory
                self.conversation_memory.add_events(session_id, events)
            
            # Create system message with RAG context
            system_message = CoreMessage(
                role="system",
                content=self._create_system_prompt(rag_context, long_term_context, domain)
            )
            
            # Add system message to the beginning of the messages
            enhanced_messages = [system_message] + messages
            
            # Publish context injection event
            event_bus.publish(CoreEvent(
                event_type="rag_context_injected",
                data={
                    "context_length": len(rag_context) + len(long_term_context),
                    "domain": domain,
                    "session_id": session_id
                }
            ))
            
            # Get completion from core handler with enhanced messages
            response = self.core_handler.get_completion(
                messages=enhanced_messages,
                model=model or self.default_model
            )
            
            # Store response in conversation memory if available
            if self.conversation_memory and session_id:
                # Convert core Message to RAG++ Event
                event = self.message_adapter.core_to_rag(response)
                
                # Add event to conversation memory
                self.conversation_memory.add_event(session_id, event)
                
                # Save events to disk
                self.conversation_memory.save_events(session_id)
            
            # Publish response generation event
            event_bus.publish(CoreEvent(
                event_type="rag_response_generated",
                data={
                    "response_length": len(response.content),
                    "thinking_time": response.thinking_time,
                    "session_id": session_id
                }
            ))
            
            return response
            
        except Exception as e:
            # Handle errors gracefully
            error_message = f"Error in RAG-enhanced completion: {str(e)}"
            logger.error(error_message)
            
            # Fall back to core handler
            logger.info("Falling back to core OpenAIHandler")
            return self.core_handler.get_completion(
                messages=messages,
                model=model or self.default_model
            )
    
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
    
    def process_feedback(
        self,
        session_id: str,
        feedback: str,
        rating: Optional[int] = None
    ) -> bool:
        """
        Process user feedback for learning.
        
        Args:
            session_id: Session ID
            feedback: User feedback text
            rating: Optional numerical rating (1-5)
            
        Returns:
            bool: True if successfully processed, False otherwise
        """
        try:
            # Publish feedback event
            event_bus.publish(CoreEvent(
                event_type="rag_feedback_received",
                data={
                    "session_id": session_id,
                    "feedback": feedback,
                    "rating": rating
                }
            ))
            
            # Update long-term memory if available
            if self.long_term_memory:
                self.long_term_memory.add_feedback(
                    session_id=session_id,
                    feedback=feedback,
                    rating=rating
                )
            
            logger.info(f"Processed feedback for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            return False
    
    def condense_memory(self, session_id: str) -> bool:
        """
        Condense conversation memory for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            bool: True if successfully condensed, False otherwise
        """
        try:
            # Check if conversation memory is available
            if not self.conversation_memory:
                logger.warning("Conversation memory not available")
                return False
            
            # Get events from conversation memory
            events = self.conversation_memory.get_events(session_id)
            
            if not events:
                logger.warning(f"No events found for session {session_id}")
                return False
            
            # Update long-term memory if available
            if self.long_term_memory:
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
            return True
            
        except Exception as e:
            logger.error(f"Error condensing memory: {e}")
            return False
