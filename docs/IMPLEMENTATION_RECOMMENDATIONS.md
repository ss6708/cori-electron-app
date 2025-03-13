# Implementation Recommendations for Cori RAG++ System

Based on the analysis of OpenHands' memory architecture, this document provides concrete implementation recommendations for enhancing Cori's RAG++ system with sophisticated memory mechanisms tailored to financial modeling domains.

## 1. Event-Based Memory Architecture

### 1.1 Implementation Approach

Implement an event-based system to track all interactions with Cori, focusing on financial modeling events:

```python
# Core event classes for financial modeling
class FinancialModelingEvent(Event):
    """Base class for all financial modeling events."""
    domain: str  # "lbo", "ma", "debt", "private_lending"
    timestamp: datetime
    user_id: str
    session_id: str

# Domain-specific events
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

class UserPreferenceEvent(FinancialModelingEvent):
    """Events capturing user preferences."""
    preference_type: str  # "modeling", "analysis", "visualization"
    preference_value: any  # The actual preference value
    preference_context: str  # Context in which the preference was expressed
```

### 1.2 Event Processing System

```python
class EventProcessor:
    """Processes events for both conversation memory and long-term storage."""
    
    def __init__(self, conversation_memory, long_term_memory):
        self.conversation_memory = conversation_memory
        self.long_term_memory = long_term_memory
        
    def process_event(self, event: Event) -> None:
        """Process a single event."""
        # Add to conversation memory for immediate context
        self.conversation_memory.add_event(event)
        
        # Store in long-term memory for future retrieval
        self.long_term_memory.add_event(event)
```

## 2. Memory Condensation System

### 2.1 Financial Domain Condensers

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

class LBOModelingCondenser(FinancialDomainCondenser):
    """Condenser specialized for LBO modeling contexts."""
    
    def identify_critical_events(self, events: List[Event]) -> List[Event]:
        """Identify critical LBO modeling events to preserve."""
        # Group events by type
        transaction_events = [e for e in events if isinstance(e, LBOModelingAction) 
                             and e.action_type == "transaction_structure"]
        debt_events = [e for e in events if isinstance(e, LBOModelingAction)
                      and e.action_type == "debt_sizing"]
        exit_events = [e for e in events if isinstance(e, LBOModelingAction)
                      and e.action_type == "exit_analysis"]
        
        # Keep the most recent of each critical event type
        critical_events = []
        if transaction_events:
            critical_events.append(transaction_events[-1])
        if debt_events:
            critical_events.append(debt_events[-1])
        if exit_events:
            critical_events.append(exit_events[-1])
            
        return critical_events
```

### 2.2 LLM-Based Summarizing Condenser

```python
class FinancialLLMSummarizingCondenser(RollingCondenser):
    """A condenser that creates concise summaries of financial modeling history."""
    
    def condense(self, events: List[Event]) -> List[Event]:
        """Summarize forgotten financial modeling events."""
        if len(events) <= self.max_size:
            return events
            
        # Identify events to be forgotten
        head = events[:self.keep_first]
        target_size = self.max_size // 2
        events_from_tail = target_size - len(head)
        tail = events[-events_from_tail:]
        forgotten_events = events[self.keep_first:-events_from_tail]
        
        # Construct domain-specific prompt for summarization
        prompt = """You are maintaining the memory of a financial modeling assistant. 
        Summarize the key information from these events, preserving:

        TRANSACTION PARAMETERS: Purchase price, valuation multiples, deal structure
        FINANCIAL PROJECTIONS: Growth rates, margins, working capital, capex
        DEBT STRUCTURE: Tranches, interest rates, amortization schedules, covenants
        RETURNS ANALYSIS: Exit assumptions, IRR calculations, sensitivity analysis
        USER PREFERENCES: Modeling approaches, analysis methods, visualization preferences"""
        
        # Add forgotten events to the prompt
        prompt += "\n\nEVENTS TO SUMMARIZE:"
        for event in forgotten_events:
            prompt += f"\n{str(event)}"
            
        # Get summary from LLM
        response = self.llm_client.completion(
            messages=[{"content": prompt, "role": "user"}]
        )
        summary = response.choices[0].message.content
        
        return head + [CondensationObservation(content=summary)] + tail
