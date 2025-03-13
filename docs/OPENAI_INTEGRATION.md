# OpenAI Integration Design for Cori RAG++ System

This document outlines the design for integrating OpenAI's capabilities with Cori's RAG++ memory retrieval system, focusing on how to effectively inject retrieved knowledge into prompts and optimize token usage.

## 1. OpenAI Handler Extension

The existing OpenAI handler will be extended to support RAG context injection through the following components:

```
┌──────────────────────────────────────────────────────────────────┐
│                     Extended OpenAI Handler                      │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │  RAG Context    │  │  System Prompt  │  │  Token Usage    │   │
│  │  Injection      │  │  Templates      │  │  Optimization   │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### 1.1 Current OpenAI Handler Structure

The existing OpenAI handler (`backend/ai_services/openai_handler.py`) currently:

- Initializes the OpenAI client with API key
- Uses the `gpt-4o-mini` model
- Provides methods for handling message formatting
- Manages API interactions for chat completions
- Handles basic error scenarios

### 1.2 Proposed Extensions

The handler will be extended with the following capabilities:

#### 1.2.1 RAG Context Injection

Methods to inject retrieved knowledge into prompts:

```python
def inject_rag_context(self, messages: List[Message], user_query: str, context: dict) -> List[Message]:
    """
    Injects RAG context into the message list based on the user query and context.
    
    Args:
        messages: Original message list
        user_query: The latest user query
        context: Dictionary containing conversation and Excel context
        
    Returns:
        Updated message list with injected RAG context
    """
    # Extract the latest user message
    if not messages or messages[-1].role != "user":
        return messages
    
    # Retrieve relevant knowledge
    retrieved_knowledge = self.retrieval_system.retrieve(
        query=user_query,
        context=context,
        limit=5  # Retrieve top 5 most relevant chunks
    )
    
    if not retrieved_knowledge:
        return messages
    
    # Format the retrieved knowledge
    formatted_knowledge = self._format_retrieved_knowledge(retrieved_knowledge)
    
    # Create a new system message with the retrieved knowledge
    rag_message = Message(
        role="system",
        content=f"Consider the following relevant financial knowledge when responding to the user:\n\n{formatted_knowledge}"
    )
    
    # Insert the RAG message before the user's latest message
    augmented_messages = messages[:-1] + [rag_message, messages[-1]]
    
    return augmented_messages
```

#### 1.2.2 Knowledge Formatting

Methods to format retrieved knowledge for optimal use:

```python
def _format_retrieved_knowledge(self, retrieved_knowledge: List[dict]) -> str:
    """
    Formats retrieved knowledge chunks into a structured format for the prompt.
    
    Args:
        retrieved_knowledge: List of retrieved knowledge chunks with metadata
        
    Returns:
        Formatted knowledge string
    """
    formatted_chunks = []
    
    for i, chunk in enumerate(retrieved_knowledge):
        # Format based on chunk type
        if chunk["metadata"]["type"] == "concept":
            formatted_chunks.append(self._format_concept_chunk(chunk))
        elif chunk["metadata"]["type"] == "formula":
            formatted_chunks.append(self._format_formula_chunk(chunk))
        elif chunk["metadata"]["type"] == "example":
            formatted_chunks.append(self._format_example_chunk(chunk))
        elif chunk["metadata"]["type"] == "best_practice":
            formatted_chunks.append(self._format_best_practice_chunk(chunk))
        else:
            # Generic formatting
            formatted_chunks.append(f"KNOWLEDGE [{i+1}] (Relevance: {chunk['relevance']:.2f}):\n{chunk['content']}\n")
    
    return "\n\n".join(formatted_chunks)
```

## 2. System Prompt Templates

### 2.1 Base System Prompt

A foundational system prompt that establishes Cori's identity and capabilities:

```
You are Cori, an expert financial modeling assistant specializing in complex transaction modeling. 
You help users build and analyze financial models in Excel with a focus on accuracy, clarity, and best practices.

Your capabilities include:
- Building financial models from scratch or extending existing models
- Performing financial analyses including LBOs, M&A, debt modeling, and private lending
- Explaining financial concepts and modeling techniques
- Providing step-by-step guidance on financial calculations
- Visualizing financial data effectively

