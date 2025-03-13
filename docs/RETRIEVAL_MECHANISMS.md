# Retrieval Mechanisms Design for Cori RAG++ System

This document outlines the design of the advanced retrieval mechanisms for Cori's RAG++ memory retrieval system, focusing on how financial expertise will be retrieved and ranked to provide the most relevant context for user queries.

## 1. Retrieval Architecture Overview

The retrieval system follows a multi-stage architecture designed to maximize both relevance and diversity of retrieved information:

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Query       │    │  Retrieval   │    │  Reranking   │    │  Context     │
│Understanding │───►│  Execution   │───►│  & Filtering │───►│  Assembly    │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
        │                  ▲                   ▲                   │
        │                  │                   │                   │
        ▼                  │                   │                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Query       │    │  Knowledge   │    │  User        │    │  Response    │
│Transformation│    │  Base        │    │  Context     │    │  Generation  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

## 2. Query Understanding

### 2.1 Financial Intent Recognition

The system will implement specialized financial intent recognition:

- **Transaction Type Classification**
  - Identify if query relates to LBO, M&A, debt modeling, or private lending
  - Detect specific transaction sub-types (e.g., strategic vs. financial acquisition)
  - Recognize modeling stage (e.g., initial structuring, sensitivity analysis, exit planning)

- **Financial Concept Extraction**
  - Identify key financial terms and concepts in the query
  - Extract numerical parameters and constraints
  - Recognize financial formulas and calculations

- **Task Identification**
  - Determine if user is asking for explanation, calculation, model building, or analysis
  - Identify specific financial analysis techniques being requested
  - Detect multi-step financial modeling tasks

### 2.2 Query Expansion

To improve retrieval quality, the system will implement:

- **Financial Synonym Expansion**
  - Expand financial abbreviations (e.g., "EBITDA" → "Earnings Before Interest, Taxes, Depreciation, and Amortization")
  - Include alternative financial terminology (e.g., "leverage" → "debt-to-equity ratio")
  - Add domain-specific synonyms (e.g., "multiple" → "valuation multiple", "EV/EBITDA")

- **Concept Hierarchy Expansion**
  - Include parent concepts (e.g., "IRR calculation" → "returns analysis")
  - Add related sub-concepts (e.g., "debt sizing" → "leverage ratios", "coverage ratios")
  - Incorporate prerequisite concepts (e.g., "LBO returns" → "entry multiple", "exit multiple")

### 2.3 Hypothetical Document Embeddings (HyDE)

The system will implement HyDE to improve retrieval for complex financial queries:

1. **Hypothetical Document Generation**
   - Generate an ideal document that would answer the user's financial query
   - Include domain-specific financial terminology and concepts
   - Structure the document according to financial analysis conventions

2. **Embedding Generation**
   - Create embeddings for the hypothetical document
   - Use these embeddings for retrieval instead of direct query embeddings
   - Maintain both query and HyDE embeddings for hybrid retrieval

3. **Financial Domain Adaptation**
   - Customize HyDE generation for each financial domain
   - Include domain-specific structures and terminology
   - Adapt to complexity level based on user history

Example HyDE implementation for an LBO query:
```python
def generate_hyde_document(query):
    prompt = f"""
    Generate a detailed financial document that would perfectly answer this query about leveraged buyouts:
    
    "{query}"
    
    Include relevant LBO concepts, formulas, and best practices. Structure the document as a professional financial analysis would.
    """
    
    hyde_document = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1000
    ).choices[0].message.content
    
    return hyde_document
```

## 3. Hybrid Retrieval Implementation

### 3.1 Dense Retrieval (Vector Similarity)

The system will implement vector-based retrieval using:

- **Embedding Models**
  - Primary: OpenAI's text-embedding-3-large (3072 dimensions)
  - Fallback: Smaller models for performance optimization when needed

- **Similarity Metrics**
  - Cosine similarity (primary metric)
  - Dot product (alternative for specific use cases)
  - Euclidean distance (for certain financial concept mappings)

- **ANN Search Optimization**
  - Approximate Nearest Neighbor search for performance
  - HNSW (Hierarchical Navigable Small World) indexing
  - Optimized for financial domain queries

### 3.2 Sparse Retrieval (Keyword Matching)

To complement vector retrieval, the system will implement:

- **BM25 Implementation**
  - Specialized financial term weighting
  - Domain-specific stopword filtering
  - Financial n-gram support

- **Financial Keyword Extraction**
  - Technical financial term identification
  - Formula and equation pattern matching
  - Numerical parameter extraction

- **Metadata Filtering**
  - Domain filtering (LBO, M&A, debt, lending)
  - Concept type filtering (formula, process, principle)
  - Complexity level filtering

### 3.3 Hybrid Retrieval Fusion

