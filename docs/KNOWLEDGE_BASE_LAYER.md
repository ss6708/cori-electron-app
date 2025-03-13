# Knowledge Base Layer Design for Cori RAG++ System

This document details the design of the Knowledge Base Layer for Cori's RAG++ memory retrieval system, focusing on the storage and organization of financial expertise.

## 1. Vector Database Design

### 1.1 Database Selection: Chroma DB

Chroma DB has been selected as the vector database for the following reasons:

- **Python-native implementation**: Seamless integration with the existing Python backend
- **Lightweight deployment**: Can be embedded directly in the application without external services
- **Rich metadata support**: Allows for detailed tagging of financial knowledge
- **Active open-source community**: Regular updates and improvements
- **Simple API**: Easy to implement and maintain

### 1.2 Collection Structure

The Chroma DB implementation will use the following collection structure:

```
financial_knowledge/
├── lbo_knowledge/         # Leveraged Buyout expertise
├── ma_knowledge/          # Mergers & Acquisitions expertise
├── debt_modeling/         # Debt modeling expertise
└── private_lending/       # Private lending expertise
```

Each collection will store document chunks with their embeddings and associated metadata.

### 1.3 Document Schema

Each document in the vector database will follow this schema:

```python
{
    "id": "unique_document_id",
    "text": "The actual financial knowledge text chunk",
    "metadata": {
        "domain": "lbo|ma|debt|lending",
        "concept_type": "formula|process|principle|definition|example",
        "complexity": "beginner|intermediate|advanced",
        "source": "source of the knowledge",
        "last_updated": "timestamp",
        "confidence": 0.95,  # System confidence in the knowledge
        "related_concepts": ["concept1", "concept2"],
        "keywords": ["keyword1", "keyword2"]
    },
    "embedding": [...]  # Vector representation
}
```

### 1.4 Chunking Strategy

The knowledge base will implement the following chunking strategy:

- **Chunk size**: 1000-1500 tokens for financial concepts
  - Rationale: Financial concepts often require detailed explanation with formulas and examples
- **Overlap**: 200 tokens between chunks
  - Rationale: Ensures context continuity between related chunks
- **Semantic boundaries**: Chunks will respect semantic boundaries where possible
  - Rationale: Keeps related financial concepts together

### 1.5 Embedding Model

The system will use OpenAI's text-embedding-3-large model for generating embeddings:

- **Dimensions**: 3072
- **Quality**: State-of-the-art semantic understanding
- **Context window**: Supports up to 8191 tokens
- **Financial domain performance**: Strong performance on financial text

## 2. Financial Knowledge Organization

### 2.1 LBO Knowledge Collection

The LBO knowledge collection will focus on:

- LBO model structures and conventions
- Debt sizing and amortization schedules
- Exit multiple analysis
- Returns analysis (IRR, MOIC, etc.)
- Covenant compliance modeling

Example document:
```
{
    "id": "lbo-001",
    "text": "In LBO modeling, the debt sizing is typically calculated as a multiple of EBITDA. Common debt multiples range from 4-6x EBITDA depending on the industry, company stability, and market conditions. The debt package is usually structured in tranches with different priorities, interest rates, and amortization schedules...",
    "metadata": {
        "domain": "lbo",
        "concept_type": "principle",
        "complexity": "intermediate",
        "source": "expert_knowledge",
        "keywords": ["debt sizing", "EBITDA multiple", "tranches"]
    }
}
```

### 2.2 M&A Knowledge Collection

The M&A knowledge collection will focus on:

- Accretion/dilution analysis
- Synergy modeling
- Purchase price allocation
- Transaction structuring
- Pro forma financial statements

Example document:
```
{
    "id": "ma-001",
    "text": "Accretion/dilution analysis determines whether an acquisition will increase (accrete) or decrease (dilute) the acquirer's EPS. The calculation compares the pro forma EPS after the transaction to the standalone EPS. Key factors affecting accretion/dilution include purchase price, financing structure, synergies, and accounting treatments...",
    "metadata": {
        "domain": "ma",
        "concept_type": "process",
        "complexity": "advanced",
        "source": "expert_knowledge",
        "keywords": ["accretion", "dilution", "EPS", "pro forma"]
    }
}
```

### 2.3 Debt Modeling Collection

The debt modeling collection will focus on:

- Term loan structures
- Revolving credit facilities
- Interest rate modeling
- Debt covenant calculations
- Refinancing scenarios

Example document:
```
{
    "id": "debt-001",
    "text": "Term loans are typically amortized over a set period, with principal repayments made according to a predetermined schedule. The amortization schedule can be calculated using the formula: Principal Payment = Total Loan Amount / Number of Periods. For a $100M term loan with a 5-year maturity and quarterly payments, each principal payment would be $5M ($100M / 20 quarters)...",
    "metadata": {
        "domain": "debt",
        "concept_type": "formula",
        "complexity": "intermediate",
        "source": "expert_knowledge",
        "keywords": ["term loan", "amortization", "principal payment"]
    }
}
```

### 2.4 Private Lending Collection

The private lending collection will focus on:

- Credit analysis frameworks
- Collateral valuation methods
- Risk-adjusted return calculations
- Covenant structures
- Default and recovery modeling

Example document:
```
{
    "id": "lending-001",
    "text": "In private lending, the risk-adjusted return is calculated using the formula: Risk-Adjusted Return = (Expected Return - Risk-Free Rate) / Standard Deviation of Returns. This metric allows lenders to compare opportunities with different risk profiles. For private debt, the expected return includes both interest income and any fees, while the standard deviation is estimated based on historical performance of similar loans...",
    "metadata": {
        "domain": "lending",
        "concept_type": "formula",
        "complexity": "advanced",
        "source": "expert_knowledge",
        "keywords": ["risk-adjusted return", "standard deviation", "expected return"]
    }
}
```

