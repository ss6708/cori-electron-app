# Cori RAG++ Memory System

This module implements a three-tier memory architecture for Cori's RAG++ system, designed specifically for financial transaction modeling domains.

## Overview

The memory system consists of three tiers:

1. **Conversation Memory**: Manages the short-term conversation history, including event tracking and condensation.
2. **Memory Condensers**: Reduces the size of the conversation history while preserving important information.
3. **Long-Term Memory**: Stores persistent knowledge using ChromaDB and vector embeddings.

## Key Components

### Event Models

- `Event`: Base class for all events
- `FinancialModelingEvent`: Base class for financial modeling events
- Domain-specific events:
  - `LBOModelingEvent`: Events related to LBO modeling
  - `MAModelingEvent`: Events related to M&A modeling
  - `DebtModelingEvent`: Events related to debt modeling
  - `PrivateLendingEvent`: Events related to private lending

### Condensers

- `Condenser`: Abstract base class for all condensers
- `RollingCondenser`: Base class for condensers that apply to rolling history
- `RecentEventsCondenser`: Simple condenser that keeps recent events
- `FinancialDomainCondenser`: Base condenser for financial domain contexts
- Domain-specific condensers:
  - `LBOModelingCondenser`: Preserves transaction structure, debt terms, and exit assumptions
  - `MAModelingCondenser`: Preserves valuation methodology, deal structure, and synergies
  - `DebtModelingCondenser`: Preserves debt sizing, covenant analysis, and amortization schedules
  - `PrivateLendingCondenser`: Preserves loan terms, security analysis, and returns calculation
- LLM-based condensers:
  - `LLMSummarizingCondenser`: Creates concise summaries of past events
  - `LLMAttentionCondenser`: Identifies and prioritizes important events
  - `FinancialLLMSummarizingCondenser`: Specialized for financial modeling contexts

### Memory Management

- `ConversationMemory`: Manages the conversation memory for a session
- `LongTermMemory`: Handles storing and retrieving information using ChromaDB
- `MemoryManager`: Coordinates between conversation memory, condensers, and long-term memory
- `UserPreferenceStore`: Manages storage and retrieval of user preferences

### OpenAI Integration

- `RAGEnhancedOpenAIHandler`: Extends the existing OpenAI handler to support RAG context injection

## Usage

### Basic Usage

```python
from memory.memory_manager import MemoryManager
from memory.rag_enhanced_openai import RAGEnhancedOpenAIHandler
from ai_services import OpenAIHandler

# Initialize OpenAI handler
openai_handler = OpenAIHandler()

# Initialize memory manager
memory_manager = MemoryManager(
    session_id="session-123",
    user_id="user-456",
    db_path="./data/vector_db",
    openai_handler=openai_handler
)

# Initialize RAG-enhanced OpenAI handler
rag_openai_handler = RAGEnhancedOpenAIHandler(
    memory_manager=memory_manager,
    model_name="gpt-4o"
)

# Add user message to memory
memory_manager.add_user_message("How should I structure an LBO model?", domain="lbo")

# Get RAG-enhanced response
response = rag_openai_handler.get_rag_enhanced_completion(
    messages=[{"role": "user", "content": "How should I structure an LBO model?"}],
    user_query="How should I structure an LBO model?",
    domain="lbo"
)

print(response['content'])
```

### Adding Knowledge

```python
# Add knowledge document
memory_manager.add_knowledge_document(
    text="LBO models typically use debt-to-EBITDA ratios of 4-6x for senior debt.",
    metadata={
        "type": "financial_knowledge",
        "domain": "lbo",
        "topic": "debt_sizing"
    },
    domain="lbo"
)
```

### Searching Knowledge

```python
# Search for relevant knowledge
results = memory_manager.search_knowledge(
    query="debt structure for LBO",
    domain="lbo",
    k=5
)

for result in results:
    print(f"Document: {result['text']}")
    print(f"Metadata: {result['metadata']}")
    print(f"Relevance: {1.0 - result['distance']:.2f}")
    print()
```

## Examples

See the `examples` directory for complete examples:

- `rag_integration_example.py`: Demonstrates the integration of the three-tier memory architecture with the existing OpenAI handler
- `memory_integration.py`: Shows how to integrate the memory system with the existing backend server

## Dependencies

- `openai`: OpenAI API client
- `chromadb`: Vector database for long-term memory
- `pydantic`: Data validation and settings management
- `numpy`: Numerical operations for embeddings

## Testing

Run the tests with pytest:

```bash
pytest backend/memory/tests/
```