The system will combine dense and sparse retrieval through:

- **Reciprocal Rank Fusion**
  - Combine rankings from vector and keyword searches
  - Apply domain-specific weighting factors
  - Adjust fusion parameters based on query type

- **Weighted Interpolation**
  - Linear combination of similarity scores
  - Dynamic weighting based on query characteristics
  - Confidence-based score adjustment

- **Ensemble Methods**
  - Multiple retrieval strategies in parallel
  - Voting mechanisms for result selection
  - Confidence-based ensemble weighting

Example hybrid retrieval implementation:
```python
def hybrid_retrieval(query, hyde_document=None, top_k=10):
    # Dense retrieval
    query_embedding = get_embedding(query)
    hyde_embedding = get_embedding(hyde_document) if hyde_document else None
    
    # Use HyDE embedding if available, otherwise use query embedding
    search_embedding = hyde_embedding if hyde_embedding else query_embedding
    
    # Vector search
    vector_results = chroma_client.collection('financial_knowledge').query(
        query_embeddings=[search_embedding],
        n_results=top_k*2
    )
    
    # Sparse search (BM25)
    sparse_results = bm25_search(query, top_k=top_k*2)
    
    # Fusion using reciprocal rank
    fused_results = reciprocal_rank_fusion(vector_results, sparse_results)
    
    return fused_results[:top_k]
```

## 4. Context-Aware Retrieval

### 4.1 User Session History Awareness

The system will incorporate conversation history through:

- **Conversation Memory**
  - Maintain rolling window of recent interactions
  - Extract key financial concepts from conversation
  - Track financial domain focus over time

- **Query Contextualization**
  - Resolve pronouns and references to previous concepts
  - Maintain context of financial analysis being performed
  - Track variables and parameters mentioned earlier

- **Progressive Disclosure**
  - Track which financial concepts have been explained
  - Adjust complexity level based on previous interactions
  - Build on previously established financial knowledge

### 4.2 Excel Model Context Integration

The system will integrate with Excel model state:

- **Model Structure Awareness**
  - Understand current Excel model structure
  - Identify key sections (assumptions, calculations, outputs)
  - Recognize financial modeling patterns in use

- **Formula Context**
  - Extract and understand formulas in active cells
  - Identify financial calculations being performed
  - Recognize standard financial modeling conventions

- **Data Context**
  - Incorporate numerical values from relevant cells
  - Understand data relationships and dependencies
  - Recognize financial ratios and metrics in the model

### 4.3 Financial Domain Detection

The system will dynamically detect and adapt to financial domains:

- **Domain Classification**
  - Classify queries into LBO, M&A, debt modeling, or private lending
  - Detect multi-domain queries
  - Identify domain-specific terminology

- **Sub-domain Specialization**
  - Recognize specific transaction types
  - Identify particular modeling techniques
  - Detect specialized financial analyses

- **Domain-Specific Retrieval Adjustment**
  - Prioritize domain-specific knowledge
  - Apply domain-specific reranking criteria
  - Adjust retrieval parameters by domain

## 5. Reranking and Filtering

### 5.1 Maximum Marginal Relevance (MMR)

The system will implement MMR to balance relevance and diversity:

- **Diversity-Relevance Tradeoff**
  - λ parameter to balance relevance vs. diversity
  - Dynamic adjustment based on query complexity
  - Domain-specific optimization

- **Financial Knowledge Diversity**
  - Ensure coverage of different aspects of financial concepts
  - Include both theoretical explanations and practical applications
  - Balance formulas, processes, and principles

- **Complexity Diversity**
  - Include both fundamental and advanced explanations
  - Provide both detailed and summary information
  - Balance technical and conceptual knowledge

Example MMR implementation:
```python
def mmr_reranking(query_embedding, candidate_embeddings, candidate_docs, lambda_param=0.5, top_k=5):
    """
    Rerank candidates using Maximum Marginal Relevance.
    - query_embedding: embedding of the query
    - candidate_embeddings: list of embeddings for candidate documents
    - candidate_docs: list of candidate documents
    - lambda_param: balance between relevance and diversity (0-1)
    - top_k: number of documents to return
    """
    # Initialize selected documents and their embeddings
    selected = []
    selected_embeddings = []
    
    # Calculate initial similarity scores
    similarities = [cosine_similarity(query_embedding, doc_embedding) 
                   for doc_embedding in candidate_embeddings]
    
    # Select documents iteratively
    while len(selected) < top_k and candidate_docs:
        # Calculate MMR scores
        mmr_scores = []
        for i, doc_embedding in enumerate(candidate_embeddings):
            if i in selected:
                continue
                
            # Relevance term
            relevance = similarities[i]
            
            # Diversity term
            if not selected_embeddings:
                diversity = 0
            else:
                diversity = max([cosine_similarity(doc_embedding, sel_embedding) 
                               for sel_embedding in selected_embeddings])
            
            # MMR score
            mmr_score = lambda_param * relevance - (1 - lambda_param) * diversity
            mmr_scores.append((i, mmr_score))
        
        # Get document with highest MMR score
        next_idx, _ = max(mmr_scores, key=lambda x: x[1])
        
        # Add to selected
        selected.append(next_idx)
        selected_embeddings.append(candidate_embeddings[next_idx])
    
    # Return selected documents
    return [candidate_docs[i] for i in selected]
```