```

## 3. Long-Term Memory System

### 3.1 Vector Database Integration

```python
class LongTermMemory:
    """Handles storing and retrieving information using ChromaDB."""
    
    def __init__(self, db_path: str, embedding_model, session_id: str):
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=f"{db_path}/sessions/{session_id}/memory"
        )
        
        # Create collections for each domain
        self.collections = {
            "lbo": self.client.get_or_create_collection("lbo"),
            "ma": self.client.get_or_create_collection("ma"),
            "debt": self.client.get_or_create_collection("debt"),
            "private_lending": self.client.get_or_create_collection("private_lending"),
            "general": self.client.get_or_create_collection("general")
        }
        
        self.embedding_model = embedding_model
        self.session_id = session_id
        
    def add_event(self, event: Event) -> None:
        """Add an event to the appropriate collection."""
        # Convert event to document format
        doc_id, text, metadata = event_to_document(event)
        
        # Determine which collection to use
        domain = getattr(event, "domain", "general")
        collection = self.collections.get(domain, self.collections["general"])
        
        # Generate embedding and add to collection
        embedding = self.embedding_model.embed_text(text)
        collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[text]
        )
        
    def search(self, query: str, domain: str = None, filters: dict = None, k: int = 10) -> List[Dict]:
        """Search for relevant documents."""
        # Determine which collection to search
        collection = self.collections.get(domain, None) if domain else None
        
        # If no specific domain, search all collections
        if collection is None:
            results = []
            for domain_name, coll in self.collections.items():
                domain_results = self._search_collection(
                    collection=coll,
                    query=query,
                    filters=filters,
                    k=k
                )
                for result in domain_results:
                    result["domain"] = domain_name
                results.extend(domain_results)
            
            # Sort by distance and take top k
            results.sort(key=lambda x: x["distance"])
            return results[:k]
        else:
            # Search specific collection
            return self._search_collection(
                collection=collection,
                query=query,
                filters=filters,
                k=k
            )
```

### 3.2 Financial Knowledge Collections

```python
# Define collection structure for financial domains
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
    },
    # Similar structures for MA, Debt, and Private Lending domains
}
```

## 4. Microagent System for Financial Expertise

### 4.1 Microagent Base Implementation

```python
class MicroagentMetadata(BaseModel):
    """Metadata for microagents."""
    name: str
    type: str
    triggers: Optional[List[str]] = None
    domains: Optional[List[str]] = None
    description: Optional[str] = None

class KnowledgeMicroagent:
    """Microagent that provides specialized knowledge."""
    name: str
    content: str
    metadata: MicroagentMetadata
    
    def __init__(self, name: str, content: str, metadata: MicroagentMetadata):
        self.name = name
        self.content = content
        self.metadata = metadata
    
    def match_trigger(self, message: str) -> Optional[str]:
        """Check if any trigger words appear in the message."""
        if not self.metadata.triggers:
            return None
            
        message = message.lower()
        for trigger in self.metadata.triggers:
            if trigger.lower() in message:
                return trigger
                
        return None
```

### 4.2 Financial Domain Microagents

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

### 4.3 Prompt Enhancement System

```python
class PromptManager:
    """Manages prompts and microagent integration."""
    
    def __init__(self, microagents: Dict[str, KnowledgeMicroagent] = None):
        self.microagents = microagents or {}
        
    def enhance_message(self, message: str) -> str:
        """Enhance a user message with relevant microagent knowledge."""
        if not message or not self.microagents:
            return message
            
        triggered_agents = []
        for name, microagent in self.microagents.items():
            trigger = microagent.match_trigger(message)
            if trigger:
                triggered_agents.append({
                    "agent": microagent,
                    "trigger_word": trigger
                })
                
        if not triggered_agents:
            return message
            
        # Build enhanced message with microagent knowledge
        enhanced_message = message + "\n\n"
        enhanced_message += "RELEVANT FINANCIAL EXPERTISE:\n\n"
        
        for triggered in triggered_agents:
            agent = triggered["agent"]
            trigger_word = triggered["trigger_word"]
            enhanced_message += f"# {agent.name.upper()} (triggered by '{trigger_word}')\n"
            enhanced_message += agent.content + "\n\n"
            
        return enhanced_message
```

## 5. Enhanced Retrieval System

### 5.1 Query Understanding and Expansion

```python
class QueryProcessor:
    """Processes and enhances queries for improved retrieval."""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        
    def detect_financial_domain(self, query: str) -> Optional[str]:
        """Detect the financial domain of a query."""
        prompt = f"""Determine which financial domain this query belongs to:
Query: {query}

Choose ONE domain from:
- lbo (Leveraged Buyout modeling)
- ma (Mergers & Acquisitions)
- debt (Debt modeling)
- private_lending (Private lending)
- general (General financial or non-specific)

Return only the domain name, nothing else."""
        
        response = self.llm_client.completion(
            messages=[{"content": prompt, "role": "user"}]
        )
        domain = response.choices[0].message.content.strip().lower()
        
        valid_domains = ["lbo", "ma", "debt", "private_lending", "general"]
        return domain if domain in valid_domains else "general"
        
    def expand_query(self, query: str, domain: Optional[str] = None) -> str:
        """Expand a query with domain-specific terminology."""
        if not domain or domain == "general":
            return query
            
        prompt = f"""Expand this financial query with relevant domain-specific terminology:
Domain: {domain}
Original Query: {query}

Return the expanded query only, no explanations."""
        
        response = self.llm_client.completion(
            messages=[{"content": prompt, "role": "user"}]
        )
        expanded_query = response.choices[0].message.content.strip()
        
        return expanded_query
