# RAG++ Memory Retrieval System Architecture for Cori

This document outlines the architecture for Cori's advanced RAG++ memory retrieval system, designed to equip Cori with specialized financial expertise in complex transaction modeling.

## 1. System Architecture Overview

The RAG++ system follows a three-tier architecture:

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

### 1.1 Knowledge Base Layer

The foundation of the RAG++ system, responsible for storing and organizing:
- Financial domain expertise (LBOs, M&A, Debt Modeling, Private Lending)
- User preferences for specific financial modeling tasks
- Feedback data for continuous learning

### 1.2 Retrieval Layer

The intelligence of the RAG++ system, responsible for:
- Understanding user queries in financial context
- Retrieving relevant knowledge based on query and context
- Ranking and selecting the most appropriate information

### 1.3 Integration Layer

The connection to Cori's existing systems, responsible for:
- Integrating retrieved knowledge with OpenAI's capabilities
- Coordinating with agent orchestration for tool selection
- Connecting with Excel integration for financial modeling

## 2. Data Flow Architecture

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

## 3. Component Specifications

### 3.1 Knowledge Base Components

#### 3.1.1 Vector Database (Chroma)

Chroma DB will store embeddings of financial knowledge with the following structure:
- Collections for different financial domains
- Document chunks with semantic metadata
- Embedding vectors for similarity search

#### 3.1.2 User Preference Storage

A structured database to store:
- User-specific modeling preferences
- Task-specific configurations
- Historical preference patterns

#### 3.1.3 Feedback Learning System

A system to:
- Collect explicit and implicit feedback
- Update knowledge base based on feedback
- Improve retrieval mechanisms over time

### 3.2 Retrieval Components

#### 3.2.1 Query Understanding

Processes that:
- Analyze user intent in financial context
- Extract key financial concepts
- Formulate effective retrieval queries

#### 3.2.2 Context-Aware Retrieval

Mechanisms that:
- Consider conversation history
- Incorporate Excel model context
- Adapt to user's financial domain focus

#### 3.2.3 Hybrid Retrieval & Reranking

Advanced retrieval combining:
- Dense retrieval (vector similarity)
- Sparse retrieval (keyword matching)
- Reranking based on relevance and context

### 3.3 Integration Components

#### 3.3.1 OpenAI Handler Integration

Extensions to the existing OpenAI handler to:
- Inject retrieved knowledge into prompts
- Manage context window efficiently
- Apply financial domain-specific system prompts

#### 3.3.2 Agent Orchestration Integration

Connections to the agent system to:
- Select appropriate financial tools
- Plan multi-step financial analyses
- Validate results against financial principles

#### 3.3.3 Excel Tool Integration

Interfaces with Excel functionality to:
- Apply financial knowledge to models
- Extract context from current Excel state
- Validate financial calculations

## 4. Technical Implementation Considerations

### 4.1 Vector Database Selection

Chroma DB is selected for the following reasons:
- Python-native implementation for easy integration
- Support for metadata filtering
- Lightweight deployment requirements
- Open-source with active community

### 4.2 Embedding Strategy

The system will use:
- OpenAI's text-embedding-3-large model
- Chunk size of 1000-1500 tokens for financial concepts
- Overlap of 200 tokens to maintain context
- Metadata enrichment for financial domain context

### 4.3 Retrieval Enhancements

The system will implement:
- Hypothetical Document Embeddings (HyDE) for complex queries
- Maximum Marginal Relevance (MMR) for diverse retrievals
- Recursive retrieval for multi-step financial analyses

### 4.4 Performance Optimizations

The system will include:
- Caching for frequently accessed financial knowledge
- Batched embedding generation
- Incremental knowledge base updates

## 5. Integration with Existing Codebase

The RAG++ system will integrate with Cori's existing architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Cori Electron App                           │
│                                                                 │
│  ┌─────────────────┐                      ┌─────────────────┐   │
│  │  Next.js        │                      │  Electron       │   │
│  │  Frontend       │◄────────────────────►│  Wrapper        │   │
│  └─────────────────┘                      └─────────────────┘   │
│           │                                                     │
│           │ HTTP/API                                            │
│           ▼                                                     │
│  ┌─────────────────┐                      ┌─────────────────┐   │
│  │  Flask Backend  │                      │  Excel          │   │
│  │  Server         │◄────────────────────►│  Integration    │   │
│  └─────────────────┘                      └─────────────────┘   │
│           │                                                     │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   RAG++ System                           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 5.1 Backend Integration Points

The RAG++ system will integrate with:
- `backend/server.py` for new API endpoints
- `backend/ai_services/openai_handler.py` for knowledge injection
- New modules for knowledge management and retrieval

### 5.2 API Extensions

New API endpoints will be added to support:
- Knowledge base management
- User preference storage and retrieval
- Feedback collection and processing

## 6. Conclusion

This architecture provides a comprehensive framework for implementing an advanced RAG++ memory retrieval system for Cori, enabling it to leverage specialized financial knowledge, adapt to user preferences, and continuously improve through feedback learning.
