# OpenHands Memory Architecture Analysis for Cori RAG++ System

## Executive Summary

This report analyzes the memory mechanisms in the OpenHands repository and identifies key components that can be adapted for Cori's RAG++ system for financial transaction modeling. OpenHands implements a sophisticated three-tier memory architecture that effectively manages context across complex interactions:

1. **Short-term memory**: Conversation processing with comprehensive event tracking
2. **Working memory**: Advanced condensation strategies for context window management
3. **Long-term memory**: Vector storage for persistent knowledge retrieval

Five key transferable components have been identified:

1. **Three-tier memory architecture** with conversation processing, memory condensation, and long-term vector storage
2. **Event-based memory system** for tracking interactions and maintaining context
3. **Advanced condensation strategies** for managing context window limitations
4. **Flexible embedding framework** supporting multiple models and providers
5. **Domain-specific knowledge integration** through microagents

By implementing these components with adaptations for financial domains (LBOs, M&A, Debt Modeling, and Private Lending), Cori can significantly enhance its capabilities as a financial modeling assistant.

## 1. Conversation Memory System

### 1.1 OpenHands Implementation

OpenHands implements a sophisticated conversation memory system in `conversation_memory.py` that:

- Tracks all interactions through an event-based system
- Converts various events (actions, observations) into a coherent conversation history
- Maintains metadata about events for context management
- Supports multi-modal content (text and images)

The system processes different types of events and converts them into messages suitable for language models:

```python
def add_event(self, event: Event) -> None:
    """Add an event to the conversation history."""
    self.events.append(event)
    self._apply_condensers()
    
def to_messages(self) -> list[Message]:
    """Convert the conversation history to a list of messages for the LLM."""
    messages = []
    for event in self.condensed_events():
        message = event.to_message()
        if message:
            messages.append(message)
    return messages
```

### 1.2 Relevance for Cori

This event-based memory system is highly relevant for Cori's financial modeling context, where tracking different types of interactions is crucial:

- **Excel operations**: Formulas, cell formatting, worksheet creation
- **Financial calculations**: LBO returns, debt sizing, accretion/dilution analysis
- **User preferences**: Modeling approaches, visualization preferences
- **Domain-specific actions**: Transaction structuring, synergy analysis, covenant modeling

By implementing a similar event-based system tailored to financial domains, Cori can maintain rich context across complex financial modeling sessions.

## 2. Memory Condensation System

### 2.1 OpenHands Implementation

OpenHands implements multiple condensation strategies to manage context window limitations:

1. **LLM Summarizing Condenser** (`llm_summarizing_condenser.py`): Creates concise summaries of past events using an LLM
2. **LLM Attention Condenser** (`llm_attention_condenser.py`): Uses an LLM to identify and prioritize important events
3. **Amortized Forgetting Condenser** (`amortized_forgetting_condenser.py`): Maintains fixed-size history with important initial events
4. **Recent Events Condenser** (`recent_events_condenser.py`): Simple rolling history with fixed-size event tracking

The base `Condenser` class provides a flexible framework for implementing different condensation strategies:

```python
class Condenser(ABC):
    """Abstract base class for all condensers."""
    
    @abstractmethod
    def condense(self, events: list[Event]) -> list[Event]:
        """Condense a sequence of events into a potentially smaller list."""
        pass
```

The `LLMSummarizingCondenser` is particularly sophisticated, using an LLM to create concise summaries of forgotten events:

```python
def condense(self, events: list[Event]) -> list[Event]:
    """If the history is too long, summarize forgotten events."""
    if len(events) <= self.max_size:
        return events
        
    # Keep initial events
    head = events[:self.keep_first]
    
    # Keep recent events
    target_size = self.max_size // 2
    events_from_tail = target_size - len(head)
    tail = events[-events_from_tail:]
    
    # Summarize forgotten events
    forgotten_events = events[self.keep_first:-events_from_tail]
    summary = self._summarize_events(forgotten_events)
    
    return head + [AgentCondensationObservation(summary)] + tail
```

