# RAG-Enhanced OpenAI Integration

The Cori application enhances the core OpenAI integration with Retrieval-Augmented Generation (RAG) capabilities. This document provides details on the RAG-enhanced OpenAI integration and usage examples.

## Overview

The `RAGEnhancedOpenAIHandler` extends the core `OpenAIHandler` with RAG capabilities, providing context-aware responses based on conversation history, long-term memory, and domain-specific knowledge.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  OpenAI     │     │  RAG        │     │  Memory     │
│  Handler    │◄────┤  Handler    │◄────┤  Components │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Key Components

### RAGEnhancedOpenAIHandler

The main component that integrates OpenAI with RAG capabilities:

```python
from backend.memory.rag_enhanced_openai import RAGEnhancedOpenAIHandler

# Initialize RAG handler
rag_handler = RAGEnhancedOpenAIHandler(
    core_handler=openai_handler,
    conversation_memory=conversation_memory,
    long_term_memory=long_term_memory,
    knowledge_retriever=knowledge_retriever,
    domain_detector=domain_detector,
    rag_enabled=True
)
```

### StateAwareRAGHandler

A state-aware version of the RAG handler that integrates with the core state management system:

```python
from backend.memory.adapters.state_adapter import StateAwareRAGHandler

# Initialize state-aware RAG handler
state_aware_handler = StateAwareRAGHandler(
    state_controller=state_controller,
    domain_detector=domain_detector,
    knowledge_retriever=knowledge_retriever,
    conversation_memory=conversation_memory,
    long_term_memory=long_term_memory
)
```

## Usage Examples

### Basic Usage

```python
# Get completion with RAG enhancement
response = rag_handler.get_completion(
    messages=[
        {"role": "user", "content": "How do I build an LBO model?"}
    ],
    session_id="session_123"
)

# Get streaming completion with RAG enhancement
for chunk in rag_handler.get_streaming_completion(
    messages=[
        {"role": "user", "content": "How do I build an LBO model?"}
    ],
    session_id="session_123"
):
    print(chunk.content, end="", flush=True)
```

### Domain-Specific Usage

```python
# Get completion with specific domain
response = rag_handler.get_completion(
    messages=[
        {"role": "user", "content": "How do I build an LBO model?"}
    ],
    session_id="session_123",
    domain="LBO"  # Explicitly specify domain
)
```

### Feedback Processing

```python
# Process user feedback
rag_handler.process_feedback(
    session_id="session_123",
    feedback="This response was very helpful for understanding LBO models.",
    rating=5
)
```

### Memory Condensation

```python
# Condense memory for a session
rag_handler.condense_memory("session_123")
```

### Disabling RAG

```python
# Disable RAG enhancement
rag_handler.rag_enabled = False

# Get completion without RAG enhancement
response = rag_handler.get_completion(
    messages=[
        {"role": "user", "content": "How do I build an LBO model?"}
    ],
    session_id="session_123"
)
```

## Integration with Server

```python
from backend.memory.adapters.server_integration import RAGServerIntegration

# Initialize server integration
server_integration = RAGServerIntegration(
    state_controller=state_controller,
    storage_dir="/path/to/storage",
    rag_enabled=True
)

# Initialize components
server_integration.initialize()

# Get RAG handler
rag_handler = server_integration.get_rag_handler()

# Enable/disable RAG
server_integration.set_rag_enabled(True)
```

## RAG Enhancement Process

The RAG enhancement process involves several steps:

1. **Domain Detection**: Identify the financial domain of the user query
2. **Knowledge Retrieval**: Retrieve relevant knowledge from the knowledge base
3. **Context Injection**: Inject retrieved knowledge into the prompt
4. **Response Generation**: Generate a response using the enhanced prompt
5. **Memory Update**: Update conversation and long-term memory with the interaction

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Domain     │     │  Knowledge  │     │  Context    │
│  Detection  │────►│  Retrieval  │────►│  Injection  │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Memory     │◄────│  Response   │◄────│  OpenAI     │
│  Update     │     │  Generation │     │  API        │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Event System Integration

The RAG handler integrates with the core event system to publish events related to RAG operations:

```python
# Event types
RAG_DOMAIN_DETECTED = "rag_domain_detected"
RAG_KNOWLEDGE_RETRIEVED = "rag_knowledge_retrieved"
RAG_CONTEXT_INJECTED = "rag_context_injected"
RAG_MEMORY_UPDATED = "rag_memory_updated"
RAG_MEMORY_CONDENSED = "rag_memory_condensed"

# Subscribe to events
event_bus.subscribe(RAG_DOMAIN_DETECTED, handle_domain_detected)
event_bus.subscribe(RAG_KNOWLEDGE_RETRIEVED, handle_knowledge_retrieved)
```

## Thread Safety

The RAG handler is designed to be thread-safe, allowing for concurrent operations in a multi-user environment:

```python
import threading

class ThreadSafeRAGHandler:
    def __init__(self):
        self._lock = threading.Lock()
    
    def get_completion(self, messages, session_id):
        with self._lock:
            # Perform thread-safe operations
            domain = self._detect_domain(messages)
            knowledge = self._retrieve_knowledge(domain, messages)
            enhanced_messages = self._inject_context(messages, knowledge)
            return self._get_completion_impl(enhanced_messages)
```

## Error Handling

The RAG handler implements robust error handling to ensure system stability:

```python
def get_completion_safely(self, messages, session_id):
    try:
        # Attempt RAG enhancement
        return self.get_completion_with_rag(messages, session_id)
    except Exception as e:
        logger.error(f"RAG enhancement failed: {e}")
        # Fall back to core handler
        return self.core_handler.get_completion(messages)
```

## Performance Considerations

The RAG handler includes optimizations for performance:

1. **Caching**: Frequently used knowledge is cached to reduce retrieval time
2. **Asynchronous operations**: Non-blocking operations for improved responsiveness
3. **Batch processing**: Efficient processing of multiple events
4. **Lazy loading**: Components are loaded only when needed

## Configuration Options

The RAG handler supports various configuration options:

```python
# Configure RAG handler
rag_handler = RAGEnhancedOpenAIHandler(
    core_handler=openai_handler,
    conversation_memory=conversation_memory,
    long_term_memory=long_term_memory,
    knowledge_retriever=knowledge_retriever,
    domain_detector=domain_detector,
    rag_enabled=True,
    max_context_tokens=1000,
    similarity_threshold=0.75,
    auto_condense=True,
    condense_threshold=20
)
```
