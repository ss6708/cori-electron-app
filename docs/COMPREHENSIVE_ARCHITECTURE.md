# Comprehensive Architecture for Cori RAG++ System

This document provides a complete architectural blueprint for Cori's RAG++ memory retrieval system, integrating all components designed to equip Cori with specialized financial expertise in complex transaction modeling.

## 1. Executive Summary

The Cori RAG++ system enhances Cori's capabilities as an expert financial modeling assistant through:

1. **Advanced Knowledge Management**: Storing and retrieving specialized financial knowledge about LBOs, M&A, debt modeling, and private lending
2. **Personalized User Experience**: Capturing and applying user preferences for financial modeling tasks
3. **Continuous Learning**: Collecting and integrating user feedback to improve system performance
4. **Intelligent Tool Orchestration**: Selecting and coordinating appropriate tools based on user intent

The architecture follows a three-tier design:

```
┌─────────────────────────────────────────────────────────────────┐
│                      Integration Layer                          │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  OpenAI Handler │  │ Agent Orchestra-│  │  Excel Tool     │  │
│  │  Integration    │  │ tion Integration│  │  Integration    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Retrieval Layer                           │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Query           │  │ Context-Aware   │  │ Hybrid Retrieval│  │
│  │ Understanding   │  │ Retrieval       │  │ & Reranking     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Knowledge Base Layer                        │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Vector Database │  │ User Preference │  │ Feedback        │  │
│  │ (Chroma)        │  │ Storage         │  │ Learning System │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Component Integration

### 2.1 Knowledge Base Layer Integration

The Knowledge Base Layer integrates three key components:

1. **Vector Database (Chroma DB)**: Stores financial domain expertise in specialized collections for LBOs, M&A, debt modeling, and private lending, with rich metadata for context-aware retrieval.

2. **User Preference Storage**: Maintains structured preferences for modeling approaches, analysis methods, visualization styles, and workflow patterns, enabling personalized experiences.

3. **Feedback Learning System**: Collects explicit and implicit feedback, analyzes patterns, and refines the knowledge base and retrieval strategies over time.

These components share a common database schema that enables cross-component data access and updates.

### 2.2 Retrieval Layer Integration

The Retrieval Layer integrates advanced mechanisms for knowledge access:

1. **Query Understanding**: Analyzes user intent through financial intent recognition, parameter extraction, and domain classification.

2. **Context-Aware Retrieval**: Incorporates conversation history, Excel model state, and user preferences into the retrieval process.

3. **Hybrid Retrieval & Reranking**: Combines dense vector similarity and sparse keyword matching, with Maximum Marginal Relevance (MMR) for diverse results.

These components work together to transform user queries into relevant financial knowledge retrieval.

### 2.3 Integration Layer Connections

The Integration Layer connects the RAG++ system to Cori's existing components:

1. **OpenAI Handler Integration**: Extends the existing handler with RAG context injection, domain-specific prompting, and token optimization.

2. **Agent Orchestration Integration**: Provides a framework for selecting and coordinating financial modeling tools based on user intent and retrieved knowledge.

3. **Excel Tool Integration**: Connects retrieved knowledge and selected tools to Excel operations for financial modeling tasks.

## 3. Data Flow Architecture

The RAG++ system processes user requests through the following flow:

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  User    │    │  Query   │    │ Knowledge│    │  OpenAI  │    │  Response│
│  Query   │───►│Processing│───►│ Retrieval│───►│Integration│───►│Generation│
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                      │               ▲               │               │
                      │               │               │               │
                      ▼               │               ▼               ▼
                ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
                │  User    │    │ Knowledge│    │  Tool    │    │  Feedback│
                │Preference│    │   Base   │    │ Selection│    │ Collection│
                │  Lookup  │    └──────────┘    └──────────┘    └──────────┘
                └──────────┘                         │               │
                                                     ▼               │
                                               ┌──────────┐          │
                                               │  Tool    │          │
                                               │Execution │          │
                                               └──────────┘          │
                                                     │               │
                                                     ▼               ▼
                                               ┌──────────────────────┐
                                               │  Learning System     │
                                               └──────────────────────┘
```

