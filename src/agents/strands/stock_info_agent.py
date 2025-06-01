import os,sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(project_root)

from strands import Agent, tool
from strands.models import BedrockModel
from strands.models.anthropic import AnthropicModel
from dotenv import load_dotenv
import logging
from typing import Dict, Any, List,Callable
import asyncio

# Add the project root to the path so we can import our modules
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../config/.env')
load_dotenv(config_path)

region = os.environ.get('BEDROCK_REGION', 'us-east-1')        
# Get model ID from environment variables or use default
model= os.environ.get('BEDROCK_MODEL', 'us.amazon.nova-pro-v1:0')
ant_model=os.environ.get('ANTHROPIC_MODEL', 'claude-3-7-sonnet-20250219')           

# Import the Yahoo Finance client
from src.utils.finance.yahoo_finance import yahoo_finance

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

key = os.getenv('ANTHROPIC_API_KEY')
anthropic_model = AnthropicModel(
    client_args={
        "api_key": key,
    },
    # **model_config
    max_tokens=1028,
    model_id=ant_model,
    params={
        "temperature": 0.7,
    }
)
bedrock_model=BedrockModel(
    region_name=region,
    max_tokens=1028,
    model_id=model,
    params={
        "temperature": 0.7,
    }
)
@tool
def get_stock_data(symbol: str) -> Dict[str, Any]:
    """
    Get current and historical stock data for a given symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        
    Returns:
        dict: Stock data including current price and historical data
    """
    try:
        # Fetch basic stock information
        stock_info = yahoo_finance.get_stock_info(symbol)
        
        # Check if there was an error
        if 'error' in stock_info:
            return {"error": f"Error fetching stock data: {stock_info['error']}"}
        
        # Fetch historical data for the past week
        historical_data = yahoo_finance.get_historical_data(symbol, period='1mo', interval='1d')
        
        # Fetch recent news about the company
        news = yahoo_finance.get_company_news(symbol, limit=3)
        
        # Combine all the information
        result = {
            "symbol": symbol,
            "name": stock_info.get('name', 'Unknown'),
            "current_price": stock_info.get('current_price', 'N/A'),
            "change": historical_data.get('stats', {}).get('change', 'N/A'),
            "change_percent": historical_data.get('stats', {}).get('percent_change', 'N/A'),
            "market_cap": stock_info.get('market_cap', 'N/A'),
            "market_cap_formatted": stock_info.get('market_cap_formatted', 'N/A'),
            "pe_ratio": stock_info.get('pe_ratio', 'N/A'),
            "dividend_yield": stock_info.get('dividend_yield', 'N/A'),
            "dividend_yield_formatted": stock_info.get('dividend_yield_formatted', 'N/A'),
            "fifty_two_week_high": stock_info.get('fifty_two_week_high', 'N/A'),
            "fifty_two_week_low": stock_info.get('fifty_two_week_low', 'N/A'),
            "sector": stock_info.get('sector', 'N/A'),
            "industry": stock_info.get('industry', 'N/A'),
            "currency": stock_info.get('currency', 'USD'),
            "exchange": stock_info.get('exchange', 'N/A'),
            "business_summary": stock_info.get('business_summary', 'N/A'),
            "historical_data": historical_data.get('data', []),
            "news": news
        }
        
        return result
    except Exception as e:
        logger.error(f"Error in get_stock_data for {symbol}: {str(e)}")
        return {"error": f"Failed to retrieve stock data: {str(e)}"}

@tool
def compare_stocks(symbols: list) -> Dict[str, Any]:
    """
    Compare multiple stocks based on key metrics.
    
    Args:
        symbols: List of stock ticker symbols to compare
        
    Returns:
        dict: Comparison data for the requested stocks
    """
    try:
        # Fetch quotes for all symbols
        quotes = yahoo_finance.get_multiple_quotes(symbols)
        
        # Fetch basic info for all symbols
        stock_infos = {}
        for symbol in symbols:
            stock_infos[symbol] = yahoo_finance.get_stock_info(symbol)
        
        # Create comparison metrics
        comparison = {
            "current_prices": {},
            "daily_changes": {},
            "market_caps": {},
            "pe_ratios": {},
            "dividend_yields": {},
            "sectors": {},
            "industries": {}
        }
        
        for symbol, info in stock_infos.items():
            if 'error' not in info:
                comparison["current_prices"][symbol] = info.get('current_price', 'N/A')
                comparison["daily_changes"][symbol] = quotes.get(symbol, {}).get('change_percent', 'N/A')
                comparison["market_caps"][symbol] = info.get('market_cap_formatted', info.get('market_cap', 'N/A'))
                comparison["pe_ratios"][symbol] = info.get('pe_ratio', 'N/A')
                comparison["dividend_yields"][symbol] = info.get('dividend_yield_formatted', info.get('dividend_yield', 'N/A'))
                comparison["sectors"][symbol] = info.get('sector', 'N/A')
                comparison["industries"][symbol] = info.get('industry', 'N/A')
        
        return {
            "stocks": stock_infos,
            "quotes": quotes,
            "comparison": comparison
        }
    except Exception as e:
        logger.error(f"Error in compare_stocks for {symbols}: {str(e)}")
        return {"error": f"Failed to compare stocks: {str(e)}"}