### 2.2 Relevance for Cori

These condensation strategies are highly relevant for Cori's financial modeling context, where preserving critical financial parameters and assumptions is essential. By implementing domain-specific condensers, Cori can:

- Preserve key financial parameters and assumptions across long sessions
- Maintain critical transaction details and modeling decisions
- Summarize complex financial analyses while preserving important details
- Prioritize events based on their relevance to financial outcomes

## 3. Long-Term Memory System

### 3.1 OpenHands Implementation

OpenHands implements a sophisticated long-term memory system in `long_term_memory.py` using ChromaDB with LlamaIndex for vector storage:

- Stores events as documents with metadata
- Supports semantic search for retrieving relevant past events
- Implements flexible embedding strategies
- Provides batch document insertion and retrieval

The system converts events to documents and stores them with appropriate metadata:

```python
def add_event(self, event: Event) -> None:
    """Add an event to long-term memory."""
    document = self._event_to_document(event)
    self.index.insert_documents([document])
    
def search(self, query: str, k: int = 5) -> list[Document]:
    """Search for relevant documents in long-term memory."""
    retriever = self.index.as_retriever(k=k)
    return retriever.retrieve(query)
```

### 3.2 Relevance for Cori

This long-term memory system is highly relevant for Cori's financial modeling context, where storing and retrieving domain-specific knowledge is crucial. By implementing a similar system with financial domain collections, Cori can:

- Store specialized financial knowledge in domain-specific collections
- Retrieve relevant financial expertise based on user queries
- Maintain user preferences and modeling approaches
- Support complex financial queries with domain-specific metadata filtering

## 4. Embedding System

### 4.1 OpenHands Implementation

OpenHands implements a flexible embedding system in `embeddings.py` that supports multiple embedding models and providers:

- OpenAI, Azure OpenAI, Voyage AI embeddings
- Ollama models (multiple options)
- Local Hugging Face embeddings
- Intelligent device selection (CUDA, MPS, CPU)
- Parallel processing for embedding generation

The system provides a unified interface for different embedding providers:

```python
@staticmethod
def get_embedding_model(strategy: str, llm_config: LLMConfig):
    if strategy in SUPPORTED_OLLAMA_EMBED_MODELS:
        return OllamaEmbedding(...)
    elif strategy == 'openai':
        return OpenAIEmbedding(...)
    elif strategy == 'azure_openai':
        return AzureOpenAIEmbedding(...)
    elif strategy == 'voyage':
        return VoyageEmbedding(...)
    elif strategy == 'local':
        return LocalEmbedding(...)
```

### 4.2 Relevance for Cori

This flexible embedding system is highly relevant for Cori's financial modeling context, where domain-specific embeddings can improve retrieval performance. By implementing a similar system, Cori can:

- Experiment with different embedding models for financial knowledge
- Use domain-specific embeddings for improved retrieval
- Optimize embedding generation for performance
- Support A/B testing of embedding strategies

## 5. Microagent System

### 5.1 OpenHands Implementation

OpenHands implements a sophisticated microagent system in `microagent.py` and `prompt.py` for specialized knowledge integration:

- **BaseMicroAgent**: Abstract base class for all microagents
- **KnowledgeMicroAgent**: Provides specialized expertise triggered by keywords
- **RepoMicroAgent**: Repository-specific knowledge
- **TaskMicroAgent**: Task-based operations

The system enhances user messages with relevant microagent knowledge:

```python
def enhance_message(self, message: Message) -> None:
    """Enhance the user message with additional context."""
    message_content = self._extract_message_content(message)
    
    triggered_agents = []
    for name, microagent in self.knowledge_microagents.items():
        trigger = microagent.match_trigger(message_content)
        if trigger:
            triggered_agents.append({
                'agent': microagent, 
                'trigger_word': trigger
            })
            
    if triggered_agents:
        formatted_text = self.build_microagent_info(triggered_agents)
        message.content.insert(0, TextContent(text=formatted_text))
```

