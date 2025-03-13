from typing import Dict, List, Optional, Any, Union
import os
import time
from openai import OpenAI

from .memory_manager import MemoryManager
from .models.event import Event

class RAGEnhancedOpenAIHandler:
    """
    Enhanced OpenAI handler with RAG context injection.
    Extends the existing OpenAI handler to support retrieving and injecting
    relevant knowledge from the memory system.
    """
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        model_name: str = "gpt-4o",
        system_prompt_template: Optional[str] = None
    ):
        """
        Initialize the RAG-enhanced OpenAI handler.
        
        Args:
            memory_manager: Memory manager for retrieving context
            model_name: Name of the OpenAI model to use
            system_prompt_template: Optional custom system prompt template
        """
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model_name = model_name
        self.memory_manager = memory_manager
        self.system_prompt_template = system_prompt_template or self._default_system_prompt()
    
    def _default_system_prompt(self) -> str:
        """
        Get the default system prompt template.
        
        Returns:
            Default system prompt template
        """
        return """You are Cori, an expert financial modeling assistant specializing in complex transaction modeling.
        You have deep expertise in LBOs, Corporate M&A, Debt Modeling, and Private Lending.
        
        Your goal is to help the user build and analyze financial models in Excel.
        
        RELEVANT KNOWLEDGE FROM YOUR MEMORY:
        {retrieved_knowledge}
        
        USER PREFERENCES:
        {user_preferences}
        
        CURRENT FINANCIAL CONTEXT:
        {financial_context}
        
        When responding:
        1. Prioritize accuracy in financial calculations and methodologies
        2. Provide clear explanations of financial concepts
        3. Follow the user's preferred modeling approaches when specified
        4. Be concise but thorough in your explanations
        5. Suggest improvements to the user's financial models when appropriate
        
        Remember that you are an expert in financial modeling and your advice should reflect industry best practices.
        """
    
    def get_rag_enhanced_completion(
        self,
        messages: List[Dict[str, str]],
        user_query: str,
        context: Dict[str, Any] = None,
        domain: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a completion with RAG context injection.
        
        Args:
            messages: List of messages representing the conversation history
            user_query: The user's query
            context: Optional additional context
            domain: Optional domain for the query
            model: Optional model override
            
        Returns:
            The assistant's response
        """
        # Record start time for thinking duration
        start_time = time.time()
        
        # Get context from memory
        context = context or {}
        
        # Retrieve relevant knowledge
        retrieved_knowledge = self._retrieve_relevant_knowledge(user_query, domain)
        
        # Get user preferences
        user_preferences = self._get_user_preferences(domain, context)
        
        # Get financial context
        financial_context = self._get_financial_context(domain, context)
        
        # Create system message with injected context
        system_message = self._create_system_message(
            retrieved_knowledge=retrieved_knowledge,
            user_preferences=user_preferences,
            financial_context=financial_context
        )
        
        # Prepend system message to conversation
        enhanced_messages = [
            {"role": "system", "content": system_message}
        ]
        
        # Add conversation history
        for message in messages:
            enhanced_messages.append(message)
        
        # Make API request
        try:
            response = self.client.chat.completions.create(
                model=model or self.model_name,
                messages=enhanced_messages,
                temperature=0.7,
                max_tokens=1024
            )
            
            # Calculate thinking time
            thinking_time = int(time.time() - start_time)
            
            # Create response
            result = {
                "role": "assistant",
                "content": response.choices[0].message.content,
                "thinking_time": thinking_time,
                "displayed": False
            }
            
            # Add response to memory
            self.memory_manager.add_assistant_message(
                content=result["content"],
                thinking_time=thinking_time,
                domain=domain
            )
            
            return result
            
        except Exception as e:
            # Handle errors gracefully
            error_message = f"Error getting completion from OpenAI: {str(e)}"
            
            return {
                "role": "system",
                "content": error_message,
                "thinking_time": int(time.time() - start_time),
                "displayed": False
            }
    
    def _retrieve_relevant_knowledge(
        self,
        query: str,
        domain: Optional[str] = None
    ) -> str:
        """
        Retrieve relevant knowledge from memory.
        
        Args:
            query: The user's query
            domain: Optional domain for the query
            
        Returns:
            Formatted knowledge string
        """
        # Search for relevant knowledge
        results = self.memory_manager.search_knowledge(
            query=query,
            domain=domain,
            k=5
        )
        
        # Format results
        if not results:
            return "No relevant knowledge found."
        
        formatted_knowledge = "Here is relevant information from your knowledge base:\n\n"
        
        for i, result in enumerate(results):
            formatted_knowledge += f"{i+1}. {result['text']}\n"
            if i < len(results) - 1:
                formatted_knowledge += "\n---\n\n"
        
        return formatted_knowledge
    
    def _get_user_preferences(
        self,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get user preferences.
        
        Args:
            domain: Optional domain for preferences
            context: Optional additional context
            
        Returns:
            Formatted preferences string
        """
        # This would be extended to retrieve actual user preferences
        # from the preference store
        
        # For now, return a placeholder
        return "No specific preferences found."
    
    def _get_financial_context(
        self,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get financial context.
        
        Args:
            domain: Optional domain for context
            context: Optional additional context
            
        Returns:
            Formatted financial context string
        """
        # This would be extended to extract financial context
        # from the conversation and Excel state
        
        # For now, return a placeholder
        return "No specific financial context available."
    
    def _create_system_message(
        self,
        retrieved_knowledge: str,
        user_preferences: str,
        financial_context: str
    ) -> str:
        """
        Create a system message with injected context.
        
        Args:
            retrieved_knowledge: Retrieved knowledge from memory
            user_preferences: User preferences
            financial_context: Financial context
            
        Returns:
            System message with injected context
        """
        return self.system_prompt_template.format(
            retrieved_knowledge=retrieved_knowledge,
            user_preferences=user_preferences,
            financial_context=financial_context
        )
