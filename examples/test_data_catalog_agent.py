"""
Test script for the Data Catalog Agent

This script demonstrates how to use the data catalog agent and tests its functionality.
"""

import sys
import os

# Add the src directory to the path so we can import our agents
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.strands.data_catalog_agent import data_catalog_agent, orchestrate_data_catalog_query


def test_data_catalog_agent():
    """Test the data catalog agent with various queries."""
    
    print("=== Testing Data Catalog Agent ===\n")
    
    # Test queries
    test_queries = [
        "What data products do we have available?",
        "Tell me about the Swiss power plants dataset",
        "What attributes are available in the population data?",
        "Search for energy-related data products",
        "Where is the swiss_population data stored?",
        "Show me details about swiss_power_plants including its format and location",
        "What's the difference between the two datasets we have?",
        "How often is the population data updated?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"Test Query {i}: {query}")
        print("-" * 60)
        
        try:
            # Test using the orchestrate function
            response = orchestrate_data_catalog_query(query)
            print(f"Response: {response}\n")
        except Exception as e:
            print(f"Error: {e}\n")
        
        # Add a small pause between queries for readability
        input("Press Enter to continue to next query...")
        print()


def interactive_test():
    """Interactive testing mode."""
    
    print("=== Interactive Data Catalog Agent Test ===")
    print("Ask questions about data products. Type 'quit' to exit.")
    print("Example questions:")
    print("- What data do we have about Switzerland?")
    print("- Show me the attributes of the power plants data")
    print("- Where can I find population statistics?")
    print("=" * 50)
    
    while True:
        user_query = input("\nYour question: ").strip()
        
        if user_query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not user_query:
            continue
            
        try:
            response = orchestrate_data_catalog_query(user_query)
#            print(f"\nData Catalog Agent: {response}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    print("Data Catalog Agent Test")
    print("Choose a test mode:")
    print("1. Run predefined test queries")
    print("2. Interactive testing")
    print("3. Both")
    
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    
    if choice == "1":
        test_data_catalog_agent()
    elif choice == "2":
        interactive_test()
    elif choice == "3":
        test_data_catalog_agent()
        print("\n" + "="*60 + "\n")
        interactive_test()
    else:
        print("Invalid choice. Running interactive test...")
        interactive_test()
