"""
Example demonstrating the integration of the three-tier memory architecture
with the existing OpenAI handler for RAG-enhanced completions.
"""

import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_services import OpenAIHandler
from memory.memory_manager import MemoryManager
from memory.rag_enhanced_openai import RAGEnhancedOpenAIHandler
from memory.utils.embedding_model import EmbeddingModel

# Load environment variables
load_dotenv()

def main():
    """Run the RAG integration example."""
    # Create a unique session ID
    session_id = str(uuid.uuid4())
    user_id = "example_user"
    
    # Initialize the standard OpenAI handler
    openai_handler = OpenAIHandler()
    
    # Initialize the memory manager
    memory_manager = MemoryManager(
        session_id=session_id,
        user_id=user_id,
        db_path="./data/vector_db",
        openai_handler=openai_handler
    )
    
    # Initialize the RAG-enhanced OpenAI handler
    rag_openai_handler = RAGEnhancedOpenAIHandler(
        memory_manager=memory_manager,
        model_name="gpt-4o"
    )
    
    # Add some sample knowledge to the long-term memory
    print("Adding sample knowledge to long-term memory...")
    
    # LBO knowledge
    lbo_knowledge = """
    Leveraged Buyout (LBO) Model Structure:
    
    1. Transaction Assumptions:
    - Purchase Price: Typically expressed as a multiple of EBITDA (e.g., 8-12x)
    - Transaction Fees: Usually 1-2% of enterprise value
    - Financing Fees: 2-4% of debt raised
    
    2. Debt Structure:
    - Senior Secured Debt: 3-4x EBITDA, lower interest rate (L+250-350bps)
    - Second Lien: 1-2x EBITDA, higher interest rate (L+550-750bps)
    - Mezzanine: 1-1.5x EBITDA, highest interest rate (10-12%)
    - Equity Contribution: 30-50% of total enterprise value
    
    3. Financial Projections:
    - Revenue Growth: Industry-specific, typically 3-7% annually
    - EBITDA Margin: Industry-specific, with potential expansion from operational improvements
    - Capital Expenditures: Maintenance (2-3% of revenue) and growth (project-specific)
    - Working Capital: Industry-specific, typically 10-15% of revenue change
    
    4. Exit Assumptions:
    - Exit Multiple: Often similar to entry multiple, sometimes with slight premium (0.5-1.0x)
    - Exit Year: Typically 5 years, range of 3-7 years
    - IRR Target: 20-25% for private equity investors
    """
    
    memory_manager.add_knowledge_document(
        text=lbo_knowledge,
        metadata={
            "type": "financial_knowledge",
            "domain": "lbo",
            "topic": "model_structure"
        },
        domain="lbo"
    )
    
    # M&A knowledge
    ma_knowledge = """
    Merger & Acquisition (M&A) Valuation Methodologies:
    
    1. Comparable Company Analysis:
    - Identify publicly traded peers with similar business models
    - Calculate valuation multiples (EV/EBITDA, P/E, EV/Revenue)
    - Apply appropriate discount/premium based on size, growth, and profitability
    
    2. Precedent Transaction Analysis:
    - Identify similar transactions in the industry
    - Calculate transaction multiples paid
    - Consider control premiums (typically 20-30%)
    
    3. Discounted Cash Flow (DCF) Analysis:
    - Project future cash flows (5-10 years)
    - Calculate terminal value (exit multiple or perpetuity growth method)
    - Discount at WACC (typically 8-12% depending on industry)
    
    4. Accretion/Dilution Analysis:
    - Calculate pro forma EPS impact
    - Consider synergies (cost and revenue)
    - Analyze breakeven period for EPS accretion
    """
    
    memory_manager.add_knowledge_document(
        text=ma_knowledge,
        metadata={
            "type": "financial_knowledge",
            "domain": "ma",
            "topic": "valuation_methodologies"
        },
        domain="ma"
    )
    
    # Simulate a conversation
    print("\nSimulating a conversation with RAG-enhanced responses...\n")
    
    # User query about LBO modeling
    user_query = "How should I structure the debt in an LBO model for a manufacturing company?"
    print(f"User: {user_query}")
    
    # Add user message to memory
    memory_manager.add_user_message(user_query, domain="lbo")
    
    # Get RAG-enhanced response
    response = rag_openai_handler.get_rag_enhanced_completion(
        messages=[{"role": "user", "content": user_query}],
        user_query=user_query,
        domain="lbo"
    )
    
    print(f"Cori: {response['content']}\n")
    
    # User follow-up query
    user_query = "What exit multiple should I use for this LBO?"
    print(f"User: {user_query}")
    
    # Add user message to memory
    memory_manager.add_user_message(user_query, domain="lbo")
    
    # Get conversation messages (includes previous interaction)
    messages = memory_manager.get_conversation_messages()
    
    # Get RAG-enhanced response
    response = rag_openai_handler.get_rag_enhanced_completion(
        messages=messages,
        user_query=user_query,
        domain="lbo"
    )
    
    print(f"Cori: {response['content']}\n")
    
    # User query about M&A
    user_query = "What's the best way to value a software company for acquisition?"
    print(f"User: {user_query}")
    
    # Add user message to memory
    memory_manager.add_user_message(user_query, domain="ma")
    
    # Get RAG-enhanced response
    response = rag_openai_handler.get_rag_enhanced_completion(
        messages=[{"role": "user", "content": user_query}],
        user_query=user_query,
        domain="ma"
    )
    
    print(f"Cori: {response['content']}\n")
    
    # Demonstrate memory condensation
    print("Adding multiple messages to demonstrate memory condensation...")
    
    # Add multiple messages to trigger condensation
    for i in range(10):
        memory_manager.add_user_message(f"Test message {i}", domain="general")
        memory_manager.add_assistant_message(f"Test response {i}", domain="general")
    
    # Show condensed messages
    condensed_messages = memory_manager.get_conversation_messages()
    print(f"\nNumber of condensed messages: {len(condensed_messages)}")
    
    # Search for relevant knowledge
    print("\nSearching for relevant knowledge...")
    
    search_results = memory_manager.search_knowledge(
        query="debt structure for LBO",
        domain="lbo",
        k=1
    )
    
    if search_results:
        print(f"Found relevant knowledge: {search_results[0]['text'][:100]}...")
    else:
        print("No relevant knowledge found.")
    
    print("\nRAG integration example completed.")

if __name__ == "__main__":
    main()
