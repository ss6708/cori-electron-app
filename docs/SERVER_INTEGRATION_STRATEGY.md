# Server Integration Strategy

This document outlines the strategy for integrating the RAG++ memory system with the existing server implementation in the core infrastructure branch.

## Current Server Implementation

The current server implementation in `backend/server.py` provides a simple Flask API for chat completions using the core `OpenAIHandler`. The server initializes the handler, processes incoming messages, and returns responses.

## Integration Goals

1. Initialize RAG++ components in the server
2. Register event handlers for RAG++ operations
3. Extend API endpoints to support RAG++ functionality
4. Maintain backward compatibility with existing endpoints

## Component Initialization

### 1. Initialize Core Components

```python
from backend.core.event_system import event_bus
from backend.core.state_management import state_controller
from backend.core.session_persistence import session_manager
from backend.ai_services.openai_handler import OpenAIHandler

# Initialize core components
regular_openai_handler = OpenAIHandler()
```

### 2. Initialize RAG++ Components

```python
from backend.memory.knowledge.financial_knowledge_base import FinancialKnowledgeBase
from backend.memory.knowledge.financial_domain_detector import FinancialDomainDetector
from backend.memory.knowledge.knowledge_retriever import KnowledgeRetriever
from backend.memory.conversation_memory import ConversationMemory
from backend.memory.long_term_memory import LongTermMemory
from backend.memory.rag_enhanced_openai import RAGEnhancedOpenAI

# Initialize knowledge components
knowledge_base = FinancialKnowledgeBase()
domain_detector = FinancialDomainDetector()
knowledge_retriever = KnowledgeRetriever(financial_knowledge_base=knowledge_base)

# Initialize memory components
conversation_memory = ConversationMemory()
long_term_memory = LongTermMemory()

# Initialize RAG-enhanced OpenAI handler
rag_openai_handler = RAGEnhancedOpenAI(
    model="gpt-4o",
    conversation_memory=conversation_memory,
    long_term_memory=long_term_memory,
    knowledge_base=knowledge_base,
    domain_detector=domain_detector
)
```

### 3. Initialize Adapter Components

```python
from backend.integration.adapters.event_adapter import EventAdapter
from backend.integration.adapters.message_adapter import MessageAdapter
from backend.integration.adapters.session_adapter import SessionAdapter
from backend.integration.composite_openai_handler import CompositeOpenAIHandler

# Initialize adapters
message_adapter = MessageAdapter()
event_adapter = EventAdapter()
session_adapter = SessionAdapter(
    session_manager=session_manager,
    conversation_memory=conversation_memory
)

# Initialize composite handler
openai_handler = CompositeOpenAIHandler(
    regular_handler=regular_openai_handler,
    rag_handler=rag_openai_handler
)
```

## Event Handler Registration

### 1. Define Event Types

```python
# Define RAG-specific event types
RAG_DOMAIN_DETECTED = "rag_domain_detected"
RAG_KNOWLEDGE_RETRIEVED = "rag_knowledge_retrieved"
RAG_CONTEXT_INJECTED = "rag_context_injected"
RAG_MEMORY_CONDENSED = "rag_memory_condensed"
```

### 2. Register Event Handlers

```python
def initialize_event_handlers():
    """Initialize event handlers for RAG++ operations."""
    # Subscribe to message events
    event_bus.subscribe("message_received", handle_message_received)
    event_bus.subscribe("session_created", initialize_rag_session)
    event_bus.subscribe("agent_state_changed", handle_agent_state_change)

def handle_message_received(event):
    """Handle message received event."""
    if "message" not in event.data or "session_id" not in event.data:
        return
    
    message = event.data["message"]
    session_id = event.data["session_id"]
    
    # Detect domain
    domain, confidence = domain_detector.detect_domain(message.content)
    
    # Publish domain detection event
    event_bus.publish(Event(
        event_type=RAG_DOMAIN_DETECTED,
        data={
            "session_id": session_id,
            "domain": domain,
            "confidence": confidence
        }
    ))
    
    # Retrieve knowledge
    if knowledge_retriever:
        knowledge = knowledge_retriever.retrieve_for_query(
            query=message.content,
            domain=domain,
            k=5
        )
        
        # Publish knowledge retrieved event
        event_bus.publish(Event(
            event_type=RAG_KNOWLEDGE_RETRIEVED,
            data={
                "session_id": session_id,
                "query": message.content,
                "domain": domain,
                "knowledge": knowledge
            }
        ))

def initialize_rag_session(event):
    """Initialize RAG session when a new session is created."""
    if "session_id" not in event.data:
        return
    
    session_id = event.data["session_id"]
    
    # Initialize conversation memory for the session
    conversation_memory.initialize_session(session_id)
    
    # Sync session to memory
    session_adapter.sync_session_to_memory(session_id)

def handle_agent_state_change(event):
    """Handle agent state change event."""
    if "to_state" not in event.data or "session_id" not in event.data:
        return
    
    to_state = event.data["to_state"]
    session_id = event.data["session_id"]
    
    # Handle different states
    if to_state == "analyzing":
        # Trigger domain detection and knowledge retrieval
        pass
    elif to_state == "planning":
        # Prepare RAG context for planning
        pass
    elif to_state == "executing":
        # Use RAG context for response generation
        pass
    elif to_state == "reviewing":
        # Process feedback and update memory
        pass
    elif to_state == "idle":
        # Condense memory during idle time
        conversation_memory.condense_session(session_id)
```