### 5.2 Cross-Encoder Reranking

For high-precision reranking, the system will implement:

- **Query-Document Pair Scoring**
  - Fine-tuned cross-encoder for financial domain
  - Joint encoding of query and candidate documents
  - High-precision relevance scoring

- **Financial Relevance Features**
  - Concept match scoring
  - Formula relevance assessment
  - Numerical parameter alignment

- **Two-Stage Retrieval**
  - Initial retrieval with hybrid approach
  - Secondary reranking with cross-encoder
  - Performance optimization through candidate pruning

### 5.3 User Preference Filtering

The system will incorporate user preferences:

- **Explicit Preference Application**
  - Filter based on stored user preferences
  - Apply domain-specific preferences
  - Respect complexity level preferences

- **Implicit Preference Learning**
  - Track which retrieved documents were useful
  - Learn from user interaction patterns
  - Adjust retrieval based on historical success

- **Preference Conflict Resolution**
  - Prioritize recent preferences
  - Apply task-specific preference overrides
  - Balance general and specific preferences

## 6. Recursive Retrieval for Complex Queries

### 6.1 Multi-Step Retrieval Process

For complex financial analyses, the system will implement:

- **Decomposition of Complex Queries**
  - Break down multi-part financial questions
  - Identify component concepts and calculations
  - Create retrieval plan for each component

- **Sequential Retrieval**
  - Retrieve information for each sub-query
  - Use retrieved information to inform subsequent retrievals
  - Build comprehensive context progressively

- **Knowledge Synthesis**
  - Combine information from multiple retrievals
  - Resolve conflicts and inconsistencies
  - Create coherent integrated context

### 6.2 Tree-of-Thought Retrieval

For complex reasoning chains, the system will implement:

- **Retrieval Trees**
  - Generate multiple retrieval paths
  - Explore alternative financial concepts
  - Prune irrelevant branches

- **Reasoning-Enhanced Retrieval**
  - Use intermediate reasoning to guide retrieval
  - Generate hypotheses about relevant knowledge
  - Validate retrieved information against reasoning

- **Path Selection**
  - Evaluate quality of different retrieval paths
  - Select most coherent and relevant path
  - Combine insights from multiple paths when beneficial

### 6.3 Retrieval-Augmented Generation Loop

The system will implement iterative retrieval and generation:

- **Initial Retrieval**
  - Retrieve baseline knowledge for query
  - Identify knowledge gaps and uncertainties
  - Determine additional retrieval needs

- **Generation-Guided Retrieval**
  - Generate partial response based on initial retrieval
  - Identify specific additional knowledge needed
  - Perform targeted follow-up retrievals

- **Iterative Refinement**
  - Incorporate new retrievals into context
  - Refine response based on complete knowledge
  - Repeat until response quality threshold is met

## 7. Performance Optimization

### 7.1 Caching Strategies

The system will implement multi-level caching:

- **Query-Result Caching**
  - Cache frequent financial queries and their results
  - Implement time-based cache invalidation
  - Support partial cache hits

- **Embedding Caching**
  - Cache embeddings for common financial terms
  - Precompute embeddings for core financial concepts
  - Implement efficient embedding lookup

- **Computation Caching**
  - Cache intermediate computation results
  - Store reranking scores for reuse
  - Implement LRU (Least Recently Used) cache eviction

### 7.2 Retrieval Tiering

For efficient resource utilization:

- **Progressive Retrieval Depth**
  - Start with lightweight retrieval for simple queries
  - Escalate to more complex retrieval as needed
  - Dynamically adjust retrieval depth based on query complexity

- **Retrieval Quality Thresholds**
  - Define confidence thresholds for retrieval quality
  - Stop retrieval when quality threshold is met
  - Escalate to more advanced techniques when quality is insufficient

- **Resource-Aware Retrieval**
  - Adjust retrieval complexity based on available resources
  - Implement fallback strategies for high-load situations
  - Balance retrieval quality and performance

### 7.3 Asynchronous Retrieval

For responsive user experience:

- **Background Retrieval**
  - Perform deep retrieval in background
  - Provide initial results quickly
  - Update with improved results as they become available

