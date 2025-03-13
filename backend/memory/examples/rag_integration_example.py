"""
Example of using the RAG-enhanced OpenAI integration in the Cori RAG++ architecture.
"""

import os
import sys
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from memory.models.event import Event
from memory.conversation_memory import ConversationMemory
from memory.long_term_memory import LongTermMemory
from memory.knowledge.financial_knowledge_base import FinancialKnowledgeBase
from memory.knowledge.knowledge_retriever import KnowledgeRetriever
from memory.knowledge.financial_domain_detector import FinancialDomainDetector
from memory.rag_enhanced_openai import RAGEnhancedOpenAI

def create_sample_knowledge_base() -> FinancialKnowledgeBase:
    """Create a sample knowledge base for demonstration."""
    # Create a temporary directory for the vector store
    vector_store_dir = "./data/vector_store"
    os.makedirs(vector_store_dir, exist_ok=True)
    
    # Initialize long-term memory
    ltm = LongTermMemory(
        vector_store_dir=vector_store_dir,
        embedding_model_name="text-embedding-ada-002"
    )
    
    # Initialize knowledge base
    kb = FinancialKnowledgeBase(
        long_term_memory=ltm,
        knowledge_dir="./data/financial_knowledge"
    )
    
    # Add sample knowledge
    kb.add_knowledge(
        domain="lbo",
        topic="capital_structure",
        title="LBO Capital Structure",
        content="In a leveraged buyout (LBO), the capital structure typically consists of 60-70% debt and 30-40% equity. For software companies with recurring revenue, debt can reach 5-6x EBITDA due to stable cash flows. The debt is usually structured in tranches with different priorities and interest rates."
    )
    
    kb.add_knowledge(
        domain="lbo",
        topic="debt_structure",
        title="LBO Debt Tranches",
        content="LBO debt is typically structured in multiple tranches: 1) Senior Secured Term Loan (3-4x EBITDA) at L+300-400 bps, 2) Second Lien (1-2x EBITDA) at L+700-800 bps, 3) Mezzanine Debt (optional, 1x EBITDA) at 12-15%, and 4) Revolving Credit Facility for working capital."
    )
    
    kb.add_knowledge(
        domain="ma",
        topic="valuation",
        title="M&A Valuation Multiples",
        content="Strategic acquisitions typically command higher valuation multiples than financial acquisitions due to potential synergies. While financial buyers might pay 8-10x EBITDA, strategic buyers often pay 10-15x EBITDA depending on the industry, growth rate, and synergy potential."
    )
    
    kb.add_knowledge(
        domain="ma",
        topic="financing",
        title="M&A Financing Options",
        content="Strategic acquisitions can be financed through: 1) All-cash deals using existing cash or new debt, 2) All-stock deals by issuing new shares to target shareholders, 3) Mixed cash-and-stock deals, or 4) Earnouts where part of the payment is contingent on future performance."
    )
    
    kb.add_knowledge(
        domain="debt",
        topic="covenants",
        title="Debt Covenants",
        content="Debt covenants are restrictions that lenders put on borrowers as part of a debt agreement. Common covenants include: 1) Leverage Ratio (Debt/EBITDA), 2) Interest Coverage Ratio (EBITDA/Interest), 3) Fixed Charge Coverage Ratio, 4) Minimum EBITDA, and 5) Capital Expenditure Limitations. Covenant breaches can trigger default."
    )
    
    kb.add_knowledge(
        domain="private_lending",
        topic="direct_lending",
        title="Direct Lending",
        content="Direct lending involves non-bank lenders providing loans directly to middle-market companies. These loans typically have: 1) Higher yields (8-12%), 2) Floating rates, 3) Strong covenant packages, 4) Lower leverage (3-5x EBITDA), and 5) Shorter maturities (3-5 years) compared to broadly syndicated loans."
    )
    
    return kb

def demonstrate_basic_chat():
    """Demonstrate basic chat completion."""
    print("\n=== Basic Chat Completion ===")
    
    # Check if API key is available
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        return
    
    try:
        # Initialize RAG-enhanced OpenAI
        rag_openai = RAGEnhancedOpenAI(
            api_key=api_key,
            model="gpt-4o",
            temperature=0.7
        )
        
        # Create messages
        messages = [
            {"role": "system", "content": "You are Cori, a financial modeling expert."},
            {"role": "user", "content": "What is EBITDA and why is it important?"}
        ]
        
        # Generate completion
        print("Generating completion...")
        response = rag_openai.chat_completion(
            messages=messages,
            rag_enabled=False  # Disable RAG for this example
        )
        
        # Print response
        print("\nResponse:")
        print(response.choices[0].message.content)
        
        # Print conversation history
        print("\nConversation History:")
        for event in rag_openai.get_conversation_history():
            print(f"{event.role.capitalize()}: {event.content[:100]}...")
    
    except Exception as e:
        print(f"Error demonstrating basic chat: {e}")