## 3. User Preference Storage

### 3.1 Preference Schema

User preferences will be stored in a dedicated collection with the following schema:

```python
{
    "id": "user_preference_id",
    "user_id": "unique_user_identifier",
    "preference_type": "modeling|analysis|visualization|workflow",
    "task_context": "lbo_modeling|debt_sizing|etc",
    "preference_data": {
        "key1": "value1",
        "key2": "value2"
    },
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "priority": 1  # Higher numbers indicate stronger preferences
}
```

### 3.2 Preference Categories

The system will store preferences in the following categories:

#### 3.2.1 Modeling Preferences

```python
{
    "preference_type": "modeling",
    "task_context": "lbo_modeling",
    "preference_data": {
        "exit_multiple": 8.0,
        "default_debt_amortization": "2% quarterly",
        "preferred_irr_calculation": "monthly_compounding"
    }
}
```

#### 3.2.2 Analysis Preferences

```python
{
    "preference_type": "analysis",
    "task_context": "sensitivity_analysis",
    "preference_data": {
        "preferred_variables": ["WACC", "growth_rate", "exit_multiple"],
        "step_size": 0.5,
        "range_width": 2.0
    }
}
```

#### 3.2.3 Visualization Preferences

```python
{
    "preference_type": "visualization",
    "task_context": "returns_analysis",
    "preference_data": {
        "preferred_chart_type": "waterfall",
        "color_scheme": "blue_gradient",
        "include_benchmark": true
    }
}
```

#### 3.2.4 Workflow Preferences

```python
{
    "preference_type": "workflow",
    "task_context": "model_building",
    "preference_data": {
        "preferred_order": ["assumptions", "income_statement", "balance_sheet", "cash_flow", "valuation"],
        "auto_format": true,
        "include_documentation": true
    }
}
```

### 3.3 Preference Retrieval Strategy

The system will retrieve preferences using:

1. **Context matching**: Match current task to stored preference contexts
2. **Recency weighting**: Prioritize more recent preferences
3. **Priority ranking**: Apply preferences with higher priority first
4. **Conflict resolution**: When preferences conflict, use the higher priority or more recent one

## 4. Feedback Learning System

### 4.1 Feedback Schema

Feedback data will be stored with the following schema:

```python
{
    "id": "feedback_id",
    "user_id": "unique_user_identifier",
    "session_id": "session_identifier",
    "feedback_type": "explicit|implicit",
    "context": {
        "query": "original user query",
        "response": "system response",
        "retrieved_documents": ["doc_id1", "doc_id2"]
    },
    "feedback_data": {
        "rating": 4,  # 1-5 scale
        "correction": "corrected information",
        "comments": "user comments"
    },
    "timestamp": "feedback_timestamp",
    "processed": false  # Whether feedback has been incorporated
}
```

### 4.2 Feedback Types

The system will collect two types of feedback:

#### 4.2.1 Explicit Feedback

Direct feedback from users:
- Ratings of responses (1-5 scale)
- Corrections to information
- Comments on response quality
- Preference statements

#### 4.2.2 Implicit Feedback

Inferred feedback from user behavior:
- Whether the user applied the suggestion
- Time spent reviewing the response
- Follow-up questions indicating confusion
- Repeated queries suggesting dissatisfaction

### 4.3 Feedback Integration Process

The system will process feedback through:

1. **Collection**: Gather feedback data from user interactions
2. **Analysis**: Identify patterns and issues in feedback
3. **Knowledge update**: Modify or add knowledge based on corrections
4. **Retrieval adjustment**: Tune retrieval parameters based on feedback
5. **Preference extraction**: Extract implicit preferences from feedback

## 5. Implementation Considerations

### 5.1 Storage Requirements

- **Initial knowledge base size**: ~10,000 chunks across all domains
- **Storage per chunk**: ~10KB including text, metadata, and embedding
- **Total initial storage**: ~100MB for knowledge base
- **Growth projection**: ~20% annual growth as knowledge expands

### 5.2 Performance Considerations

- **Query latency target**: <100ms for retrieval operations
- **Batch processing**: Implement batch operations for embedding generation
- **Caching strategy**: Cache frequent queries and their results
- **Index optimization**: Use approximate nearest neighbor search for large collections

### 5.3 Security and Privacy

- **Data encryption**: Encrypt sensitive financial knowledge at rest
- **Access control**: Implement role-based access to knowledge base
- **User data separation**: Maintain separation between user preferences and core knowledge
- **Compliance**: Ensure all stored knowledge complies with financial regulations

## 6. Technical Implementation

### 6.1 Required Dependencies

```python
# Python dependencies for knowledge base layer
chromadb==0.4.18
openai==1.12.0
numpy==1.26.0
pydantic==2.5.2
python-dotenv==1.0.0
```

### 6.2 Directory Structure

```
backend/
├── knowledge_base/
│   ├── __init__.py
│   ├── vector_store.py       # Chroma DB integration
│   ├── preference_store.py   # User preference management
│   ├── feedback_store.py     # Feedback collection and processing
│   └── knowledge_manager.py  # High-level knowledge management
├── data/
│   ├── chroma_db/            # Persistent storage for Chroma
│   ├── preferences/          # User preference storage
│   └── feedback/             # Feedback data storage
```

This knowledge base layer design provides a comprehensive foundation for storing, organizing, and retrieving financial expertise in Cori's RAG++ system, with special attention to the specific domains of LBOs, M&A, debt modeling, and private lending.
