# Cori Memory Architecture

The Cori application implements a sophisticated three-tier memory architecture designed specifically for financial modeling and transaction analysis. This document outlines the memory system design, components, and integration points.

## Three-Tier Memory Architecture

The memory system is organized into three distinct tiers, each serving a specific purpose in the overall memory management strategy:

### 1. Conversation Memory (Short-Term)

The `ConversationMemory` component manages the immediate conversation context, storing recent interactions between the user and the system.

**Key Features:**
- Thread-safe event storage and retrieval
- Session-based organization
- Support for event condensation to prevent context overflow
- Persistence to disk for session recovery

**Implementation:**
```python
from backend.memory.conversation_memory import ConversationMemory

# Initialize with storage directory
conversation_memory = ConversationMemory(storage_dir="/path/to/storage")

# Add events to a session
conversation_memory.add_event(session_id, event)

# Retrieve events for a session
events = conversation_memory.get_events(session_id)
```

### 2. Long-Term Memory

The `LongTermMemory` component provides vector-based storage for historical conversations and domain knowledge, enabling semantic retrieval of relevant information.

**Key Features:**
- ChromaDB-backed vector storage
- Semantic similarity search
- Domain-specific collections
- Conversation summarization and retrieval
- User feedback storage and retrieval

**Implementation:**
```python
from backend.memory.long_term_memory import LongTermMemory

# Initialize with storage directory
long_term_memory = LongTermMemory(storage_dir="/path/to/storage")

# Add conversation summary
long_term_memory.add_conversation_summary(
    session_id="session_123",
    summary="Discussion about LBO modeling techniques",
    metadata={"domain": "LBO"}
)

# Retrieve relevant memories
memories = long_term_memory.get_relevant_memories(
    query="How to structure an LBO model?",
    session_id="session_123"
)
```

### 3. Knowledge Base

The `FinancialKnowledgeBase` component stores domain-specific knowledge about financial modeling concepts, providing a foundation for the RAG system.

**Key Features:**
- Domain-specific collections (LBO, M&A, Debt Modeling, Private Lending)
- Document chunking and embedding
- Semantic search across knowledge domains
- Integration with domain detection

**Implementation:**
```python
from backend.memory.knowledge.financial_knowledge_base import FinancialKnowledgeBase

# Initialize with storage directory
knowledge_base = FinancialKnowledgeBase(storage_dir="/path/to/storage")

# Add document to knowledge base
knowledge_base.add_document(
    domain="LBO",
    document="LBO modeling involves projecting cash flows...",
    metadata={"source": "internal", "confidence": 0.95}
)

# Query knowledge base
results = knowledge_base.query(
    query="How to calculate exit multiple in LBO?",
    domain="LBO",
    max_results=3
)
```

## Memory Condensation System

To manage context length and maintain relevant information, the memory system includes a sophisticated condensation mechanism:

### Condenser Architecture

The `Condenser` base class provides the foundation for different condensation strategies:

```python
from backend.memory.condenser.condenser import Condenser
from backend.memory.condenser.impl.llm_condenser import LLMCondenser
from backend.memory.condenser.impl.financial_domain_condensers import LBOCondenser

# Base condenser
condenser = Condenser()

# LLM-based condenser
llm_condenser = LLMCondenser(openai_handler=openai_handler)

# Domain-specific condenser
lbo_condenser = LBOCondenser(openai_handler=openai_handler)
```

### Domain-Specific Condensers

The system includes specialized condensers for different financial domains:

- `LBOCondenser`: Specialized for Leveraged Buyout conversations
- `MACondenser`: Specialized for Mergers & Acquisitions conversations
- `DebtModelingCondenser`: Specialized for Debt Modeling conversations
- `PrivateLendingCondenser`: Specialized for Private Lending conversations

## Financial Domain Knowledge

The memory system includes components for detecting and retrieving domain-specific knowledge:

### Domain Detection

The `FinancialDomainDetector` identifies the financial domain of user queries:

```python
from backend.memory.knowledge.financial_domain_detector import FinancialDomainDetector

# Initialize domain detector
domain_detector = FinancialDomainDetector(api_key=openai_api_key)

# Detect domain
domain = domain_detector.detect_domain("How do I structure an LBO model?")
# Returns: "LBO"
```

### Knowledge Retrieval

The `KnowledgeRetriever` component retrieves relevant knowledge based on user queries:

```python
from backend.memory.knowledge.knowledge_retriever import KnowledgeRetriever

# Initialize knowledge retriever
knowledge_retriever = KnowledgeRetriever(
    knowledge_base=knowledge_base,
    domain_detector=domain_detector
)

# Retrieve knowledge
knowledge = knowledge_retriever.retrieve_for_query(
    query="How do I calculate the exit multiple?",
    domain="LBO"
)
```

## Integration with Core System

The memory system integrates with the core Cori system through a series of adapters:

- `EventAdapter`: Converts between core Event and memory Event models
- `MessageAdapter`: Converts between core Message and memory Event models
- `SessionAdapter`: Integrates with the core session persistence system
- `StateAdapter`: Integrates with the core state management system

See [ADAPTER_INTEGRATION.md](./ADAPTER_INTEGRATION.md) for details on the adapter pattern implementation.

## RAG-Enhanced OpenAI Integration

The memory system enhances the core OpenAI integration with RAG capabilities:

```python
from backend.memory.rag_enhanced_openai import RAGEnhancedOpenAIHandler

# Initialize RAG handler
rag_handler = RAGEnhancedOpenAIHandler(
    core_handler=openai_handler,
    conversation_memory=conversation_memory,
    long_term_memory=long_term_memory,
    knowledge_retriever=knowledge_retriever,
    domain_detector=domain_detector
)

# Get completion with RAG enhancement
response = rag_handler.get_completion(
    messages=messages,
    session_id="session_123"
)
```

## Thread Safety

All memory components are designed to be thread-safe, allowing for concurrent operations in a multi-user environment. Thread locks are used to protect shared resources, and atomic operations are used where possible.