def demonstrate_rag_enhanced_chat():
    """Demonstrate RAG-enhanced chat completion."""
    print("\n=== RAG-Enhanced Chat Completion ===")
    
    # Check if API key is available
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        return
    
    try:
        # Create knowledge base
        print("Creating knowledge base...")
        kb = create_sample_knowledge_base()
        
        # Initialize domain detector
        domain_detector = FinancialDomainDetector(api_key=api_key)
        
        # Initialize RAG-enhanced OpenAI
        rag_openai = RAGEnhancedOpenAI(
            api_key=api_key,
            model="gpt-4o",
            temperature=0.7,
            knowledge_base=kb,
            domain_detector=domain_detector
        )
        
        # Create messages
        messages = [
            {"role": "system", "content": "You are Cori, a financial modeling expert."},
            {"role": "user", "content": "What is the typical capital structure for an LBO of a software company?"}
        ]
        
        # Generate completion with domain detection
        print("Generating completion with domain detection...")
        response = rag_openai.chat_completion_with_domain_detection(
            messages=messages
        )
        
        # Print response
        print("\nResponse:")
        print(response.choices[0].message.content)
        
        # Print detected domain
        print(f"\nDetected Domain: {rag_openai.current_domain} (Confidence: {rag_openai.domain_confidence:.2f})")
        
        # Continue the conversation
        messages.append({"role": "assistant", "content": response.choices[0].message.content})
        messages.append({"role": "user", "content": "How would you structure the debt tranches?"})
        
        # Generate completion for follow-up
        print("\nGenerating completion for follow-up...")
        response = rag_openai.chat_completion_with_domain_detection(
            messages=messages
        )
        
        # Print response
        print("\nResponse:")
        print(response.choices[0].message.content)
        
        # Print detected domain
        print(f"\nDetected Domain: {rag_openai.current_domain} (Confidence: {rag_openai.domain_confidence:.2f})")
    
    except Exception as e:
        print(f"Error demonstrating RAG-enhanced chat: {e}")

def demonstrate_multi_domain_chat():
    """Demonstrate multi-domain chat completion."""
    print("\n=== Multi-Domain Chat Completion ===")
    
    # Check if API key is available
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        return
    
    try:
        # Create knowledge base
        print("Creating knowledge base...")
        kb = create_sample_knowledge_base()
        
        # Initialize domain detector
        domain_detector = FinancialDomainDetector(api_key=api_key)
        
        # Initialize RAG-enhanced OpenAI
        rag_openai = RAGEnhancedOpenAI(
            api_key=api_key,
            model="gpt-4o",
            temperature=0.7,
            knowledge_base=kb,
            domain_detector=domain_detector
        )
        
        # Create messages for LBO
        lbo_messages = [
            {"role": "system", "content": "You are Cori, a financial modeling expert."},
            {"role": "user", "content": "What is the typical capital structure for an LBO?"}
        ]
        
        # Generate completion for LBO
        print("Generating completion for LBO query...")
        lbo_response = rag_openai.chat_completion_with_domain_detection(
            messages=lbo_messages
        )
        
        # Print LBO response
        print("\nLBO Response:")
        print(lbo_response.choices[0].message.content)
        print(f"Detected Domain: {rag_openai.current_domain} (Confidence: {rag_openai.domain_confidence:.2f})")
        
        # Create messages for M&A
        ma_messages = [
            {"role": "system", "content": "You are Cori, a financial modeling expert."},
            {"role": "user", "content": "How are strategic acquisitions typically financed?"}
        ]
        
        # Generate completion for M&A
        print("\nGenerating completion for M&A query...")
        ma_response = rag_openai.chat_completion_with_domain_detection(
            messages=ma_messages
        )
        
        # Print M&A response
        print("\nM&A Response:")
        print(ma_response.choices[0].message.content)
        print(f"Detected Domain: {rag_openai.current_domain} (Confidence: {rag_openai.domain_confidence:.2f})")
        
        # Create messages for cross-domain query
        cross_domain_messages = [
            {"role": "system", "content": "You are Cori, a financial modeling expert."},
            {"role": "user", "content": "Compare the financing approaches for LBOs versus strategic acquisitions."}
        ]
        
        # Generate completion for cross-domain query
        print("\nGenerating completion for cross-domain query...")
        cross_domain_response = rag_openai.chat_completion_with_domain_detection(
            messages=cross_domain_messages
        )
        
        # Print cross-domain response
        print("\nCross-Domain Response:")
        print(cross_domain_response.choices[0].message.content)
        print(f"Detected Domain: {rag_openai.current_domain} (Confidence: {rag_openai.domain_confidence:.2f})")
    
    except Exception as e:
        print(f"Error demonstrating multi-domain chat: {e}")

