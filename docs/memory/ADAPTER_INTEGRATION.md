# Memory System Adapter Integration

The Cori memory system uses the adapter pattern to integrate with the core application components. This document explains the adapter architecture and provides implementation details for each adapter.

## Adapter Pattern Overview

The adapter pattern allows components with incompatible interfaces to work together by creating a wrapper that translates between them. In the Cori application, adapters are used to convert between core system models and memory system models.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Core       │     │  Adapter    │     │  Memory     │
│  Component  │◄────┤  Component  │◄────┤  Component  │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Event Adapter

The `EventAdapter` converts between core `Event` objects and memory system `Event` objects.

### Key Features:
- Thread-safe conversion methods
- Batch conversion support
- Metadata preservation
- Support for specialized event types

### Implementation:

```python
from backend.memory.adapters.event_adapter import EventAdapter
from backend.core.event_system import Event as CoreEvent
from backend.memory.models.event import Event as MemoryEvent

# Initialize adapter
event_adapter = EventAdapter()

# Convert core Event to memory Event
memory_event = event_adapter.core_to_memory(core_event)

# Convert memory Event to core Event
core_event = event_adapter.memory_to_core(memory_event)

# Convert memory Event to RAG Event
rag_event = event_adapter.memory_to_rag(memory_event, user_id, session_id)

# Convert RAG Event to memory Event
memory_event = event_adapter.rag_to_memory(rag_event)

# Batch conversion
memory_events = event_adapter.batch_core_to_memory(core_events)
```

### Event Type Handling:

The adapter handles different event types through specialized conversion methods:

```python
# Memory Event types
from backend.memory.models.event import (
    UserMessageEvent,
    AssistantMessageEvent,
    SystemMessageEvent,
    CondensationEvent
)

# RAG Event types
from backend.memory.models.rag.event import (
    UserMessageEvent as RAGUserMessageEvent,
    AssistantMessageEvent as RAGAssistantMessageEvent,
    SystemMessageEvent as RAGSystemMessageEvent
)
```

## Message Adapter

The `MessageAdapter` converts between core `Message` objects and memory system `Event` objects.

### Key Features:
- OpenAI format conversion
- Metadata preservation
- Thread safety

### Implementation:

```python
from backend.memory.adapters.message_adapter import MessageAdapter
from backend.models.message import Message as CoreMessage
from backend.memory.models.event import Event as MemoryEvent

# Initialize adapter
message_adapter = MessageAdapter()

# Convert core Message to memory Event
memory_event = message_adapter.core_to_rag(core_message)

# Convert memory Event to core Message
core_message = message_adapter.rag_to_core(memory_event)

# Convert OpenAI format to memory Event
memory_event = message_adapter.openai_format_to_rag(openai_message)

# Convert memory Event to OpenAI format
openai_message = message_adapter.rag_to_openai_format(memory_event)
```

## Session Adapter

The `SessionAdapter` integrates the memory system with the core session persistence system.

### Key Features:
- Session creation and management
- Message synchronization
- State persistence

### Implementation:

```python
from backend.memory.adapters.session_adapter import SessionAdapter
from backend.core.session_persistence import SessionManager
from backend.memory.conversation_memory import ConversationMemory

# Initialize adapter
session_adapter = SessionAdapter(
    session_manager=session_manager,
    conversation_memory=conversation_memory
)

# Create session
session_id = session_adapter.create_session()

# Save session
session_adapter.save_session(
    session_id=session_id,
    messages=messages,
    state_controller=state_controller
)

# Load session
session_data = session_adapter.load_session(session_id)

# Sync messages to events
session_adapter.sync_messages_to_events(
    session_id=session_id,
    messages=messages
)

# Sync events to messages
messages = session_adapter.sync_events_to_messages(session_id)
```

## State Adapter

The `StateAdapter` integrates the memory system with the core state management system.

### Key Features:
- State-aware components
- State transition handling
- Context injection based on state

### Implementation:

```python
from backend.memory.adapters.state_adapter import StateAwareComponent, StateAwareRAGHandler
from backend.core.state_management import AgentStateController, AgentState

# Initialize state-aware component
state_aware_component = StateAwareComponent(state_controller)

# Initialize state-aware RAG handler
state_aware_handler = StateAwareRAGHandler(
    state_controller=state_controller,
    domain_detector=domain_detector,
    knowledge_retriever=knowledge_retriever,
    conversation_memory=conversation_memory,
    long_term_memory=long_term_memory
)
```

### State Transition Handling:

The state adapter responds to state transitions with specialized handlers:

```python
# State transition handlers
state_aware_handler.on_analyzing_state(metadata)
state_aware_handler.on_planning_state(metadata)
state_aware_handler.on_executing_state(metadata)
state_aware_handler.on_reviewing_state(metadata)
state_aware_handler.on_idle_state(metadata)
```

## Server Integration

The `RAGServerIntegration` component provides a unified interface for integrating all memory components with the server.

### Key Features:
- Component initialization and management
- Event handling
- Configuration management

### Implementation:

```python
from backend.memory.adapters.server_integration import RAGServerIntegration
from backend.core.state_management import AgentStateController

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

# Get session adapter
session_adapter = server_integration.get_session_adapter()

# Get state-aware handler
state_aware_handler = server_integration.get_state_aware_handler()

# Enable/disable RAG
server_integration.set_rag_enabled(True)
```

## Thread Safety Considerations

All adapters implement thread safety mechanisms to ensure proper operation in a concurrent environment:

1. **Lock-based synchronization**: Critical sections are protected with threading locks
2. **Atomic operations**: Where possible, operations are made atomic to prevent race conditions
3. **Immutable data**: Immutable data structures are used where appropriate to prevent modification during processing

Example of thread-safe implementation:

```python
import threading

class ThreadSafeAdapter:
    def __init__(self):
        self._lock = threading.Lock()
    
    def convert(self, data):
        with self._lock:
            # Perform thread-safe conversion
            result = self._convert_impl(data)
            return result
```

## Error Handling

Adapters implement robust error handling to ensure system stability:

1. **Graceful degradation**: If a memory component fails, the system falls back to core functionality
2. **Error logging**: Detailed error information is logged for debugging
3. **State recovery**: The system can recover from error states

Example of error handling:

```python
def convert_safely(self, data):
    try:
        return self.convert(data)
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        # Fall back to default behavior
        return self.create_default_result()
```