@tool
def get_market_overview() -> Dict[str, Any]:
    """
    Get an overview of the current market conditions.
    
    Returns:
        dict: Market overview information including major indices
    """
    try:
        # Fetch market summary
        market_summary = yahoo_finance.get_market_summary()
        print(market_summary)
        
        if 'error' in market_summary:
            return {"error": f"Error fetching market data: {market_summary['error']}"}
        return market_summary
    except Exception as e:
        logger.error(f"Error in get_market_overview: {str(e)}")
        return {"error": f"Failed to retrieve market overview: {str(e)}"}

@tool
def generate_stock_chart_code(symbol: str, days: int = 7) -> str:
    """
    Generate Python code to create a stock price chart.
    
    Args:
        symbol: Stock ticker symbol
        days: Number of days of historical data to include
        
    Returns:
        str: Python code to generate the chart
    """
    code = f"""
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

# Get stock data
stock_data = get_stock_data("{symbol}")

# Extract historical data
if "error" in stock_data or not stock_data.get("historical_data"):
    print(f"Error: Could not retrieve historical data for {symbol}")
    return "Failed to generate chart due to missing data"

# Get the last {days} days of data
historical_data = stock_data["historical_data"][-{days}:]

# Extract dates and prices
dates = [item["date"] for item in historical_data]
prices = [item["close"] for item in historical_data]

# Create the chart
plt.figure(figsize=(10, 6))
plt.plot(dates, prices, marker='o', linestyle='-', color='blue')
plt.title(f"{{stock_data['name']}} ({symbol}) - {days} Day Price History")
plt.xlabel("Date")
plt.ylabel(f"Price ({{stock_data['currency']}})")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# Add annotations for highest and lowest points
if prices:
    max_price = max(prices)
    min_price = min(prices)
    max_idx = prices.index(max_price)
    min_idx = prices.index(min_price)
    
    plt.annotate(f"High: {{max_price}}", 
                xy=(dates[max_idx], max_price),
                xytext=(0, 10),
                textcoords="offset points",
                ha='center',
                arrowprops=dict(arrowstyle="->"))
                
    plt.annotate(f"Low: {{min_price}}", 
                xy=(dates[min_idx], min_price),
                xytext=(0, -15),
                textcoords="offset points",
                ha='center',
                arrowprops=dict(arrowstyle="->"))

# Show the chart
plt.show()

# Return a description of the chart
return f"Generated price chart for {{stock_data['name']}} ({symbol}) showing the last {days} days of price data."
"""
    return code

@tool
def search_stocks(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search for stocks by name or ticker symbol.
    
    Args:
        query: Search query (company name or ticker symbol)
        limit: Maximum number of results to return
        
    Returns:
        list: Matching stock information
    """
    try:
        results = yahoo_finance.search_stocks(query, limit)
        return results
    except Exception as e:
        logger.error(f"Error in search_stocks for {query}: {str(e)}")
        return [{"error": f"Failed to search stocks: {str(e)}"}]

# Create the stock information agent
stock_agent = Agent(
    model=anthropic_model,
    tools=[get_stock_data, compare_stocks, get_market_overview, generate_stock_chart_code, search_stocks,],
    system_prompt="""
    You are a stock information assistant specialized in financial analysis and visualization.
    Your role is to:
    
    1. Provide current stock information and historical data using real-time data from Yahoo Finance
    2. Compare multiple stocks based on key metrics like price, market cap, P/E ratio, and dividend yield
    3. Generate visualizations of stock performance
    4. Offer market overviews and insights on market trends
    5. Provide basic analysis and insights on stock trends
    
    Use your tools to retrieve stock data, perform calculations, and create visualizations.
    Present information in a clear, organized manner and explain financial concepts when needed.
    
    When analyzing stocks:
    - Consider both technical indicators and fundamental metrics
    - Explain the significance of key ratios like P/E ratio and dividend yield
    - Highlight notable recent news that might impact stock performance
    - Compare stocks within their industry context
    
    Always provide accurate, up-to-date information and be transparent about any limitations in the data.
    """
)

async def stock_agent_streaming(query: str, callback: Callable = None):
    """
    Call the stock agent with streaming enabled.
    
    Args:
        query: User query about stocks
        callback: Optional callback function to process streaming chunks
        
    Returns:
        The final response from the agent
    """
    try:
        # First try with streaming
        logger.info(f"Calling stock agent with streaming for query: {query}")
        stock_agent(query, stream=True, callback=callback)
           
    except Exception as e:
        logger.error(f"Error in stock_agent_streaming: {str(e)}")
        # Return a simple dict that mimics the structure expected by the UI
        error_response = {"content": [{"text": f"Error processing request: {str(e)}"}]}
        
        # If we have a callback, call it with the error response
        if callback:
            try:
                # Create a simple object with the expected structure
                class ErrorChunk:
                    def __init__(self, text):
                        self.content = [type('obj', (object,), {'text': text})]
                
                callback(ErrorChunk(f"Error processing request: {str(e)}"))
            except Exception as callback_error:
                logger.error(f"Error in callback: {str(callback_error)}")
        
        return error_response

# Example usage
if __name__ == "__main__":
    print("Stock Information System")
    print("------------------------")
    print("Type 'exit' to quit")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            break
            
        # Example of streaming output
        print("\nAssistant: ", end="", flush=True)
        
        def print_chunk(chunk):
            if chunk and hasattr(chunk, 'content') and chunk.content:
                print(chunk.content[0].text, end="", flush=True)
        
        asyncio.run(stock_agent_streaming(user_input, callback=print_chunk))
        print()  # Add a newline at the end
