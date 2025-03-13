"""
Example of integrating the financial domain knowledge system with the memory architecture.
"""

import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from memory.models.event import Event
from memory.conversation_memory import ConversationMemory
from memory.long_term_memory import LongTermMemory
from memory.knowledge.financial_knowledge_base import FinancialKnowledgeBase
from memory.knowledge.knowledge_retriever import KnowledgeRetriever
from memory.knowledge.financial_domain_detector import FinancialDomainDetector

def main():
    """Run the integration example."""
    # Initialize components
    print("Initializing memory components...")
    
    # Create long-term memory
    ltm = LongTermMemory(
        vector_store_dir="./data/vector_store",
        embedding_model_name="text-embedding-ada-002"
    )
    
    # Create financial knowledge base
    knowledge_base = FinancialKnowledgeBase(
        long_term_memory=ltm,
        knowledge_dir="./data/financial_knowledge"
    )
    
    # Create knowledge retriever
    knowledge_retriever = KnowledgeRetriever(
        financial_knowledge_base=knowledge_base
    )
    
    # Create domain detector
    domain_detector = FinancialDomainDetector()
    
    # Create conversation memory
    conversation_memory = ConversationMemory(
        session_id="example_session",
        user_id="example_user"
    )
    
    # Load domain knowledge
    print("Loading financial domain knowledge...")
    for domain in ["lbo", "ma", "debt", "private_lending"]:
        count = knowledge_base.load_domain_knowledge(domain)
        print(f"Loaded {count} knowledge items for {domain} domain")
    
    # Simulate a conversation
    print("\nSimulating a conversation about LBO modeling...")
    
    # User query about LBO
    user_query = "How do I structure the debt for an LBO of a software company?"
    print(f"User: {user_query}")
    
    # Add user event to conversation memory
    user_event = Event(
        id="1",
        role="user",
        content=user_query,
        timestamp=datetime.now().isoformat()
    )
    conversation_memory.add_event(user_event)
    
    # Detect domain
    domain, confidence = domain_detector.detect_domain(user_query)
    print(f"Detected domain: {domain} (confidence: {confidence:.2f})")
    
    # Retrieve relevant knowledge
    knowledge = knowledge_retriever.retrieve_for_query(
        query=user_query,
        domain=domain,
        k=3
    )
    print("\nRetrieved knowledge:")
    print(knowledge)
    
    # Generate assistant response (simulated)
    assistant_response = """
    For structuring debt in a software company LBO, you can typically use higher leverage due to recurring revenue:
    
    1. Senior Secured Debt: 4-5x EBITDA (higher than average due to stable cash flows)
    2. Second Lien: 1-2x EBITDA
    3. Mezzanine: 1x EBITDA (optional)
    
    Total leverage can reach 6-7x EBITDA for software companies with strong recurring revenue.
    
    Key considerations:
    - Revenue predictability (% recurring)
    - Customer retention metrics
    - Growth rate
    - EBITDA margins (typically 20%+ for software)
    
    Lenders value the predictable cash flows and high margins of software businesses.
    """
    print(f"\nAssistant: {assistant_response}")
    
    # Add assistant event to conversation memory
    assistant_event = Event(
        id="2",
        role="assistant",
        content=assistant_response,
        timestamp=datetime.now().isoformat()
    )
    conversation_memory.add_event(assistant_event)
    
    # User follow-up query
    user_followup = "What are typical covenant requirements for this type of deal?"
    print(f"\nUser: {user_followup}")
    
    # Add user event to conversation memory
    user_followup_event = Event(
        id="3",
        role="user",
        content=user_followup,
        timestamp=datetime.now().isoformat()
    )
    conversation_memory.add_event(user_followup_event)
    
    # Retrieve knowledge for follow-up
    followup_knowledge = knowledge_retriever.retrieve_for_query(
        query=user_followup,
        domain=domain,
        topic="covenant_analysis",
        k=2
    )
    print("\nRetrieved knowledge for follow-up:")
    print(followup_knowledge)
    
    # Extract knowledge from conversation
    print("\nExtracting knowledge from conversation...")
    events = conversation_memory.get_events()
    doc_id = knowledge_base.extract_knowledge_from_events(events, domain)
    
    if doc_id:
        print(f"Extracted new knowledge and added to knowledge base with ID: {doc_id}")
    else:
        print("No new knowledge extracted from conversation")
    
    # Save domain knowledge
    print("\nSaving domain knowledge...")
    success = knowledge_base.save_domain_knowledge(domain)
    if success:
        print(f"Successfully saved {domain} knowledge to file")
    else:
        print(f"Failed to save {domain} knowledge to file")

if __name__ == "__main__":
    main()