### 3.1 Query Processing Flow

1. User submits a query about financial modeling
2. System analyzes query intent and financial domain
3. User preferences are retrieved based on context
4. Knowledge base is queried using hybrid retrieval
5. Retrieved knowledge is formatted and injected into OpenAI prompt
6. OpenAI generates response with enhanced financial expertise
7. Response is delivered to user and feedback is collected

### 3.2 Tool Execution Flow

1. User submits a query requiring financial calculations
2. System identifies required financial tools
3. Knowledge base provides domain expertise for tool configuration
4. Agent orchestration selects and configures appropriate tools
5. Tools are executed with proper parameters
6. Results are validated against financial principles
7. Response is delivered to user with explanation and visualization

## 4. Key Component Specifications

### 4.1 Knowledge Base Components

#### 4.1.1 Vector Database (Chroma)

- **Collections**: Domain-specific collections for LBO, M&A, debt modeling, and private lending
- **Document Schema**: Rich metadata including domain, type, importance, and relationships
- **Embedding Model**: OpenAI's text-embedding-3-large with 3072 dimensions
- **Chunking Strategy**: Domain-specific chunking with 1200-1500 token size and 200-250 token overlap

#### 4.1.2 User Preference Storage

- **Preference Categories**: Modeling, analysis, visualization, and workflow preferences
- **Storage Schema**: Structured schema with preference type, category, key, value, and metadata
- **Preference Sources**: Explicit user settings and implicit pattern recognition
- **Context Adaptation**: Contextual preference application based on task and domain

#### 4.1.3 Feedback Learning System

- **Feedback Types**: Explicit ratings, corrections, and implicit interaction metrics
- **Analysis Methods**: Pattern recognition, impact assessment, and trend analysis
- **Learning Mechanisms**: Knowledge base refinement and retrieval strategy adjustment
- **Continuous Improvement**: Automated and expert-reviewed updates

### 4.2 Retrieval Components

#### 4.2.1 Query Understanding

- **Intent Recognition**: Financial task classification and parameter extraction
- **Domain Detection**: Identifying relevant financial domains (LBO, M&A, etc.)
- **Query Expansion**: Enhancing queries with financial terminology
- **Hypothetical Document Embeddings**: Generating synthetic documents for complex queries

#### 4.2.2 Context-Aware Retrieval

- **Context Sources**: Conversation history, Excel state, and user preferences
- **Context Integration**: Weighting and combining multiple context sources
- **Adaptive Retrieval**: Adjusting retrieval parameters based on context

#### 4.2.3 Hybrid Retrieval & Reranking

- **Dense Retrieval**: Vector similarity search using embeddings
- **Sparse Retrieval**: Keyword-based search for financial terms
- **Reranking Methods**: Maximum Marginal Relevance (MMR) for diversity
- **Recursive Retrieval**: Multi-step retrieval for complex queries

### 4.3 Integration Components

#### 4.3.1 OpenAI Handler Integration

- **RAG Context Injection**: Methods to inject retrieved knowledge into prompts
- **Domain-Specific Prompting**: Specialized system prompts for financial domains
- **Token Optimization**: Dynamic context window management and relevance filtering
- **Few-Shot Examples**: Domain-specific examples for improved responses

#### 4.3.2 Agent Orchestration Integration

- **Tool Registry**: Categorized financial and Excel tools with detailed metadata
- **Intent Mapping**: Mapping user intents to appropriate tools
- **Execution Planning**: Dependency analysis and parameter mapping
- **Result Validation**: Financial sanity checks and consistency validation

#### 4.3.3 Excel Tool Integration

- **Excel State Analysis**: Understanding current Excel model context
- **Formula Generation**: Creating financial formulas based on best practices
- **Model Structure**: Implementing financial modeling patterns
- **Visualization Creation**: Generating appropriate financial visualizations

