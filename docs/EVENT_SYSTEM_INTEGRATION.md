# Event System Integration Analysis

## Core Infrastructure Event System

The core infrastructure branch implements a sophisticated event system in `backend/core/event_system.py` that provides a pub/sub mechanism for decoupling components. This system is designed to facilitate communication between different parts of the application without creating tight coupling.

### Key Components

#### Event Class
```python
class Event:
    def __init__(self, event_type: str, data: Any = None):
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now().isoformat()
        self.id = None  # Will be set by EventBus when added
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "id": self.id,
            "type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create an Event instance from a dictionary."""
        event = cls(data["type"], data["data"])
        event.timestamp = data["timestamp"]
        event.id = data["id"]
        return event
```

#### EventBus Class
The `EventBus` class provides:
- Thread-safe event publishing and subscribing
- Event history tracking
- Event filtering capabilities
- Global singleton instance

```python
class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._history: List[Event] = []
        self._next_id = 0
        self._lock = threading.Lock()
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to events of a specific type."""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)
    
    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        with self._lock:
            # Assign ID and add to history
            event.id = self._next_id
            self._next_id += 1
            self._history.append(event)
            
            # Notify subscribers
            if event.event_type in self._subscribers:
                for callback in self._subscribers[event.event_type]:
                    try:
                        callback(event)
                    except Exception as e:
                        logger.error(f"Error in event subscriber: {e}")
```

## RAG++ Memory Event Model

The RAG++ memory system implements its own `Event` class in `backend/memory/models/event.py` that represents conversation events between the user and the system.

### Key Components

#### Event Class
```python
class Event:
    def __init__(
        self,
        id: Optional[str] = None,
        role: str = "user",
        content: str = "",
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.utcnow().isoformat() + "Z"
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        return cls(
            id=data.get("id"),
            role=data.get("role", "user"),
            content=data.get("content", ""),
            timestamp=data.get("timestamp"),
            metadata=data.get("metadata", {})
        )
```

## Integration Challenges

1. **Name Collision**: Both systems define an `Event` class with different structures and purposes.
2. **Different Focus**: 
   - Core Event: Generic event with type and data
   - RAG++ Event: Conversation event with role and content
3. **Different Usage Patterns**:
   - Core Event: Used for system-wide communication
   - RAG++ Event: Used for conversation history

## Integration Strategies

### 1. Adapter Pattern

Create an adapter that converts between the two event models:

```python
class EventAdapter:
    @staticmethod
    def rag_to_core(rag_event: memory.models.event.Event) -> core.event_system.Event:
        """Convert a RAG++ Event to a Core Event."""
        return core.event_system.Event(
            event_type="conversation",
            data={
                "role": rag_event.role,
                "content": rag_event.content,
                "metadata": rag_event.metadata,
                "original_id": rag_event.id,
                "original_timestamp": rag_event.timestamp
            }
        )
    
    @staticmethod
    def core_to_rag(core_event: core.event_system.Event) -> Optional[memory.models.event.Event]:
        """Convert a Core Event to a RAG++ Event if possible."""
        if core_event.event_type != "conversation" or not isinstance(core_event.data, dict):
            return None
        
        data = core_event.data
        return memory.models.event.Event(
            id=data.get("original_id"),
            role=data.get("role", "system"),
            content=data.get("content", ""),
            timestamp=data.get("original_timestamp"),
            metadata=data.get("metadata", {})
        )
```

### 2. Namespace Resolution

Ensure proper imports and use fully qualified names when needed:

```python
# When using both event types in the same file
import backend.core.event_system as core_events
import backend.memory.models.event as memory_events

# Create core event
core_event = core_events.Event("knowledge_retrieved", {"query": "LBO model"})

# Create memory event
memory_event = memory_events.Event(role="user", content="How do I build an LBO model?")
```

### 3. Event Type Definition

Define standard event types for RAG++ operations:

```python
# RAG++ Event Types
RAG_KNOWLEDGE_RETRIEVED = "rag_knowledge_retrieved"
RAG_MEMORY_CONDENSED = "rag_memory_condensed"
RAG_CONTEXT_INJECTED = "rag_context_injected"
RAG_DOMAIN_DETECTED = "rag_domain_detected"
RAG_USER_PREFERENCE_UPDATED = "rag_user_preference_updated"
```

### 4. EventBus Integration

Modify RAG++ components to publish events to the core EventBus:

```python
from backend.core.event_system import event_bus

class KnowledgeRetriever:
    def retrieve_for_query(self, query: str, domain: Optional[str] = None, topic: Optional[str] = None, k: int = 5) -> str:
        # Search for knowledge
        results = self.financial_knowledge_base.search_knowledge(
            query=query,
            domain=domain,
            topic=topic,
            k=k
        )
        
        # Publish event
        event_bus.publish(Event(
            event_type="rag_knowledge_retrieved",
            data={
                "query": query,
                "domain": domain,
                "topic": topic,
                "result_count": len(results)
            }
        ))
        
        # Format results
        # ...
```

## Recommended Integration Approach

1. **Keep Both Event Models**: Maintain both event models for their specific purposes
2. **Use Adapter Pattern**: Create adapters for converting between models when needed
3. **Publish RAG++ Events**: Have RAG++ components publish events to the core EventBus
4. **Subscribe to Core Events**: Have RAG++ components subscribe to relevant core events
5. **Define Standard Event Types**: Create a standard set of event types for RAG++ operations

## Example Integration

```python
# In RAG++ initialization
from backend.core.event_system import event_bus, Event as CoreEvent

# Subscribe to relevant core events
event_bus.subscribe("user_message", handle_user_message)
event_bus.subscribe("session_created", initialize_rag_memory)
event_bus.subscribe("agent_state_changed", handle_agent_state_change)

# Publish RAG++ events
def handle_user_message(event: CoreEvent):
    # Process user message
    # ...
    
    # Detect domain
    domain = domain_detector.detect(event.data["content"])
    
    # Publish domain detection event
    event_bus.publish(CoreEvent(
        event_type="rag_domain_detected",
        data={"domain": domain, "confidence": 0.85}
    ))
```

## Conclusion

The integration of the core event system with the RAG++ memory system requires careful handling of the different event models and their purposes. By using the adapter pattern and properly subscribing to and publishing events, we can leverage the robust event system provided by the core infrastructure while maintaining the specialized functionality of the RAG++ memory system.