```

### 5.2 Hybrid Retrieval Implementation

```python
class HybridRetriever:
    """Implements hybrid retrieval combining vector search and keyword matching."""
    
    def __init__(self, long_term_memory, query_processor, embedding_model):
        self.long_term_memory = long_term_memory
        self.query_processor = query_processor
        self.embedding_model = embedding_model
        
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
            
        # Deduplicate results
        deduplicated = {}
        for result in all_results:
            if result["id"] not in deduplicated:
                deduplicated[result["id"]] = result
                
        # Sort by relevance score
        sorted_results = sorted(
            deduplicated.values(),
            key=lambda x: x["distance"]
        )
            
        return sorted_results[:k]
```

## 6. Integration with OpenAI Handler

```python
class RAGEnhancedOpenAIHandler:
    """Enhanced OpenAI handler with RAG integration."""
    
    def __init__(
        self,
        api_key: str,
        model: str,
        hybrid_retriever: HybridRetriever,
        prompt_manager: PromptManager
    ):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.hybrid_retriever = hybrid_retriever
        self.prompt_manager = prompt_manager
        
    def get_rag_enhanced_completion(
        self,
        messages: List[Dict],
        user_query: str,
        context: Dict,
        domain: Optional[str] = None
    ) -> Dict:
        """Get completion with RAG enhancement."""
        # Detect domain if not provided
        if not domain:
            domain = self.hybrid_retriever.query_processor.detect_financial_domain(user_query)
            
        # Enhance user message with microagent knowledge
        enhanced_query = self.prompt_manager.enhance_message(user_query)
        
        # Retrieve relevant knowledge
        retrieved_docs = self.hybrid_retriever.retrieve(
            query=user_query,
            domain=domain,
            k=5
        )
        
        # Format retrieved knowledge
        knowledge_context = self._format_retrieved_knowledge(retrieved_docs)
        
        # Construct system message with domain-specific instructions
        system_message = self._get_domain_specific_system_message(domain)
        
        # Add knowledge context to system message
        system_message += f"\n\nRELEVANT FINANCIAL KNOWLEDGE:\n{knowledge_context}"
        
        # Prepare messages for OpenAI
        openai_messages = [
            {"role": "system", "content": system_message}
        ]
        
        # Add conversation history
        for msg in messages[:-1]:  # Exclude the last message (user query)
            openai_messages.append(msg)
            
        # Add enhanced user query
        openai_messages.append({"role": "user", "content": enhanced_query})
        
        # Get completion from OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages
        )
        
        return response
        
    def _format_retrieved_knowledge(self, retrieved_docs: List[Dict]) -> str:
        """Format retrieved documents into a knowledge context string."""
        if not retrieved_docs:
            return "No relevant knowledge found."
            
        knowledge_context = ""
        for i, doc in enumerate(retrieved_docs, 1):
            knowledge_context += f"{i}. {doc['text']}\n\n"
            
        return knowledge_context
        
    def _get_domain_specific_system_message(self, domain: str) -> str:
        """Get domain-specific system message."""
        base_message = "You are Cori, an expert financial modeling assistant specializing in complex transaction modeling."
        
        domain_specific = {
            "lbo": "You excel at LBO modeling, including transaction structuring, debt sizing, operational projections, and returns analysis.",
            "ma": "You excel at M&A modeling, including valuation, synergy analysis, accretion/dilution, and deal structuring.",
            "debt": "You excel at debt modeling, including debt sizing, covenant analysis, amortization scheduling, and refinancing analysis.",
            "private_lending": "You excel at private lending analysis, including loan structuring, security analysis, returns calculation, and risk assessment."
        }
        
        return f"{base_message} {domain_specific.get(domain, '')}"
```

## 7. Implementation Roadmap

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

## 8. Required Dependencies

```
# Python dependencies
chromadb==0.4.18
openai==1.12.0
pydantic==2.5.2
python-dotenv==1.0.0
sentence-transformers==2.2.2
fastapi==0.104.1
```

## 9. Conclusion

These implementation recommendations provide a comprehensive framework for enhancing Cori with sophisticated memory mechanisms adapted from OpenHands. By implementing these components, Cori will be able to maintain context across complex financial modeling sessions, provide domain-specific expertise, and continuously learn from user interactions.
