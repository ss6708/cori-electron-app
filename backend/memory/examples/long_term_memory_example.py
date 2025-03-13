"""
Example of using the long-term memory system in the Cori RAG++ architecture.
"""

import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from memory.models.event import Event
from memory.long_term_memory import LongTermMemory
from memory.utils.embedding_model import EmbeddingModel

def create_sample_events() -> List[Event]:
    """Create sample events for demonstration."""
    events = [
        Event(
            id="1",
            role="user",
            content="I'm looking to model an LBO for a software company with $50M in revenue and $15M in EBITDA.",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="2",
            role="assistant",
            content="Great, I can help you model an LBO for a software company. Let's start with some key assumptions. What EBITDA multiple are you considering for the purchase price?",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="3",
            role="user",
            content="I'm thinking of a 10x EBITDA multiple, so a $150M purchase price.",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="4",
            role="assistant",
            content="A 10x EBITDA multiple is reasonable for a software company with good growth prospects. For a $150M purchase price, let's consider the capital structure. Typically, software LBOs can support 5-6x EBITDA in debt due to recurring revenue. That would be $75-90M in debt, with the remainder as equity.",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="5",
            role="user",
            content="That sounds good. Let's use 5.5x EBITDA for debt, so $82.5M in debt and $67.5M in equity.",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="6",
            role="assistant",
            content="Perfect. With $82.5M in debt (5.5x EBITDA) and $67.5M in equity, your capital structure is 55% debt and 45% equity, which is reasonable for a software LBO. Now, let's consider the debt tranches. Typically, you might have a senior secured term loan, a second lien, and potentially a revolver for working capital.",
            timestamp=datetime.now().isoformat()
        )
    ]
    return events

def create_sample_ma_events() -> List[Event]:
    """Create sample M&A events for demonstration."""
    events = [
        Event(
            id="7",
            role="user",
            content="I need to model a strategic acquisition of a competitor. The target has $30M in revenue and $6M in EBITDA.",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="8",
            role="assistant",
            content="I can help you model a strategic acquisition. For strategic acquisitions, companies often pay higher multiples due to synergies. What multiple are you considering?",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="9",
            role="user",
            content="We're looking at a 12x EBITDA multiple, so $72M purchase price.",
            timestamp=datetime.now().isoformat()
        ),
        Event(
            id="10",
            role="assistant",
            content="A 12x EBITDA multiple is on the higher end but reasonable for a strategic acquisition with significant synergies. For the $72M purchase price, how do you plan to finance it? All-cash, stock, or a combination?",
            timestamp=datetime.now().isoformat()
        )
    ]
    return events

def create_sample_financial_knowledge() -> List[Dict[str, Any]]:
    """Create sample financial knowledge documents."""
    knowledge = [
        {
            "title": "LBO Capital Structure",
            "domain": "lbo",
            "topic": "capital_structure",
            "content": "In a leveraged buyout (LBO), the capital structure typically consists of 60-70% debt and 30-40% equity. For software companies with recurring revenue, debt can reach 5-6x EBITDA due to stable cash flows. The debt is usually structured in tranches with different priorities and interest rates."
        },
        {
            "title": "LBO Debt Tranches",
            "domain": "lbo",
            "topic": "debt_structure",
            "content": "LBO debt is typically structured in multiple tranches: 1) Senior Secured Term Loan (3-4x EBITDA) at L+300-400 bps, 2) Second Lien (1-2x EBITDA) at L+700-800 bps, 3) Mezzanine Debt (optional, 1x EBITDA) at 12-15%, and 4) Revolving Credit Facility for working capital."
        },
        {
            "title": "M&A Valuation Multiples",
            "domain": "ma",
            "topic": "valuation",
            "content": "Strategic acquisitions typically command higher valuation multiples than financial acquisitions due to potential synergies. While financial buyers might pay 8-10x EBITDA, strategic buyers often pay 10-15x EBITDA depending on the industry, growth rate, and synergy potential."
        },
        {
            "title": "M&A Financing Options",
            "domain": "ma",
            "topic": "financing",
            "content": "Strategic acquisitions can be financed through: 1) All-cash deals using existing cash or new debt, 2) All-stock deals by issuing new shares to target shareholders, 3) Mixed cash-and-stock deals, or 4) Earnouts where part of the payment is contingent on future performance."
        }
    ]
    return knowledge