def demonstrate_feedback_based_chat():
    """Demonstrate feedback-based chat completion."""
    print("\n=== Feedback-Based Chat Completion ===")
    
    # Check if API key is available
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        return
    
    try:
        # Initialize RAG-enhanced OpenAI
        rag_openai = RAGEnhancedOpenAI(
            api_key=api_key,
            model="gpt-4o",
            temperature=0.7
        )
        
        # Create messages
        messages = [
            {"role": "system", "content": "You are Cori, a financial modeling expert."},
            {"role": "user", "content": "Create a simple LBO model for a company with $10M EBITDA."}
        ]
        
        # Define feedback function
        def feedback_function(completion):
            """Example feedback function that checks for specific content."""
            content = completion.choices[0].message.content.lower()
            
            # Check if the response includes key elements
            has_purchase_price = "purchase price" in content or "acquisition price" in content
            has_debt = "debt" in content
            has_equity = "equity" in content
            has_exit = "exit" in content or "return" in content
            
            # Determine if the response is acceptable
            is_acceptable = has_purchase_price and has_debt and has_equity and has_exit
            
            # Generate feedback
            feedback = ""
            if not has_purchase_price:
                feedback += "Please include information about the purchase price calculation. "
            if not has_debt:
                feedback += "Please include details about the debt structure. "
            if not has_equity:
                feedback += "Please include information about the equity contribution. "
            if not has_exit:
                feedback += "Please include details about the exit strategy and returns. "
            
            if is_acceptable:
                feedback = "Good response that covers all key elements of an LBO model."
            
            return is_acceptable, feedback
        
        # Generate completion with feedback
        print("Generating completion with feedback...")
        completion, is_acceptable, feedback = rag_openai.chat_completion_with_feedback(
            messages=messages,
            feedback_function=feedback_function,
            max_attempts=3
        )
        
        # Print response
        print("\nFinal Response:")
        print(completion.choices[0].message.content)
        
        # Print feedback
        print(f"\nAcceptable: {is_acceptable}")
        print(f"Feedback: {feedback}")
        
        # Print conversation history
        print("\nConversation History:")
        for event in rag_openai.get_conversation_history():
            print(f"{event.role.capitalize()}: {event.content[:100]}...")
    
    except Exception as e:
        print(f"Error demonstrating feedback-based chat: {e}")

def demonstrate_response_formatting():
    """Demonstrate response formatting."""
    print("\n=== Response Formatting ===")
    
    # Check if API key is available
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        return
    
    try:
        # Initialize RAG-enhanced OpenAI
        rag_openai = RAGEnhancedOpenAI(
            api_key=api_key,
            model="gpt-4o",
            temperature=0.7
        )
        
        # Create messages
        messages = [
            {"role": "system", "content": "You are Cori, a financial modeling expert. Format your response with markdown-style bold text for titles and use bullet points for lists."},
            {"role": "user", "content": "List the key components of an LBO model."}
        ]
        
        # Generate completion
        print("Generating completion...")
        response = rag_openai.chat_completion(
            messages=messages
        )
        
        # Get raw response
        raw_response = response.choices[0].message.content
        
        # Format response
        formatted_response = rag_openai.format_response(raw_response)
        
        # Print responses
        print("\nRaw Response:")
        print(raw_response)
        
        print("\nFormatted Response:")
        print(formatted_response)
    
    except Exception as e:
        print(f"Error demonstrating response formatting: {e}")

def main():
    """Run the RAG-enhanced OpenAI examples."""
    print("Cori RAG++ System - OpenAI Integration Examples")
    print("===============================================")
    
    # Demonstrate basic chat completion
    demonstrate_basic_chat()
    
    # Demonstrate RAG-enhanced chat completion
    demonstrate_rag_enhanced_chat()
    
    # Demonstrate multi-domain chat completion
    demonstrate_multi_domain_chat()
    
    # Demonstrate feedback-based chat completion
    demonstrate_feedback_based_chat()
    
    # Demonstrate response formatting
    demonstrate_response_formatting()

if __name__ == "__main__":
    main()
