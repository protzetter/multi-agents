from strands import Agent, tool
from strands_tools import retrieve, file_read
from strands.models import BedrockModel
from strands.models.anthropic import AnthropicModel
import os
import json

# Mock knowledge base for demonstration purposes
KNOWLEDGE_BASE = {
    "banking_policies": [
        {
            "title": "Account Opening Requirements",
            "content": "To open a new account, customers must provide valid identification, proof of address, and complete the KYC process. For business accounts, additional documentation including business registration and ownership structure is required."
        },
        {
            "title": "Fee Structure",
            "content": "Standard checking accounts have a $5 monthly maintenance fee, which can be waived with a minimum balance of $1,500 or direct deposits totaling $500 per month. Savings accounts have no monthly fee with a minimum balance of $300."
        }
    ],
    "investment_guides": [
        {
            "title": "Beginner's Guide to Stock Investing",
            "content": "Stock investing involves purchasing shares of publicly traded companies. Before investing, consider your financial goals, risk tolerance, and investment timeline. Diversification across different sectors and asset classes can help manage risk."
        },
        {
            "title": "Understanding Market Indicators",
            "content": "Key market indicators include the P/E ratio, dividend yield, and market capitalization. The P/E ratio compares a company's share price to its earnings per share. A high P/E may indicate investors expect high growth, while a low P/E might suggest undervaluation or concerns about future performance."
        }
    ],
    "compliance_regulations": [
        {
            "title": "Anti-Money Laundering (AML) Requirements",
            "content": "Financial institutions must implement AML programs that include customer identification, transaction monitoring, and suspicious activity reporting. Enhanced due diligence is required for high-risk customers and politically exposed persons."
        },
        {
            "title": "Know Your Customer (KYC) Guidelines",
            "content": "KYC procedures require verification of customer identity, assessment of risk factors, and ongoing monitoring of customer relationships. Documentation must be periodically updated, with more frequent reviews for high-risk customers."
        }
    ]
}

@tool
def search_knowledge_base(query: str, category: str = None) -> list:
    """
    Search the knowledge base for information related to a query.
    
    Args:
        query: The search query
        category: Optional category to limit the search (banking_policies, investment_guides, compliance_regulations)
        
    Returns:
        list: Relevant documents from the knowledge base
    """
    query = query.lower()
    results = []
    
    # Determine which categories to search
    categories = [category] if category and category in KNOWLEDGE_BASE else KNOWLEDGE_BASE.keys()
    
    # Search through the knowledge base
    for cat in categories:
        for document in KNOWLEDGE_BASE[cat]:
            # Simple keyword matching (in a real implementation, use vector search)
            if query in document["title"].lower() or query in document["content"].lower():
                results.append({
                    "category": cat,
                    "title": document["title"],
                    "content": document["content"],
                    "relevance": 0.85  # Mock relevance score
                })
    
    # Sort by relevance
    results.sort(key=lambda x: x["relevance"], reverse=True)
    
    return results

# Create the RAG-enhanced agent
rag_agent = Agent(
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    tools=[search_knowledge_base, retrieve, file_read],
    system_prompt="""
    You are a knowledge-enhanced assistant with access to a banking and finance knowledge base.
    Your role is to:
    
    1. Answer questions by retrieving relevant information from the knowledge base
    2. Provide accurate, up-to-date information on banking policies, investment strategies, and compliance regulations
    3. Synthesize information from multiple sources when needed
    4. Clearly indicate when information comes from the knowledge base versus your general knowledge
    
    Use your tools to search the knowledge base and retrieve relevant information before responding.
    Always prioritize information from the knowledge base over your general knowledge when available.
    """
)

# Example usage
if __name__ == "__main__":
    print("RAG-Enhanced Knowledge Assistant")
    print("--------------------------------")
    print("Type 'exit' to quit")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            break
            
        response = rag_agent(user_input)
        print(f"\nAssistant: {response.message}")