### 5.2 Relevance for Cori

This microagent system is highly relevant for Cori's financial modeling context, where domain-specific expertise is crucial. By implementing a similar system with financial domain microagents, Cori can:

- Provide specialized expertise for different financial domains
- Trigger relevant knowledge based on user queries
- Enhance prompts with domain-specific best practices
- Support different financial modeling approaches

## 6. Implementation Recommendations

Based on the analysis of OpenHands' memory architecture, we recommend implementing the following components for Cori's RAG++ system:

### 6.1 Event-Based Memory Architecture

Implement an event-based system to track all interactions with Cori, focusing on financial modeling events:

```python
class FinancialModelingEvent(Event):
    """Base class for all financial modeling events."""
    domain: str  # "lbo", "ma", "debt", "private_lending"
    timestamp: datetime
    user_id: str
    session_id: str

class LBOModelingAction(FinancialModelingEvent):
    """Actions related to LBO modeling."""
    action_type: str  # "transaction_structure", "debt_sizing", "exit_analysis"
    parameters: dict  # Transaction parameters, assumptions, etc.
    
class ExcelOperationEvent(FinancialModelingEvent):
    """Events related to Excel operations."""
    operation_type: str  # "set_formula", "create_table", "format_cells"
    worksheet: str
    range_reference: str
    content: str  # Formula, value, etc.
    domain_context: str  # Which financial domain this operation relates to
```

### 6.2 Financial Domain-Specific Condensers

Implement domain-specific condensers that preserve critical financial information:

```python
class FinancialDomainCondenser(RollingCondenser):
    """Base condenser for financial domain contexts."""
    
    def identify_critical_events(self, events: List[Event]) -> List[Event]:
        """Identify domain-specific critical events to preserve."""
        raise NotImplementedError("Subclasses must implement this method")
        
    def condense(self, events: List[Event]) -> List[Event]:
        """Preserve critical financial modeling information while condensing history."""
        if len(events) <= self.max_size:
            return events
            
        # Keep initial user requirements
        head = events[:self.keep_first]
        
        # Identify domain-specific critical events
        critical_events = self.identify_critical_events(events)
        
        # Keep recent interactions with remaining slots
        remaining_slots = self.max_size - len(head) - len(critical_events)
        tail = events[-remaining_slots:] if remaining_slots > 0 else []
        
        return head + critical_events + tail
```

### 6.3 Financial Knowledge Collections

Implement domain-specific collections for financial knowledge:

```python
FINANCIAL_COLLECTIONS = {
    "lbo": {
        "description": "Leveraged Buyout modeling knowledge",
        "subcollections": {
            "structure": {
                "description": "Transaction structure knowledge",
                "metadata_schema": {
                    "purchase_price_range": "string",  # e.g., "100M-500M"
                    "entry_multiple_range": "string",  # e.g., "8x-12x"
                    "leverage_range": "string"  # e.g., "4x-6x"
                }
            },
            "returns": {
                "description": "Returns analysis knowledge",
                "metadata_schema": {
                    "holding_period_range": "string",  # e.g., "3-5 years"
                    "exit_multiple_range": "string",  # e.g., "8x-12x"
                    "target_irr_range": "string"  # e.g., "20%-25%"
                }
            }
        }
    }
}
```

### 6.4 Financial Microagents

Implement domain-specific microagents for financial expertise:

```python
def load_lbo_microagent() -> KnowledgeMicroagent:
    """Load the LBO expert microagent."""
    metadata = MicroagentMetadata(
        name="lbo_expert",
        type="knowledge",
        triggers=[
            "leveraged buyout",
            "LBO",
            "debt multiple",
            "exit multiple",
            "sponsor returns"
        ],
        domains=["lbo"]
    )
    
    content = """# LBO Modeling Best Practices

## Transaction Structure
- Purchase price typically expressed as a multiple of EBITDA (8-12x)
- Sources of funds include equity contribution (40-60%), debt financing (40-60%)
- Pro forma capital structure should be optimized for target returns

## Operational Projections
- Revenue growth assumptions should be based on historical performance
- EBITDA margin expansion opportunities should be realistic
- Working capital requirements typically 10-15% of revenue

## Debt Structure
- Senior debt typically 3-5x EBITDA with 5-7 year maturity
- Subordinated debt can add 1-2x additional leverage
- Financial covenants include leverage ratio and interest coverage ratio

## Returns Analysis
- Target IRR for private equity sponsors typically 20-25%
- Multiple of Invested Capital (MOIC) target typically 2.0-3.0x
- Exit typically modeled at similar or slightly lower multiple than entry"""
    
    return KnowledgeMicroagent(
        name=metadata.name,
        content=content,
        metadata=metadata
    )
```

### 6.5 Enhanced Retrieval Mechanisms

Implement enhanced retrieval mechanisms for financial knowledge:

```python
class HybridRetriever:
    """Implements hybrid retrieval combining vector search and keyword matching."""
    
    def retrieve(
        self,
        query: str,
        domain: Optional[str] = None,
        use_hyde: bool = True,
        use_expansion: bool = True,
        k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Retrieve relevant documents using hybrid approach."""
        # Detect domain if not provided
        if not domain:
            domain = self.query_processor.detect_financial_domain(query)
            
        # Process query
        processed_queries = [query]  # Start with original query
        
        # Add expanded query if requested
        if use_expansion:
            expanded_query = self.query_processor.expand_query(query, domain)
            if expanded_query != query:
                processed_queries.append(expanded_query)
                
        # Add HyDE document if requested
        if use_hyde:
            hyde_document = self.query_processor.generate_hyde_document(query, domain)
            processed_queries.append(hyde_document)
            
        # Retrieve results for each query
        all_results = []
        for q in processed_queries:
            results = self.long_term_memory.search(
                query=q,
                domain=domain,
                filters=filters,
                k=k
            )
            all_results.extend(results)
            
        # Deduplicate and sort results
        deduplicated = {}
        for result in all_results:
            if result["id"] not in deduplicated:
                deduplicated[result["id"]] = result
                
        sorted_results = sorted(
            deduplicated.values(),
            key=lambda x: x["distance"]
        )
            
        return sorted_results[:k]
```

## 7. Implementation Roadmap

We recommend implementing these components in the following phases:

1. **Phase 1: Core Memory Architecture** (2-3 weeks)
   - Implement event-based system
   - Set up ChromaDB integration
   - Create basic condensers

2. **Phase 2: Financial Domain Knowledge** (3-4 weeks)
   - Develop financial microagents
   - Populate knowledge collections
   - Implement domain-specific condensers

3. **Phase 3: Enhanced Retrieval** (2-3 weeks)
   - Implement query processing
   - Develop hybrid retrieval
   - Integrate with OpenAI handler

4. **Phase 4: User Preference System** (2-3 weeks)
   - Implement preference capture
   - Develop preference-aware retrieval
   - Create preference-based filtering

5. **Phase 5: Testing and Optimization** (2-3 weeks)
   - Benchmark retrieval performance
   - Optimize token usage
   - Fine-tune condensation strategies

## 8. Conclusion

OpenHands' memory architecture provides a sophisticated framework that can be adapted to enhance Cori's RAG++ system. By implementing the three-tier memory approach with event-based memory, advanced condensation strategies, and domain-specific knowledge integration, Cori can become a more effective financial modeling assistant with improved context awareness and specialized expertise.

The key insight from OpenHands is the three-tier approach to memory management:
1. **Short-term memory**: Conversation processing with event tracking
2. **Working memory**: Condensation strategies for context management
3. **Long-term memory**: Vector storage for knowledge retrieval

This approach, when adapted for financial domains (LBOs, M&A, Debt Modeling, and Private Lending), will enable Cori to maintain context across complex financial modeling sessions, provide domain-specific expertise, and continuously learn from user interactions.
