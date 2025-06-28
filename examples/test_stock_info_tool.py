"""
Test script for the Stock Info Agent Tool

This script demonstrates how to use the stock info agent tools
to leverage the specialized stock analysis agent through other agents.
"""

import sys
import os

# Add the src directory to the path so we can import our tools
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools.stock_info_tool import (
    analyze_with_stock_agent,
    get_stock_price,
    compare_multiple_stocks,
    get_market_overview,
    search_stocks_by_name,
    get_stock_agent_capabilities
)


def test_stock_agent_capabilities():
    """Test getting Stock agent capabilities."""
    
    print("=== Stock Agent Capabilities ===\n")
    
    capabilities = get_stock_agent_capabilities()
    
    print(f"Agent: {capabilities['agent_name']}")
    print(f"Status: {capabilities['message']}")
    print(f"\nData Sources: {', '.join(capabilities['data_sources'])}")
    
    print("\nCapabilities:")
    for i, capability in enumerate(capabilities['capabilities'], 1):
        print(f"  {i}. {capability}")
    
    print("\nSupported Metrics:")
    for i, metric in enumerate(capabilities['supported_metrics'], 1):
        print(f"  {i}. {metric}")
    
    print("\nAnalysis Types:")
    for i, analysis_type in enumerate(capabilities['analysis_types'], 1):
        print(f"  {i}. {analysis_type}")
    
    print("\nUsage Examples:")
    for i, example in enumerate(capabilities['usage_examples'], 1):
        print(f"  {i}. \"{example}\"")
    
    print("\nLimitations:")
    for i, limitation in enumerate(capabilities['limitations'], 1):
        print(f"  {i}. {limitation}")
    
    print()


def test_individual_stock_tools():
    """Test individual stock analysis tools."""
    
    print("=== Individual Stock Tools Test ===\n")
    
    # Test get_stock_price
    print("1. Testing get_stock_price with AAPL:")
    print("-" * 40)
    
    try:
        result = get_stock_price("AAPL")
        if result['status'] == 'success':
            print(f"Symbol: {result['symbol']}")
            print(f"Analysis: {result['analysis'][:300]}...")
        else:
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f"Exception: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test search_stocks_by_name
    print("2. Testing search_stocks_by_name with 'Apple':")
    print("-" * 45)
    
    try:
        result = search_stocks_by_name("Apple", limit=3)
        if result['status'] == 'success':
            print(f"Search Query: {result['search_query']}")
            print(f"Results: {result['results'][:300]}...")
        else:
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f"Exception: {e}")
    
    print()


def test_comparison_and_market_tools():
    """Test stock comparison and market overview tools."""
    
    print("=== Comparison and Market Tools Test ===\n")
    
    # Test compare_multiple_stocks
    print("1. Testing compare_multiple_stocks with tech stocks:")
    print("-" * 50)
    
    try:
        result = compare_multiple_stocks(["AAPL", "MSFT", "GOOGL"])
        if result['status'] == 'success':
            print(f"Symbols: {', '.join(result['symbols'])}")
            print(f"Comparison: {result['comparison'][:400]}...")
        else:
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f"Exception: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test get_market_overview
    print("2. Testing get_market_overview:")
    print("-" * 30)
    
    try:
        result = get_market_overview()
        if result['status'] == 'success':
            print(f"Market Overview: {result['overview'][:400]}...")
        else:
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f"Exception: {e}")
    
    print()


def test_general_stock_analysis():
    """Test general stock analysis queries."""
    
    print("=== General Stock Analysis Test ===\n")
    
    test_queries = [
        "What are the best performing tech stocks today?",
        "Explain what P/E ratio means and why it's important",
        "What should I know about dividend investing?",
        "How do I analyze a stock's financial health?",
        "What are the current market trends?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: {query}")
        print("-" * 60)
        
        try:
            result = analyze_with_stock_agent(query)
            if result['status'] == 'success':
                print(f"Analysis: {result['analysis'][:300]}...")
            else:
                print(f"Error: {result['error']}")
        except Exception as e:
            print(f"Exception: {e}")
        
        # Pause between queries for readability
        input("\nPress Enter to continue to next query...")
        print()


def interactive_test():
    """Interactive testing mode."""
    
    print("\n=== Interactive Stock Agent Test ===")
    print("Ask the Stock agent questions about stocks, markets, or financial analysis.")
    print("Type 'quit' to exit.")
    print("=" * 60)
    
    print("\nAvailable commands:")
    print("- price <SYMBOL>: Get stock price (e.g., 'price AAPL')")
    print("- compare <SYMBOL1,SYMBOL2,...>: Compare stocks (e.g., 'compare AAPL,MSFT')")
    print("- search <COMPANY>: Search for stocks (e.g., 'search Tesla')")
    print("- market: Get market overview")
    print("- Or ask any general question about stocks")
    
    while True:
        query = input("\nYour question: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not query:
            continue
        
        try:
            # Parse special commands
            if query.lower().startswith('price '):
                symbol = query[6:].strip().upper()
                result = get_stock_price(symbol)
            elif query.lower().startswith('compare '):
                symbols_str = query[8:].strip()
                symbols = [s.strip().upper() for s in symbols_str.split(',')]
                result = compare_multiple_stocks(symbols)
            elif query.lower().startswith('search '):
                company = query[7:].strip()
                result = search_stocks_by_name(company)
            elif query.lower() == 'market':
                result = get_market_overview()
            else:
                # General analysis
                result = analyze_with_stock_agent(query)
            
            if result['status'] == 'success':
                if 'analysis' in result:
                    print(f"\nStock Agent: {result['analysis']}")
                elif 'comparison' in result:
                    print(f"\nStock Agent: {result['comparison']}")
                elif 'overview' in result:
                    print(f"\nStock Agent: {result['overview']}")
                elif 'results' in result:
                    print(f"\nStock Agent: {result['results']}")
                else:
                    print(f"\nStock Agent: {result}")
            else:
                print(f"\nError: {result['error']}")
                
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    print("Stock Info Agent Tool Test")
    print("Choose a test mode:")
    print("1. Show Stock agent capabilities")
    print("2. Test individual stock tools")
    print("3. Test comparison and market tools")
    print("4. Test general stock analysis")
    print("5. Interactive testing")
    print("6. All tests")
    
    choice = input("Enter your choice (1-6): ").strip()
    
    if choice == "1":
        test_stock_agent_capabilities()
    elif choice == "2":
        test_individual_stock_tools()
    elif choice == "3":
        test_comparison_and_market_tools()
    elif choice == "4":
        test_general_stock_analysis()
    elif choice == "5":
        interactive_test()
    elif choice == "6":
        test_stock_agent_capabilities()
        test_individual_stock_tools()
        test_comparison_and_market_tools()
        test_general_stock_analysis()
        interactive_test()
    else:
        print("Invalid choice. Running capabilities test...")
        test_stock_agent_capabilities()