Always prioritize accuracy in financial calculations and adhere to industry best practices.
When uncertain about specific details, ask clarifying questions rather than making assumptions.
```

### 2.2 Domain-Specific Prompt Templates

Specialized prompt templates for different financial domains:

#### 2.2.1 LBO Modeling Template

```
You are Cori, an expert in Leveraged Buyout (LBO) modeling. 

When analyzing or building LBO models, focus on:
- Appropriate debt sizing based on EBITDA multiples and coverage ratios
- Realistic operational projections considering the target company's industry
- Accurate debt schedules with appropriate amortization and interest calculations
- Exit value determination using appropriate multiples or DCF methodologies
- Returns analysis including IRR, MOIC, and cash-on-cash returns
- Sensitivity analyses for key variables (exit multiple, EBITDA growth, debt terms)

Key LBO modeling best practices:
- Debt-to-EBITDA multiples typically range from 4-6x depending on industry and market conditions
- Include multiple debt tranches when appropriate (senior, subordinated, mezzanine)
- Model management equity rollover and incentive structures
- Account for transaction fees and expenses
- Consider covenant compliance throughout the projection period
- Model debt prepayments from excess cash flow
```

#### 2.2.2 M&A Modeling Template

```
You are Cori, an expert in Mergers & Acquisitions (M&A) modeling.

When analyzing or building M&A models, focus on:
- Accurate standalone financial projections for both acquirer and target
- Appropriate valuation methodologies for transaction pricing
- Detailed synergy modeling (revenue and cost synergies)
- Transaction structure considerations (cash vs. stock, mixed consideration)
- Accretion/dilution analysis with EPS and other key metrics
- Pro forma financial statements and credit metrics
- Deal financing impacts including debt and equity considerations

Key M&A modeling best practices:
- Model synergies separately with realistic phasing (typically 1-3 years)
- Include one-time costs to achieve synergies
- Account for transaction expenses and financing fees
- Consider tax implications including step-up in basis when relevant
- Model purchase price allocation and resulting goodwill
- Analyze pro forma leverage and liquidity metrics
- Include sensitivity analysis for key variables (synergies, purchase price, financing mix)
```

## 3. Token Usage Optimization

### 3.1 Dynamic Context Window Management

Strategies for optimizing token usage:

```python
def optimize_context_window(self, messages: List[Message], max_tokens: int = 4096) -> List[Message]:
    """
    Optimizes the context window to stay within token limits.
    
    Args:
        messages: List of messages
        max_tokens: Maximum tokens to allow
        
    Returns:
        Optimized message list
    """
    # Estimate current token count
    current_tokens = self._estimate_token_count(messages)
    
    # If within limits, return unchanged
    if current_tokens <= max_tokens:
        return messages
    
    # Preserve system messages and recent user/assistant exchanges
    system_messages = [msg for msg in messages if msg.role == "system"]
    user_assistant_messages = [msg for msg in messages if msg.role in ["user", "assistant"]]
    
    # Keep all system messages
    optimized_messages = system_messages.copy()
    
    # Always keep the most recent exchanges
    recent_exchanges = user_assistant_messages[-4:]  # Keep last 2 user-assistant exchanges
    
    # If we still need to reduce tokens, summarize older exchanges
    if len(user_assistant_messages) > 4:
        older_exchanges = user_assistant_messages[:-4]
        summary = self._summarize_conversation(older_exchanges)
        
        # Add summary as a system message
        summary_message = Message(
            role="system",
            content=f"Previous conversation summary: {summary}"
        )
        
        optimized_messages.append(summary_message)
    
    # Add recent exchanges
    optimized_messages.extend(recent_exchanges)
    
    return optimized_messages
```

### 3.2 Relevance Filtering

Methods to filter retrieved knowledge by relevance:

```python
def filter_by_relevance(self, retrieved_knowledge: List[dict], threshold: float = 0.7) -> List[dict]:
    """
    Filters retrieved knowledge chunks by relevance score.
    
    Args:
        retrieved_knowledge: List of retrieved knowledge chunks
        threshold: Minimum relevance score to include
        
    Returns:
        Filtered knowledge chunks
    """
    return [chunk for chunk in retrieved_knowledge if chunk["relevance"] >= threshold]