## API Endpoint Extensions

### 1. Extend Chat Endpoint

```python
@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint with RAG capabilities."""
    try:
        # Get request data
        data = request.json
        
        if not data or 'messages' not in data:
            return jsonify({"error": "Invalid request. 'messages' field is required."}), 400
        
        # Get session ID
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Convert incoming messages to Message objects
        messages = [Message.from_dict(msg) for msg in data['messages']]
        
        # Determine whether to use RAG
        use_rag = data.get('use_rag', True)
        
        # Transition to ANALYZING state
        state_controller.set_state(
            AgentState.ANALYZING,
            metadata={"session_id": session_id}
        )
        
        # Get completion
        response = openai_handler.get_completion(
            messages=messages,
            model=data.get('model'),
            use_rag=use_rag
        )
        
        # Add message to session
        session_manager.add_message(session_id, response)
        
        # Transition to IDLE state
        state_controller.set_state(
            AgentState.IDLE,
            metadata={"session_id": session_id}
        )
        
        # Return the response
        return jsonify({
            "message": response.to_dict(),
            "session_id": session_id
        })
    
    except Exception as e:
        # Transition to ERROR state
        state_controller.set_state(
            AgentState.ERROR,
            metadata={"error": str(e)}
        )
        
        return jsonify({"error": str(e)}), 500
```

### 2. Add Domain Detection Endpoint

