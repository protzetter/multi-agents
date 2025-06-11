"""
Test script for the Excel Agent Tool

This script demonstrates how to use the analyze_with_excel_agent tool
to leverage the specialized Excel analysis agent through other agents.
"""

import sys
import os

# Add the src directory to the path so we can import our tools
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools.excel_tools_strands import (
    analyze_with_excel_agent,
    read_csv_file
)


def test_excel_agent_analysis():
    """Test the Excel agent analysis with sample data."""
    
    print("=== Excel Agent Analysis Test ===\n")
    
    # Test with the Swiss power plants data
    docs_path = os.path.join(os.path.dirname(__file__), '..', 'docs')
    power_plants_file = os.path.join(docs_path, 'renewable_power_plants_CH_filtered.csv')
    
    if os.path.exists(power_plants_file):
        print("Testing with Swiss Power Plants data...")
        
        test_queries = [
            "What are the main types of renewable energy sources in this dataset?",
            "Which canton has the most power plants?",
            "What's the average electrical capacity of the power plants?",
            "Can you identify any interesting patterns in the commissioning dates?",
            "What data quality issues do you notice in this dataset?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\nQuery {i}: {query}")
            print("-" * 60)
            
            try:
                result = analyze_with_excel_agent(query, power_plants_file)
                
                if result['status'] == 'success':
                    print(f"Analysis: {result['analysis']}")
                else:
                    print(f"Error: {result['error']}")
                    
            except Exception as e:
                print(f"Exception: {e}")
            
            # Pause between queries for readability
            input("\nPress Enter to continue to next query...")
    
    else:
        print(f"Power plants file not found at: {power_plants_file}")
        print("Testing with a general query instead...")
        
        try:
            result = analyze_with_excel_agent("What are your capabilities for data analysis?")
            print(f"Response: {result['analysis']}")
        except Exception as e:
            print(f"Error: {e}")


def interactive_test():
    """Interactive testing mode."""
    
    print("\n=== Interactive Excel Agent Test ===")
    print("Ask the Excel agent questions about data analysis.")
    print("You can specify a file path or ask general questions.")
    print("Type 'quit' to exit.")
    print("=" * 50)
    
    while True:
        query = input("\nYour question: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not query:
            continue
        
        # Check if user wants to analyze a specific file
        file_path = None
        if "file:" in query.lower():
            parts = query.split("file:", 1)
            if len(parts) == 2:
                file_path = parts[1].strip()
                query = parts[0].strip()
        
        try:
            result = analyze_with_excel_agent(query, file_path)
            
            if result['status'] == 'success':
                print(f"\nExcel Agent: {result['analysis']}")
            else:
                print(f"\nError: {result['error']}")
                
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    print("Excel Agent Tool Test")
    print("Choose a test mode:")
    print("1. Test analysis with sample data")
    print("2. Interactive testing")
    print("3. All tests")
    
    choice = input("Enter your choice (1-5): ").strip()
    
    if choice == "1":
        test_excel_agent_analysis()
    elif choice == "2":
        interactive_test()
    elif choice == "3":
        test_excel_agent_analysis()
        interactive_test()
    else:
        print("Invalid choice. Running capabilities test...")
        test_excel_agent_analysis()

