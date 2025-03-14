# Financial Domain Knowledge Components

The Cori application includes specialized components for handling financial domain knowledge. This document describes these components and their integration with the memory system.

## Financial Domain Detection

The `FinancialDomainDetector` component identifies the financial domain of user queries, allowing for domain-specific knowledge retrieval and processing.

### Supported Domains:

- **LBO (Leveraged Buyout)**: Financial transactions where a company is acquired using significant borrowed money
- **M&A (Mergers & Acquisitions)**: Consolidation of companies through various financial transactions
- **Debt Modeling**: Analysis of a company's debt structure and repayment capabilities
- **Private Lending**: Loans made by private individuals or institutions rather than traditional banks

### Implementation:

```python
from backend.memory.knowledge.financial_domain_detector import FinancialDomainDetector

# Initialize domain detector
domain_detector = FinancialDomainDetector(api_key=openai_api_key)

# Detect domain
domain = domain_detector.detect_domain("How do I structure an LBO model?")
# Returns: "LBO"

# Detect domain with confidence
domain, confidence = domain_detector.detect_domain_with_confidence(
    "What's the typical exit multiple for a tech company?"
)
# Returns: ("LBO", 0.85)
```

## Financial Knowledge Base

The `FinancialKnowledgeBase` component stores and retrieves domain-specific financial knowledge.

### Key Features:

- Domain-specific collections
- Document chunking and embedding
- Semantic search
- Metadata filtering

### Implementation:

```python
from backend.memory.knowledge.financial_knowledge_base import FinancialKnowledgeBase

# Initialize knowledge base
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

# Add domain-specific knowledge
knowledge_base.add_lbo_knowledge(document, metadata)
knowledge_base.add_ma_knowledge(document, metadata)
knowledge_base.add_debt_modeling_knowledge(document, metadata)
knowledge_base.add_private_lending_knowledge(document, metadata)
```

## Knowledge Extraction

The `KnowledgeExtractor` component extracts structured knowledge from unstructured text.

### Key Features:

- Financial term extraction
- Relationship identification
- Confidence scoring
- Domain classification

### Implementation:

```python
from backend.memory.knowledge.knowledge_extraction import KnowledgeExtractor

# Initialize knowledge extractor
knowledge_extractor = KnowledgeExtractor(api_key=openai_api_key)

# Extract knowledge
extracted_knowledge = knowledge_extractor.extract_from_text(
    text="The LBO model uses a 6x exit multiple and 5-year projection period.",
    domain="LBO"
)

# Extract financial terms
terms = knowledge_extractor.extract_financial_terms(
    text="Calculate the IRR and cash-on-cash return for this investment."
)
```

## Knowledge Retriever

The `KnowledgeRetriever` component retrieves relevant knowledge based on user queries.

### Key Features:

- Domain-aware retrieval
- Query reformulation
- Context-sensitive search
- Multi-domain search

### Implementation:

```python
from backend.memory.knowledge.knowledge_retriever import KnowledgeRetriever

# Initialize knowledge retriever
knowledge_retriever = KnowledgeRetriever(
    knowledge_base=knowledge_base,
    domain_detector=domain_detector
)

# Retrieve knowledge for query
knowledge = knowledge_retriever.retrieve_for_query(
    query="How do I calculate the exit multiple?",
    domain="LBO"
)

# Retrieve knowledge with auto-detected domain
knowledge = knowledge_retriever.retrieve_for_query(
    query="How do I calculate the exit multiple?",
    auto_detect_domain=True
)

# Retrieve knowledge across all domains
knowledge = knowledge_retriever.retrieve_across_domains(
    query="What's the difference between IRR and MOIC?"
)
```

## Domain-Specific Condensers

The memory system includes specialized condensers for different financial domains.

### Implementation:

```python
from backend.memory.condenser.impl.financial_domain_condensers import (
    LBOCondenser,
    MACondenser,
    DebtModelingCondenser,
    PrivateLendingCondenser
)

# Initialize domain-specific condensers
lbo_condenser = LBOCondenser(openai_handler=openai_handler)
ma_condenser = MACondenser(openai_handler=openai_handler)
debt_condenser = DebtModelingCondenser(openai_handler=openai_handler)
lending_condenser = PrivateLendingCondenser(openai_handler=openai_handler)

# Condense events
condensed_event = lbo_condenser.condense(events, max_tokens=1000)
```

## Domain-Specific Prompts

The system includes specialized prompts for different financial domains.

### LBO Domain Prompts:

```python
LBO_SYSTEM_PROMPT = """
You are a financial modeling expert specializing in Leveraged Buyouts (LBOs).
Your expertise includes:
- LBO model structure and components
- Debt sizing and amortization schedules
- Exit multiple calculation
- IRR and cash-on-cash return analysis
- LBO sensitivity analysis
"""

LBO_CONDENSE_PROMPT = """
Summarize the key points of this LBO modeling conversation, focusing on:
1. Model structure decisions
2. Financing assumptions
3. Operational projections
4. Exit strategy
5. Returns analysis
"""
```

### M&A Domain Prompts:

```python
MA_SYSTEM_PROMPT = """
You are a financial modeling expert specializing in Mergers & Acquisitions (M&A).
Your expertise includes:
- Accretion/dilution analysis
- Synergy valuation
- Deal structure optimization
- Purchase price allocation
- Pro forma financial statement modeling
"""

MA_CONDENSE_PROMPT = """
Summarize the key points of this M&A conversation, focusing on:
1. Deal rationale and structure
2. Valuation methodology
3. Synergy assumptions
4. Integration planning
5. Financial impact analysis
"""
```

## Integration with RAG System

The financial domain knowledge components integrate with the RAG system to provide domain-specific context enhancement.

### Implementation:

```python
from backend.memory.rag_enhanced_openai import RAGEnhancedOpenAIHandler

# Initialize RAG handler with financial domain components
rag_handler = RAGEnhancedOpenAIHandler(
    core_handler=openai_handler,
    conversation_memory=conversation_memory,
    long_term_memory=long_term_memory,
    knowledge_retriever=knowledge_retriever,
    domain_detector=domain_detector
)

# Get completion with domain-specific enhancement
response = rag_handler.get_completion(
    messages=[
        {"role": "user", "content": "How do I build an LBO model?"}
    ],
    session_id="session_123"
)
```

## Domain-Specific State Handling

The `StateAwareRAGHandler` component provides domain-specific state handling.

### Implementation:

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

# Handle analyzing state with domain detection
state_aware_handler.on_analyzing_state({
    "session_id": "session_123",
    "query": "How do I build an LBO model?"
})

# Handle planning state with domain-specific context
state_aware_handler.on_planning_state({
    "session_id": "session_123",
    "query": "How do I build an LBO model?"
})
```
