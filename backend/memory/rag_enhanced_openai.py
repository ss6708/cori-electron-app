"""
RAG-enhanced OpenAI integration for Cori's three-tier memory architecture.
This module provides enhanced OpenAI API integration with RAG capabilities.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime
import time

from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessage

from .models.event import Event
from .conversation_memory import ConversationMemory
from .long_term_memory import LongTermMemory
from .knowledge.financial_knowledge_base import FinancialKnowledgeBase
from .knowledge.knowledge_retriever import KnowledgeRetriever
from .knowledge.financial_domain_detector import FinancialDomainDetector

# Set up logging
logger = logging.getLogger(__name__)

class RAGEnhancedOpenAI:
    """
    RAG-enhanced OpenAI integration for Cori's three-tier memory architecture.
    This class provides enhanced OpenAI API integration with RAG capabilities.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        conversation_memory: Optional[ConversationMemory] = None,
        long_term_memory: Optional[LongTermMemory] = None,
        knowledge_base: Optional[FinancialKnowledgeBase] = None,
        domain_detector: Optional[FinancialDomainDetector] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """
        Initialize the RAG-enhanced OpenAI integration.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
            model: OpenAI model to use
            conversation_memory: Conversation memory instance
            long_term_memory: Long-term memory instance
            knowledge_base: Financial knowledge base instance
            domain_detector: Financial domain detector instance
            temperature: Temperature for OpenAI API
            max_tokens: Maximum tokens for OpenAI API
            session_id: Session ID for conversation memory
            user_id: User ID for conversation memory
        """
        # Set API key
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Set model and parameters
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Set session and user IDs
        self.session_id = session_id or f"session_{int(time.time())}"
        self.user_id = user_id or "default_user"
        
        # Initialize memory components
        self.conversation_memory = conversation_memory or ConversationMemory(
            session_id=self.session_id,
            user_id=self.user_id
        )
        
        self.long_term_memory = long_term_memory
        self.knowledge_base = knowledge_base
        
        # Initialize domain detector
        self.domain_detector = domain_detector or FinancialDomainDetector(
            api_key=self.api_key
        )
        
        # Initialize knowledge retriever if knowledge base is provided
        self.knowledge_retriever = None
        if self.knowledge_base:
            self.knowledge_retriever = KnowledgeRetriever(
                financial_knowledge_base=self.knowledge_base
            )
        
        # Track whether RAG is enabled
        self.rag_enabled = True
        
        # Track the current financial domain
        self.current_domain = "general"
        self.domain_confidence = 0.0
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        rag_enabled: Optional[bool] = None,
        rag_query: Optional[str] = None,
        system_prompt: Optional[str] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[Union[str, Dict[str, Any]]] = None
    ) -> Union[ChatCompletion, Dict[str, Any]]:
        """
        Generate a chat completion with RAG enhancement.
        
        Args:
            messages: List of messages for the chat completion
            model: OpenAI model to use (overrides instance model)
            temperature: Temperature for OpenAI API (overrides instance temperature)
            max_tokens: Maximum tokens for OpenAI API (overrides instance max_tokens)
            stream: Whether to stream the response
            rag_enabled: Whether to enable RAG (overrides instance rag_enabled)
            rag_query: Query for RAG retrieval (defaults to last user message)
            system_prompt: System prompt to use (overrides any existing system prompt)
            functions: Functions for function calling
            function_call: Function call configuration
            
        Returns:
            Chat completion or streamed response
        """
        # Set parameters
        model = model or self.model
        temperature = temperature if temperature is not None else self.temperature
        max_tokens = max_tokens or self.max_tokens
        rag_enabled = rag_enabled if rag_enabled is not None else self.rag_enabled
        
        # Process messages
        processed_messages = self._process_messages(
            messages=messages,
            system_prompt=system_prompt,
            rag_enabled=rag_enabled,
            rag_query=rag_query
        )
        
        # Generate completion
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=processed_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                functions=functions,
                function_call=function_call
            )
            
            # Store the interaction in conversation memory
            self._store_interaction(messages, response)
            
            return response
        
        except Exception as e:
            logger.error(f"Error generating chat completion: {e}")
            raise
    
    def chat_completion_with_domain_detection(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        system_prompt: Optional[str] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[Union[str, Dict[str, Any]]] = None
    ) -> Union[ChatCompletion, Dict[str, Any]]:
        """
        Generate a chat completion with domain detection and RAG enhancement.
        
        Args:
            messages: List of messages for the chat completion
            model: OpenAI model to use (overrides instance model)
            temperature: Temperature for OpenAI API (overrides instance temperature)
            max_tokens: Maximum tokens for OpenAI API (overrides instance max_tokens)
            stream: Whether to stream the response
            system_prompt: System prompt to use (overrides any existing system prompt)
            functions: Functions for function calling
            function_call: Function call configuration
            
        Returns:
            Chat completion or streamed response
        """
        # Detect domain from messages
        if len(messages) > 0:
            last_user_message = None
            for msg in reversed(messages):
                if msg["role"] == "user":
                    last_user_message = msg["content"]
                    break
            
            if last_user_message:
                domain, confidence = self.domain_detector.detect_domain(last_user_message)
                self.current_domain = domain
                self.domain_confidence = confidence
                logger.info(f"Detected domain: {domain} (confidence: {confidence:.2f})")
        
        # Generate completion with domain-specific RAG
        return self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            rag_enabled=True,
            system_prompt=system_prompt,
            functions=functions,
            function_call=function_call
        )
    
    def chat_completion_with_feedback(
        self,
        messages: List[Dict[str, str]],
        feedback_function: Callable[[ChatCompletion], Tuple[bool, str]],
        max_attempts: int = 3,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[Union[str, Dict[str, Any]]] = None
    ) -> Tuple[ChatCompletion, bool, str]:
        """
        Generate a chat completion with feedback-based improvement.
        
        Args:
            messages: List of messages for the chat completion
            feedback_function: Function that takes a completion and returns (is_acceptable, feedback)
            max_attempts: Maximum number of attempts to generate an acceptable completion
            model: OpenAI model to use (overrides instance model)
            temperature: Temperature for OpenAI API (overrides instance temperature)
            max_tokens: Maximum tokens for OpenAI API (overrides instance max_tokens)
            system_prompt: System prompt to use (overrides any existing system prompt)
            functions: Functions for function calling
            function_call: Function call configuration
            
        Returns:
            Tuple of (final_completion, is_acceptable, feedback)
        """
        # Set parameters
        model = model or self.model
        temperature = temperature if temperature is not None else self.temperature
        max_tokens = max_tokens or self.max_tokens
        
        # Initialize variables
        current_messages = messages.copy()
        
        # Try to generate an acceptable completion
        for attempt in range(max_attempts):
            # Generate completion
            completion = self.chat_completion(
                messages=current_messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                system_prompt=system_prompt,
                functions=functions,
                function_call=function_call
            )
            
            # Get feedback
            is_acceptable, feedback = feedback_function(completion)
            
            # If acceptable, return the completion
            if is_acceptable:
                return completion, True, feedback
            
            # Add feedback to messages
            current_messages.append({
                "role": "user",
                "content": f"Please improve your response based on this feedback: {feedback}"
            })
        
        # Return the last completion with feedback
        return completion, False, feedback
    
    def _process_messages(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        rag_enabled: bool = False,
        rag_query: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Process messages for chat completion.
        
        Args:
            messages: List of messages for the chat completion
            system_prompt: System prompt to use (overrides any existing system prompt)
            rag_enabled: Whether to enable RAG
            rag_query: Query for RAG retrieval (defaults to last user message)
            
        Returns:
            Processed messages
        """
        # Create a copy of the messages
        processed_messages = messages.copy()
        
        # Handle system prompt
        if system_prompt:
            # Check if there's an existing system message
            has_system_message = False
            for i, msg in enumerate(processed_messages):
                if msg["role"] == "system":
                    # Replace existing system message
                    processed_messages[i] = {
                        "role": "system",
                        "content": system_prompt
                    }
                    has_system_message = True
                    break
            
            # Add system message if none exists
            if not has_system_message:
                processed_messages.insert(0, {
                    "role": "system",
                    "content": system_prompt
                })
        
        # Add RAG context if enabled
        if rag_enabled and self.knowledge_retriever:
            # Get the query for RAG
            if not rag_query:
                # Use the last user message as the query
                for msg in reversed(processed_messages):
                    if msg["role"] == "user":
                        rag_query = msg["content"]
                        break
            
            if rag_query:
                # Retrieve relevant knowledge
                rag_context = self._retrieve_rag_context(rag_query)
                
                # Add RAG context to system message
                if rag_context:
                    for i, msg in enumerate(processed_messages):
                        if msg["role"] == "system":
                            processed_messages[i] = {
                                "role": "system",
                                "content": f"{msg['content']}\n\n{rag_context}"
                            }
                            break
                    else:
                        # No system message found, add one
                        processed_messages.insert(0, {
                            "role": "system",
                            "content": f"You are Cori, a financial modeling expert. Use the following information to help answer the user's questions:\n\n{rag_context}"
                        })
        
        return processed_messages
    
    def _retrieve_rag_context(self, query: str) -> str:
        """
        Retrieve RAG context for a query.
        
        Args:
            query: Query for RAG retrieval
            
        Returns:
            RAG context
        """
        if not self.knowledge_retriever:
            return ""
        
        try:
            # Retrieve knowledge for the current domain
            knowledge = self.knowledge_retriever.retrieve_for_query(
                query=query,
                domain=self.current_domain,
                k=5
            )
            
            # If confidence is low, also retrieve from other domains
            if self.domain_confidence < 0.7:
                # Get relevant domains
                relevant_domains = self.domain_detector.get_relevant_domains(
                    query=query,
                    threshold=0.3
                )
                
                # Remove current domain from relevant domains
                if self.current_domain in relevant_domains:
                    relevant_domains.remove(self.current_domain)
                
                # Retrieve from other domains
                if relevant_domains:
                    multi_domain_knowledge = self.knowledge_retriever.retrieve_multi_domain(
                        query=query,
                        domains=relevant_domains,
                        k_per_domain=2
                    )
                    
                    # Combine knowledge
                    if multi_domain_knowledge:
                        knowledge += "\n\n" + multi_domain_knowledge
            
            return knowledge
        
        except Exception as e:
            logger.error(f"Error retrieving RAG context: {e}")
            return ""
    
    def _store_interaction(
        self,
        messages: List[Dict[str, str]],
        response: Union[ChatCompletion, Dict[str, Any]]
    ) -> None:
        """
        Store the interaction in conversation memory.
        
        Args:
            messages: List of messages for the chat completion
            response: Chat completion response
        """
        if not self.conversation_memory:
            return
        
        try:
            # Store user message
            for msg in messages:
                if msg["role"] == "user":
                    user_event = Event(
                        id=f"user_{int(time.time())}",
                        role="user",
                        content=msg["content"],
                        timestamp=datetime.now().isoformat()
                    )
                    self.conversation_memory.add_event(user_event)
            
            # Store assistant message
            if hasattr(response, "choices") and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content:
                    assistant_event = Event(
                        id=f"assistant_{int(time.time())}",
                        role="assistant",
                        content=content,
                        timestamp=datetime.now().isoformat()
                    )
                    self.conversation_memory.add_event(assistant_event)
        
        except Exception as e:
            logger.error(f"Error storing interaction in conversation memory: {e}")
    
    def get_conversation_history(self) -> List[Event]:
        """
        Get the conversation history.
        
        Returns:
            List of events in the conversation history
        """
        if not self.conversation_memory:
            return []
        
        return self.conversation_memory.get_events()
    
    def clear_conversation_history(self) -> None:
        """Clear the conversation history."""
        if self.conversation_memory:
            # Delete all events in the session
            session_ids = self.conversation_memory.get_session_ids()
            for session_id in session_ids:
                self.conversation_memory.delete_session(session_id)
    
    def set_rag_enabled(self, enabled: bool) -> None:
        """
        Set whether RAG is enabled.
        
        Args:
            enabled: Whether to enable RAG
        """
        self.rag_enabled = enabled
    
    def set_current_domain(self, domain: str, confidence: float = 1.0) -> None:
        """
        Set the current financial domain.
        
        Args:
            domain: Financial domain
            confidence: Confidence in the domain
        """
        self.current_domain = domain
        self.domain_confidence = confidence
    
    def detect_domain_from_history(self) -> Tuple[str, float]:
        """
        Detect the financial domain from conversation history.
        
        Returns:
            Tuple of (domain, confidence)
        """
        if not self.conversation_memory or not self.domain_detector:
            return "general", 0.5
        
        events = self.conversation_memory.get_events()
        if not events:
            return "general", 0.5
        
        domain, confidence = self.domain_detector.detect_domain_from_events(events)
        self.current_domain = domain
        self.domain_confidence = confidence
        
        return domain, confidence
    
    def format_response(self, response: str) -> str:
        """
        Format the response for display.
        
        Args:
            response: Response to format
            
        Returns:
            Formatted response
        """
        # Convert markdown-style bold text to actual bold text
        formatted = response.replace("**", "")
        
        # Create new lines for bullet points and numbered lists
        formatted = formatted.replace("- ", "\n- ")
        
        # Break large text paragraphs into smaller, more readable sections
        paragraphs = formatted.split("\n\n")
        formatted = "\n\n".join(paragraphs)
        
        return formatted