- **Predictive Retrieval**
  - Anticipate follow-up questions
  - Pre-retrieve likely needed information
  - Warm caches for expected queries

- **Parallel Retrieval Pipelines**
  - Execute multiple retrieval strategies in parallel
  - Combine results as they become available
  - Implement timeout mechanisms for slow retrievals

## 8. Implementation Considerations

### 8.1 Required Dependencies

```python
# Python dependencies for retrieval mechanisms
chromadb==0.4.18
openai==1.12.0
numpy==1.26.0
scikit-learn==1.3.0
rank_bm25==0.2.2
sentence_transformers==2.2.2
pydantic==2.5.2
python-dotenv==1.0.0
redis==5.0.1  # For caching
```

### 8.2 Directory Structure

```
backend/
├── retrieval/
│   ├── __init__.py
│   ├── query_understanding/
│   │   ├── __init__.py
│   │   ├── intent_recognizer.py
│   │   ├── query_expander.py
│   │   └── hyde_generator.py
│   ├── retrieval_engines/
│   │   ├── __init__.py
│   │   ├── vector_retriever.py
│   │   ├── sparse_retriever.py
│   │   └── hybrid_retriever.py
│   ├── context_awareness/
│   │   ├── __init__.py
│   │   ├── session_tracker.py
│   │   ├── excel_context.py
│   │   └── domain_detector.py
│   ├── reranking/
│   │   ├── __init__.py
│   │   ├── mmr_reranker.py
│   │   ├── cross_encoder.py
│   │   └── preference_filter.py
│   ├── recursive_retrieval/
│   │   ├── __init__.py
│   │   ├── query_decomposer.py
│   │   ├── tree_retriever.py
│   │   └── rag_loop.py
│   └── optimization/
│       ├── __init__.py
│       ├── cache_manager.py
│       ├── retrieval_tiering.py
│       └── async_retriever.py
```

## 9. Integration with Existing Codebase

### 9.1 OpenAI Handler Integration

The retrieval system will integrate with the existing OpenAI handler:

```python
# Pseudocode for integration with OpenAI handler
def enhanced_get_completion(self, messages: List[Message], model: Optional[str] = None) -> Message:
    # Extract the latest user query
    user_query = messages[-1].content if messages[-1].role == "user" else None
    
    if user_query:
        # Get conversation context
        conversation_context = self._extract_conversation_context(messages)
        
        # Get Excel context if available
        excel_context = self._get_excel_context()
        
        # Perform RAG retrieval
        retrieved_context = self.retrieval_system.retrieve(
            query=user_query,
            conversation_context=conversation_context,
            excel_context=excel_context
        )
        
        # Inject retrieved context into system message
        system_message = self._create_system_message_with_context(retrieved_context)
        
        # Add system message to the beginning of the messages
        augmented_messages = [system_message] + messages
    else:
        augmented_messages = messages
    
    # Call the original method with augmented messages
    response = self.client.chat.completions.create(
        model=model or self.model,
        messages=[msg.to_openai_format() for msg in augmented_messages],
        temperature=0.7,
        max_tokens=1024
    )
    
    return Message.from_openai_response(response)
```

### 9.2 API Endpoints

New API endpoints will be added to the Flask server:

```python
# Pseudocode for new API endpoints

@app.route('/retrieve', methods=['POST'])
def retrieve():
    """Perform knowledge retrieval for a query."""
    try:
        data = request.json
        
        if not data or 'query' not in data:
            return jsonify({"error": "Invalid request. 'query' field is required."}), 400
        
        query = data['query']
        conversation_context = data.get('conversation_context', [])
        excel_context = data.get('excel_context', {})
        
        # Perform retrieval
        retrieved_context = retrieval_system.retrieve(
            query=query,
            conversation_context=conversation_context,
            excel_context=excel_context
        )
        
        # Return the retrieved context
        return jsonify({"retrieved_context": retrieved_context})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    """Submit feedback on retrieval quality."""
    try:
        data = request.json
        
        if not data or 'query' not in data or 'retrieved_ids' not in data or 'feedback' not in data:
            return jsonify({"error": "Invalid request. 'query', 'retrieved_ids', and 'feedback' fields are required."}), 400
        
        # Process feedback
        retrieval_system.process_feedback(
            query=data['query'],
            retrieved_ids=data['retrieved_ids'],
            feedback=data['feedback']
        )
        
        return jsonify({"message": "Feedback processed successfully"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

## 10. Conclusion

This retrieval mechanisms design provides a comprehensive framework for implementing advanced, context-aware retrieval of financial expertise in Cori's RAG++ system. The hybrid approach combining vector similarity, keyword matching, and sophisticated reranking ensures that the most relevant financial knowledge is retrieved for each user query, while the context-aware features ensure that the system adapts to the user's specific financial domain, conversation history, and Excel model context.