```python
@app.route('/detect_domain', methods=['POST'])
def detect_domain():
    """Detect financial domain in text."""
    try:
        # Get request data
        data = request.json
        
        if not data or 'text' not in data:
            return jsonify({"error": "Invalid request. 'text' field is required."}), 400
        
        # Detect domain
        domain, confidence = domain_detector.detect_domain(data['text'])
        
        # Return the domain
        return jsonify({
            "domain": domain,
            "confidence": confidence
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### 3. Add Knowledge Retrieval Endpoint

```python
@app.route('/retrieve_knowledge', methods=['POST'])
def retrieve_knowledge():
    """Retrieve knowledge for a query."""
    try:
        # Get request data
        data = request.json
        
        if not data or 'query' not in data:
            return jsonify({"error": "Invalid request. 'query' field is required."}), 400
        
        # Get parameters
        query = data['query']
        domain = data.get('domain')
        k = data.get('k', 5)
        
        # Retrieve knowledge
        knowledge = knowledge_retriever.retrieve_for_query(
            query=query,
            domain=domain,
            k=k
        )
        
        # Return the knowledge
        return jsonify({
            "knowledge": knowledge
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### 4. Add Memory Management Endpoints

```python
@app.route('/memory/condense', methods=['POST'])
def condense_memory():
    """Condense memory for a session."""
    try:
        # Get request data
        data = request.json
        
        if not data or 'session_id' not in data:
            return jsonify({"error": "Invalid request. 'session_id' field is required."}), 400
        
        # Condense memory
        conversation_memory.condense_session(data['session_id'])
        
        # Return success
        return jsonify({
            "success": True
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/memory/events', methods=['GET'])
def get_memory_events():
    """Get memory events for a session."""
    try:
        # Get session ID
        session_id = request.args.get('session_id')
        
        if not session_id:
            return jsonify({"error": "Invalid request. 'session_id' parameter is required."}), 400
        
        # Get events
        events = conversation_memory.get_events(session_id)
        
        # Convert events to dictionaries
        event_dicts = [event.to_dict() for event in events]
        
        # Return the events
        return jsonify({
            "events": event_dicts
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

## Backward Compatibility

To maintain backward compatibility with existing endpoints, we need to ensure that:

1. The core `OpenAIHandler` is still available for use
2. The existing API endpoints continue to work as expected
3. New RAG functionality is optional and can be disabled

### 1. Maintain Original Handler

```python
# Keep the original handler available
original_openai_handler = OpenAIHandler()

# Use the composite handler by default
openai_handler = CompositeOpenAIHandler(
    regular_handler=original_openai_handler,
    rag_handler=rag_openai_handler
)
```

### 2. Add Compatibility Layer

```python
def get_completion_compatible(messages, model=None, use_rag=False):
    """
    Get a completion in a backward-compatible way.
    
    Args:
        messages: List of Message objects
        model: Optional model override
        use_rag: Whether to use RAG enhancement
        
    Returns:
        Message: The assistant's response
    """
    if use_rag:
        return openai_handler.get_completion(messages, model, use_rag=True)
    else:
        return original_openai_handler.get_completion(messages, model)
```

### 3. Add Feature Flags

```python
# Feature flags
RAG_ENABLED = os.environ.get("RAG_ENABLED", "true").lower() == "true"
DOMAIN_DETECTION_ENABLED = os.environ.get("DOMAIN_DETECTION_ENABLED", "true").lower() == "true"
MEMORY_CONDENSING_ENABLED = os.environ.get("MEMORY_CONDENSING_ENABLED", "true").lower() == "true"

# Use feature flags in endpoints
@app.route('/chat', methods=['POST'])
def chat():
    # ...
    
    # Determine whether to use RAG based on feature flag
    use_rag = data.get('use_rag', RAG_ENABLED)
    
    # ...
```

## Error Handling

Implement robust error handling to ensure that failures in RAG components don't affect the core functionality:

```python
def safe_get_completion(messages, model=None, use_rag=False):
    """
    Get a completion with safe fallback.
    
    Args:
        messages: List of Message objects
        model: Optional model override
        use_rag: Whether to use RAG enhancement
        
    Returns:
        Message: The assistant's response
    """
    try:
        if use_rag:
            return openai_handler.get_completion(messages, model, use_rag=True)
        else:
            return original_openai_handler.get_completion(messages, model)
    except Exception as e:
        logger.error(f"Error in RAG-enhanced completion: {e}")
        # Fall back to regular handler
        return original_openai_handler.get_completion(messages, model)
```

## Logging and Monitoring

Add logging and monitoring for RAG operations:

```python
def initialize_rag_logging():
    """Initialize logging for RAG operations."""
    # Set up logger
    rag_logger = logging.getLogger("rag")
    rag_logger.setLevel(logging.INFO)
    
    # Create handler
    handler = logging.FileHandler("rag.log")
    handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Add handler to logger
    rag_logger.addHandler(handler)
    
    # Subscribe to RAG events for logging
    event_bus.subscribe(RAG_DOMAIN_DETECTED, log_rag_event)
    event_bus.subscribe(RAG_KNOWLEDGE_RETRIEVED, log_rag_event)
    event_bus.subscribe(RAG_CONTEXT_INJECTED, log_rag_event)
    event_bus.subscribe(RAG_MEMORY_CONDENSED, log_rag_event)

def log_rag_event(event):
    """Log RAG event."""
    rag_logger = logging.getLogger("rag")
    rag_logger.info(f"RAG event: {event.event_type}, data: {event.data}")
```

## Configuration Management

Add configuration management for RAG components:

```python
def load_rag_config():
    """Load RAG configuration from environment variables."""
    return {
        "enabled": os.environ.get("RAG_ENABLED", "true").lower() == "true",
        "model": os.environ.get("RAG_MODEL", "gpt-4o"),
        "temperature": float(os.environ.get("RAG_TEMPERATURE", "0.7")),
        "max_tokens": int(os.environ.get("RAG_MAX_TOKENS", "1024")),
        "domain_detection_enabled": os.environ.get("DOMAIN_DETECTION_ENABLED", "true").lower() == "true",
        "memory_condensing_enabled": os.environ.get("MEMORY_CONDENSING_ENABLED", "true").lower() == "true",
        "knowledge_items_per_query": int(os.environ.get("KNOWLEDGE_ITEMS_PER_QUERY", "5")),
        "confidence_threshold": float(os.environ.get("CONFIDENCE_THRESHOLD", "0.7"))
    }
```

## Complete Server Integration

Putting it all together, the complete server integration would look like:

```python
import os
import logging
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS

from backend.core.event_system import event_bus, Event
from backend.core.state_management import state_controller, AgentState
from backend.core.session_persistence import session_manager
from backend.models.message import Message
from backend.ai_services.openai_handler import OpenAIHandler

from backend.memory.knowledge.financial_knowledge_base import FinancialKnowledgeBase
from backend.memory.knowledge.financial_domain_detector import FinancialDomainDetector
from backend.memory.knowledge.knowledge_retriever import KnowledgeRetriever
from backend.memory.conversation_memory import ConversationMemory
from backend.memory.long_term_memory import LongTermMemory
from backend.memory.rag_enhanced_openai import RAGEnhancedOpenAI

from backend.integration.adapters.event_adapter import EventAdapter
from backend.integration.adapters.message_adapter import MessageAdapter
from backend.integration.adapters.session_adapter import SessionAdapter
from backend.integration.composite_openai_handler import CompositeOpenAIHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Define RAG-specific event types
RAG_DOMAIN_DETECTED = "rag_domain_detected"
RAG_KNOWLEDGE_RETRIEVED = "rag_knowledge_retrieved"
RAG_CONTEXT_INJECTED = "rag_context_injected"
RAG_MEMORY_CONDENSED = "rag_memory_condensed"

# Load configuration
rag_config = load_rag_config()

# Initialize core components
regular_openai_handler = OpenAIHandler()

# Initialize RAG components if enabled
if rag_config["enabled"]:
    # Initialize knowledge components
    knowledge_base = FinancialKnowledgeBase()
    domain_detector = FinancialDomainDetector()
    knowledge_retriever = KnowledgeRetriever(
        financial_knowledge_base=knowledge_base
    )
    
    # Initialize memory components
    conversation_memory = ConversationMemory()
    long_term_memory = LongTermMemory()
    
    # Initialize RAG-enhanced OpenAI handler
    rag_openai_handler = RAGEnhancedOpenAI(
        model=rag_config["model"],
        temperature=rag_config["temperature"],
        max_tokens=rag_config["max_tokens"],
        conversation_memory=conversation_memory,
        long_term_memory=long_term_memory,
        knowledge_base=knowledge_base,
        domain_detector=domain_detector
    )
    
    # Initialize adapters
    message_adapter = MessageAdapter()
    event_adapter = EventAdapter()
    session_adapter = SessionAdapter(
        session_manager=session_manager,
        conversation_memory=conversation_memory
    )
    
    # Initialize composite handler
    openai_handler = CompositeOpenAIHandler(
        regular_handler=regular_openai_handler,
        rag_handler=rag_openai_handler
    )
    
    # Initialize event handlers
    initialize_event_handlers()
    
    # Initialize logging
    initialize_rag_logging()
else:
    # Use regular handler if RAG is disabled
    openai_handler = regular_openai_handler

# Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint with RAG capabilities."""
    try:
        # Get request data
        data = request.json
        
        if not data or 'messages' not in data:
            return jsonify({"error": "Invalid request. 'messages' field is required."}), 400
        
        # Get session ID
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Convert incoming messages to Message objects
        messages = [Message.from_dict(msg) for msg in data['messages']]
        
        # Determine whether to use RAG
        use_rag = data.get('use_rag', rag_config["enabled"])
        
        # Transition to ANALYZING state
        state_controller.set_state(
            AgentState.ANALYZING,
            metadata={"session_id": session_id}
        )
        
        # Get completion
        response = safe_get_completion(
            messages=messages,
            model=data.get('model'),
            use_rag=use_rag
        )
        
        # Add message to session
        session_manager.add_message(session_id, response)
        
        # Transition to IDLE state
        state_controller.set_state(
            AgentState.IDLE,
            metadata={"session_id": session_id}
        )
        
        # Return the response
        return jsonify({
            "message": response.to_dict(),
            "session_id": session_id
        })
    
    except Exception as e:
        # Transition to ERROR state
        state_controller.set_state(
            AgentState.ERROR,
            metadata={"error": str(e)}
        )
        
        return jsonify({"error": str(e)}), 500

# Add other endpoints...

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
```

## Conclusion

This server integration strategy provides a comprehensive approach to integrating the RAG++ memory system with the existing server implementation. By using adapters, composition, and the event bus, we can create a flexible and maintainable architecture that leverages the strengths of both systems while maintaining backward compatibility.

The key aspects of this integration are:
1. Initializing both core and RAG++ components
2. Using adapters to bridge between different models
3. Leveraging the event bus for communication
4. Extending API endpoints to support RAG functionality
5. Maintaining backward compatibility with existing endpoints
6. Implementing robust error handling and logging
7. Adding configuration management for RAG components

This approach allows for a gradual integration of RAG++ capabilities while ensuring that the existing functionality continues to work as expected.