def demonstrate_long_term_memory():
    """Demonstrate the long-term memory system."""
    print("\n=== Long-Term Memory Demonstration ===")
    
    # Check if API key is available
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        return
    
    # Create a temporary directory for the vector store
    vector_store_dir = "./data/vector_store"
    os.makedirs(vector_store_dir, exist_ok=True)
    
    try:
        # Initialize the long-term memory
        print("Initializing long-term memory...")
        ltm = LongTermMemory(
            vector_store_dir=vector_store_dir,
            embedding_model_name="text-embedding-ada-002",
            api_key=api_key
        )
        
        # Add financial knowledge
        print("\nAdding financial knowledge...")
        knowledge = create_sample_financial_knowledge()
        for doc in knowledge:
            doc_id = ltm.add_document(
                collection_name=doc["domain"],
                text=doc["content"],
                metadata={
                    "title": doc["title"],
                    "domain": doc["domain"],
                    "topic": doc["topic"],
                    "type": "knowledge"
                }
            )
            print(f"Added {doc['title']} to {doc['domain']} collection with ID: {doc_id}")
        
        # Add LBO events
        print("\nAdding LBO conversation events...")
        lbo_events = create_sample_events()
        lbo_doc_ids = ltm.add_events(
            events=lbo_events,
            domain="lbo"
        )
        print(f"Added {len(lbo_doc_ids)} LBO events to the vector store")
        
        # Add M&A events
        print("\nAdding M&A conversation events...")
        ma_events = create_sample_ma_events()
        ma_doc_ids = ltm.add_events(
            events=ma_events,
            domain="ma"
        )
        print(f"Added {len(ma_doc_ids)} M&A events to the vector store")
        
        # Search for LBO capital structure
        print("\nSearching for LBO capital structure...")
        lbo_results = ltm.search(
            query="What is the typical capital structure for an LBO?",
            collection_name="lbo",
            k=2
        )
        
        print("\nSearch results:")
        for i, result in enumerate(lbo_results):
            print(f"Result {i+1}:")
            print(f"Text: {result['text'][:100]}...")
            print(f"Metadata: {result['metadata']}")
            print(f"Distance: {result['distance']}")
            print()
        
        # Search across domains
        print("\nSearching across domains for acquisition financing...")
        multi_results = ltm.multi_domain_search(
            query="How to finance an acquisition?",
            domains=["lbo", "ma"],
            k_per_domain=2
        )
        
        print("\nMulti-domain search results:")
        for domain, results in multi_results.items():
            print(f"\n{domain.upper()} DOMAIN:")
            for i, result in enumerate(results):
                print(f"Result {i+1}:")
                print(f"Text: {result['text'][:100]}...")
                print(f"Metadata: {result['metadata']}")
                print(f"Distance: {result['distance']}")
        
        # Search by metadata
        print("\nSearching for documents by metadata...")
        topic_results = ltm.search_by_metadata(
            filters={"topic": "debt_structure"},
            collection_name="lbo",
            k=2
        )
        
        print("\nMetadata search results:")
        for i, result in enumerate(topic_results):
            print(f"Result {i+1}:")
            print(f"Text: {result['text'][:100]}...")
            print(f"Metadata: {result['metadata']}")
            print(f"ID: {result['id']}")
            print()
        
        # Get collection statistics
        print("\nCollection statistics:")
        for domain in ["lbo", "ma", "debt", "private_lending", "general"]:
            stats = ltm.get_collection_stats(domain)
            print(f"{domain.upper()}: {stats['count']} documents")
        
        # Export a collection
        print("\nExporting LBO collection...")
        export_file = "./data/lbo_export.json"
        ltm.export_collection(
            collection_name="lbo",
            output_file=export_file
        )
        print(f"Exported LBO collection to {export_file}")
        
        # Print the embedding model info
        print("\nEmbedding model information:")
        model_info = ltm.embedding_model.get_model_info()
        print(f"Model: {model_info['model_name']}")
        print(f"Cache size: {model_info['cache_size']} embeddings")
        
    except Exception as e:
        print(f"Error demonstrating long-term memory: {e}")

def demonstrate_embedding_model():
    """Demonstrate the embedding model."""
    print("\n=== Embedding Model Demonstration ===")
    
    # Check if API key is available
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        return
    
    try:
        # Initialize the embedding model
        print("Initializing embedding model...")
        embedding_model = EmbeddingModel(
            model_name="text-embedding-ada-002",
            api_key=api_key,
            cache_embeddings=True
        )
        
        # Generate embeddings for a single text
        print("\nGenerating embedding for a single text...")
        text = "Leveraged buyouts typically use significant debt to finance acquisitions."
        embedding = embedding_model.embed_text(text)
        print(f"Embedding dimension: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
        
        # Generate embeddings for multiple texts
        print("\nGenerating embeddings for multiple texts...")
        texts = [
            "Leveraged buyouts typically use significant debt to finance acquisitions.",
            "Strategic acquisitions are often motivated by synergies between companies.",
            "Debt modeling is crucial for understanding a company's financial health."
        ]
        embeddings = embedding_model.embed_texts(texts)
        print(f"Number of embeddings: {len(embeddings)}")
        print(f"Embedding dimensions: {[len(emb) for emb in embeddings]}")
        
        # Calculate similarity between texts
        print("\nCalculating similarity between texts...")
        text1 = "Leveraged buyouts typically use significant debt to finance acquisitions."
        text2 = "LBOs involve using substantial debt to fund company purchases."
        text3 = "Strategic acquisitions are often motivated by synergies between companies."
        
        similarity1 = embedding_model.similarity(text1, text2)
        similarity2 = embedding_model.similarity(text1, text3)
        
        print(f"Similarity between related texts: {similarity1:.4f}")
        print(f"Similarity between unrelated texts: {similarity2:.4f}")
        
        # Calculate similarities between a query and multiple texts
        print("\nCalculating similarities between a query and multiple texts...")
        query = "How much debt should be used in an LBO?"
        similarities = embedding_model.similarities(query, texts)
        
        print("Similarities:")
        for i, (text, similarity) in enumerate(zip(texts, similarities)):
            print(f"{i+1}. {text[:50]}... : {similarity:.4f}")
        
        # Check cache
        print("\nChecking embedding cache...")
        print(f"Cache size before clearing: {len(embedding_model.embedding_cache)} embeddings")
        embedding_model.clear_cache()
        print(f"Cache size after clearing: {len(embedding_model.embedding_cache)} embeddings")
        
    except Exception as e:
        print(f"Error demonstrating embedding model: {e}")

def main():
    """Run the long-term memory examples."""
    print("Cori RAG++ System - Long-Term Memory Examples")
    print("=============================================")
    
    # Demonstrate the long-term memory system
    demonstrate_long_term_memory()
    
    # Demonstrate the embedding model
    demonstrate_embedding_model()

if __name__ == "__main__":
    main()
