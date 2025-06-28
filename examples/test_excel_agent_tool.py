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
    analyze_with_excel_agent
)

if __name__ == "__main__":
    print("Excel Agent Tool Test")
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

    