```

### 3.3 Compression of Historical Context

Methods to compress conversation history:

```python
def _summarize_conversation(self, messages: List[Message]) -> str:
    """
    Summarizes a sequence of messages to reduce token usage.
    
    Args:
        messages: List of messages to summarize
        
    Returns:
        Summary string
    """
    # Format messages for summarization
    conversation = "\n".join([f"{msg.role}: {msg.content}" for msg in messages])
    
    # Use OpenAI to generate a summary
    summary_prompt = f"Summarize the following conversation concisely, focusing on key financial concepts, user requests, and important information:\n\n{conversation}"
    
    summary_message = Message(role="user", content=summary_prompt)
    
    # Get summary from OpenAI
    response = self.get_completion([summary_message])
    
    return response.content
```

## 4. Implementation Plan

### 4.1 Extended OpenAI Handler Class

```python
class ExtendedOpenAIHandler(OpenAIHandler):
    """Extended OpenAI handler with RAG capabilities."""
    
    def __init__(self, retrieval_system=None):
        super().__init__()
        self.retrieval_system = retrieval_system
        self.prompt_templates = self._load_prompt_templates()
    
    def _load_prompt_templates(self):
        """Load system prompt templates."""
        return {
            "base": "You are Cori, an expert financial modeling assistant...",
            "lbo": "You are Cori, an expert in Leveraged Buyout (LBO) modeling...",
            "ma": "You are Cori, an expert in Mergers & Acquisitions (M&A) modeling...",
            "debt": "You are Cori, an expert in debt modeling and private lending analysis...",
            "private_lending": "You are Cori, an expert in private lending and credit analysis..."
        }
    
    def get_rag_enhanced_completion(self, messages: List[Message], user_query: str, 
                                   context: dict, domain: str = None) -> Message:
        """
        Get a completion with RAG context injection and domain-specific prompting.
        
        Args:
            messages: Original message list
            user_query: The latest user query
            context: Dictionary containing conversation and Excel context
            domain: Optional domain for specialized prompting
            
        Returns:
            Message: The assistant's response
        """
        # Apply domain-specific system prompt if needed
        if domain and domain in self.prompt_templates:
            domain_prompt = Message(role="system", content=self.prompt_templates[domain])
            # Replace existing system messages or add if none exist
            has_system = any(msg.role == "system" for msg in messages)
            if has_system:
                messages = [domain_prompt if msg.role == "system" else msg for msg in messages]
            else:
                messages = [domain_prompt] + messages
        
        # Inject RAG context
        augmented_messages = self.inject_rag_context(messages, user_query, context)
        
        # Optimize token usage
        optimized_messages = self.optimize_context_window(augmented_messages)
        
        # Get completion
        return super().get_completion(optimized_messages)
```

### 4.2 Integration with Existing Code

The extended handler will be integrated with the existing server.py:

```python
# In server.py

from ai_services.extended_openai_handler import ExtendedOpenAIHandler
from retrieval.retrieval_system import RetrievalSystem

# Initialize systems
retrieval_system = RetrievalSystem()
openai_handler = ExtendedOpenAIHandler(retrieval_system=retrieval_system)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = [Message(**msg) for msg in data.get('messages', [])]
    user_query = messages[-1].content if messages and messages[-1].role == "user" else ""
    
    # Extract context from request
    context = {
        "conversation_history": data.get('conversation_history', []),
        "excel_state": data.get('excel_state', {})
    }
    
    # Detect domain from query
    domain = detect_domain(user_query, context)
    
    # Get enhanced completion
    response = openai_handler.get_rag_enhanced_completion(
        messages=messages,
        user_query=user_query,
        context=context,
        domain=domain
    )
    
    return jsonify(response.to_dict())
```

## 5. Conclusion

This OpenAI integration design provides a comprehensive framework for extending the existing OpenAI handler with RAG capabilities, domain-specific prompting, and token optimization strategies. By implementing these extensions, Cori will be able to leverage specialized financial knowledge, provide domain-specific guidance, and efficiently manage token usage for optimal performance.
