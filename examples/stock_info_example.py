"""
Example of using the Stock Information Agent.
"""
import os
import sys
from dotenv import load_dotenv

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

# Import the Stock Information Agent
from src.agents.bedrock.stock_info_agent import StockInfoAgent

def main():
    """Run the stock information example."""
    # Get AWS region from environment variables or use default
    aws_region = os.environ.get('AWS_REGION', 'us-east-1')
    
    # Get model ID from environment variables or use default
    model_id = os.environ.get('BEDROCK_MODEL_ID', 'amazon.nova-pro-v1:0')
    
    # Allow command line override for model
    if len(sys.argv) > 1:
        model_id = sys.argv[1]
    
    print(f"Using AWS Region: {aws_region}")
    print(f"Using Bedrock Model: {model_id}")
    
    # Initialize the Stock Information Agent with environment configuration
    agent = StockInfoAgent(model_id=model_id, region=aws_region)
    
    print("\nStock Information Agent Example")
    print("==============================")
    
    while True:
        print("\nOptions:")
        print("1. Get stock summary")
        print("2. Compare stocks")
        print("3. Get market overview")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            ticker = input("Enter stock ticker symbol (e.g., AAPL): ").upper()
            print(f"\nFetching information for {ticker}...")
            
            summary = agent.get_stock_summary(ticker)
            
            if 'error' in summary:
                print(f"Error: {summary['error']}")
            elif 'stock_info' in summary and summary['stock_info']:
                stock_info = summary['stock_info']
                print(f"\n{stock_info.get('name', 'Unknown')} ({stock_info.get('symbol', 'Unknown')})")
                print(f"Current Price: {stock_info.get('current_price', 'N/A')} {stock_info.get('currency', 'USD')}")
                print(f"Market Cap: {stock_info.get('market_cap_formatted', stock_info.get('market_cap', 'N/A'))}")
                print(f"Sector: {stock_info.get('sector', 'N/A')}")
                print(f"Industry: {stock_info.get('industry', 'N/A')}")
                
                if 'natural_language_summary' in summary:
                    print("\nSummary:")
                    print(summary['natural_language_summary'])
                
                if 'news' in summary and summary['news']:
                    print("\nRecent News:")
                    for item in summary['news']:
                        print(f"- {item.get('title', 'No title')} ({item.get('publish_time', 'Unknown date')})")
            else:
                print("No stock information available.")
        
        elif choice == '2':
            tickers_input = input("Enter stock ticker symbols separated by commas (e.g., AAPL,MSFT,GOOGL): ")
            tickers = [t.strip().upper() for t in tickers_input.split(',')]
            
            print(f"\nComparing stocks: {', '.join(tickers)}...")
            
            comparison = agent.compare_stocks(tickers)
            
            if 'error' in comparison:
                print(f"Error: {comparison['error']}")
            elif 'analysis' in comparison:
                print("\nComparison Analysis:")
                print(comparison['analysis'])
            else:
                print("\nComparison data retrieved, but no analysis was generated.")
                
                # Print raw data if no analysis
                print("\nStock Information:")
                for ticker, info in comparison['stock_infos'].items():
                    quote = comparison['quotes'].get(ticker, {})
                    print(f"\n{info['name']} ({ticker}):")
                    print(f"  Price: {quote.get('price', 'N/A')}")
                    print(f"  Change: {quote.get('change', 'N/A')} ({quote.get('change_percent_formatted', 'N/A')})")
                    print(f"  Market Cap: {info.get('market_cap_formatted', info.get('market_cap', 'N/A'))}")
                    print(f"  P/E Ratio: {info.get('pe_ratio', 'N/A')}")
        
        elif choice == '3':
            print("\nFetching market overview...")
            
            overview = agent.get_market_overview()
            
            if 'error' in overview:
                print(f"Error: {overview['error']}")
            elif 'analysis' in overview:
                print("\nMarket Analysis:")
                print(overview['analysis'])
            else:
                print("\nMarket data retrieved, but no analysis was generated.")
                
                # Print raw index data
                print("\nMajor Indices:")
                for symbol, index in overview['indices'].items():
                    if 'error' not in index:
                        print(f"{index['name']}: {index['price']} ({index.get('change_percent_formatted', 'N/A')})")
        
        elif choice == '4':
            print("\nExiting. Goodbye!")
            break
        
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()