## 5. API and Backend Integration

### 5.1 Backend API Extensions

The existing backend API will be extended with new endpoints:

- **Knowledge Base Management**: CRUD operations for knowledge entries
- **User Preference Management**: Setting and retrieving user preferences
- **Feedback Collection**: Submitting and analyzing feedback
- **Tool Execution**: Discovering and executing financial tools

### 5.2 Enhanced Chat Endpoint

The existing `/chat` endpoint will be enhanced to integrate with the RAG++ system:

```python
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = [Message(**msg) for msg in data.get('messages', [])]
    user_query = messages[-1].content if messages and messages[-1].role == "user" else ""
    
    # Extract context from request
    context = {
        "conversation_history": data.get('conversation_history', []),
        "excel_state": data.get('excel_state', {}),
        "user_preferences": get_user_preferences(data.get('preference_context', {}))
    }
    
    # Detect domain from query
    domain = detect_domain(user_query, context)
    
    # Get enhanced completion with RAG
    response = openai_handler.get_rag_enhanced_completion(
        messages=messages,
        user_query=user_query,
        context=context,
        domain=domain
    )
    
    # Record interaction for feedback learning
    record_interaction(user_query, response.content, context)
    
    return jsonify(response.to_dict())
```

## 6. Implementation Strategy

### 6.1 Phased Implementation

The RAG++ system will be implemented in phases:

1. **Phase 1: Knowledge Base Foundation**
   - Implement Chroma DB with basic collections
   - Create knowledge ingestion pipeline
   - Develop basic retrieval mechanisms

2. **Phase 2: Enhanced Retrieval**
   - Implement hybrid retrieval
   - Add context-aware capabilities
   - Integrate with OpenAI handler

3. **Phase 3: User Preferences & Feedback**
   - Implement preference storage and application
   - Develop feedback collection mechanisms
   - Create learning system for continuous improvement

4. **Phase 4: Tool Orchestration**
   - Implement tool registry
   - Develop intent understanding
   - Create execution planning

### 6.2 Required Dependencies

```
# Vector Database
chromadb==0.4.18
pydantic==2.5.2

# Embedding and Processing
openai==1.12.0
tiktoken==0.5.1
langchain==0.1.0
langchain-community==0.0.13

# Backend and API
flask==2.3.3
flask-cors==4.0.0
celery==5.3.4

# Database
sqlalchemy==2.0.23
alembic==1.12.1

# Testing
pytest==7.4.3
pytest-mock==3.12.0
```

### 6.3 Directory Structure

```
backend/
├── ai_services/
│   ├── openai_handler.py
│   └── extended_openai_handler.py
├── knowledge/
│   ├── vector_store.py
│   ├── ingestion_pipeline.py
│   └── retrieval_system.py
├── preferences/
│   ├── preference_manager.py
│   └── preference_store.py
├── feedback/
│   ├── feedback_collector.py
│   └── learning_system.py
├── agent_orchestration/
│   ├── tool_registry.py
│   ├── intent_parser.py
│   └── execution_planner.py
├── models/
│   ├── message.py
│   ├── knowledge_entry.py
│   └── user_preference.py
├── api/
│   ├── knowledge_api.py
│   ├── preference_api.py
│   ├── feedback_api.py
│   └── tool_api.py
└── server.py
```

## 7. Conclusion

This comprehensive architecture provides a complete blueprint for implementing Cori's RAG++ memory retrieval system. By integrating specialized financial knowledge, user preferences, and feedback learning with advanced retrieval mechanisms and tool orchestration, Cori will become a true expert system for complex financial transaction modeling.

The architecture is designed to be modular, extensible, and focused on the specific domains of LBOs, M&A, debt modeling, and private lending. It leverages the strengths of OpenAI's foundation models while enhancing them with domain-specific expertise and personalization.

Implementation of this architecture will transform Cori into a powerful financial modeling assistant that can adapt to user preferences, learn from interactions, and provide expert-level guidance for complex financial transactions.
