import os
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI
import sys

# Add the parent directory to sys.path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.message import Message

class OpenAIHandler:
    """Handler for OpenAI API interactions."""
    
    def __init__(self):
        # Get API key from environment variable
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Default model
        self.model = "gpt-4o-mini"
    
    def get_completion(self, messages: List[Message], model: Optional[str] = None) -> Message:
        """
        Get a completion from the OpenAI API.
        
        Args:
            messages: List of Message objects representing the conversation history
            model: Optional model override (defaults to gpt-4o-mini)
            
        Returns:
            Message: The assistant's response
        """
        # Record start time for thinking duration
        start_time = time.time()
        
        # Convert messages to OpenAI format
        openai_messages = [msg.to_openai_format() for msg in messages]
        
        # Make API request
        try:
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=openai_messages,
                temperature=0.7,
                max_tokens=1024
            )
            
            # Calculate thinking time
            thinking_time = int(time.time() - start_time)
            
            # Create and return Message object
            return Message(
                role="system",
                content=response.choices[0].message.content,
                thinking_time=thinking_time,
                displayed=False  # Set to false to trigger typewriter effect
            )
            
        except Exception as e:
            # Handle errors gracefully
            error_message = f"Error getting completion from OpenAI: {str(e)}"
            return Message(
                role="system",
                content=error_message,
                thinking_time=int(time.time() - start_time),
                displayed=False
            )
