from strands import Agent, tool
from strands_tools import calculator, python_repl, http_request
import json
import os

@tool
def get_stock_data(symbol: str) -> dict:
    """
    Get current and historical stock data for a given symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        
    Returns:
        dict: Stock data including current price and historical data
    """
    # In a real implementation, this would use a financial API
    # For this example, we'll use a mock response
    
    # Mock stock data
    mock_data = {
        "AAPL": {
            "name": "Apple Inc.",
            "current_price": 182.63,
            "change": 1.25,
            "change_percent": 0.69,
            "market_cap": "2.85T",
            "pe_ratio": 28.45,
            "dividend_yield": 0.54,
            "historical_data": [
                {"date": "2025-05-11", "close": 181.38},
                {"date": "2025-05-12", "close": 180.95},
                {"date": "2025-05-13", "close": 179.80},
                {"date": "2025-05-14", "close": 180.25},
                {"date": "2025-05-15", "close": 181.50},
                {"date": "2025-05-16", "close": 182.10},
                {"date": "2025-05-17", "close": 182.63}
            ]
        },
        "MSFT": {
            "name": "Microsoft Corporation",
            "current_price": 415.72,
            "change": 2.35,
            "change_percent": 0.57,
            "market_cap": "3.09T",
            "pe_ratio": 35.12,
            "dividend_yield": 0.72,
            "historical_data": [
                {"date": "2025-05-11", "close": 413.37},
                {"date": "2025-05-12", "close": 412.95},
                {"date": "2025-05-13", "close": 410.80},
                {"date": "2025-05-14", "close": 412.25},
                {"date": "2025-05-15", "close": 413.50},
                {"date": "2025-05-16", "close": 414.10},
                {"date": "2025-05-17", "close": 415.72}
            ]
        },
        "GOOGL": {
            "name": "Alphabet Inc.",
            "current_price": 175.98,
            "change": 0.85,
            "change_percent": 0.49,
            "market_cap": "2.21T",
            "pe_ratio": 26.78,
            "dividend_yield": 0.0,
            "historical_data": [
                {"date": "2025-05-11", "close": 175.13},
                {"date": "2025-05-12", "close": 174.95},
                {"date": "2025-05-13", "close": 173.80},
                {"date": "2025-05-14", "close": 174.25},
                {"date": "2025-05-15", "close": 174.50},
                {"date": "2025-05-16", "close": 175.10},
                {"date": "2025-05-17", "close": 175.98}
            ]
        }
    }
    
    symbol = symbol.upper()
    if symbol not in mock_data:
        return {"error": f"Stock symbol not found: {symbol}"}
    
    return mock_data[symbol]

@tool
def compare_stocks(symbols: list) -> dict:
    """
    Compare multiple stocks based on key metrics.
    
    Args:
        symbols: List of stock ticker symbols to compare
        
    Returns:
        dict: Comparison data for the requested stocks
    """
    # Get data for each symbol
    stocks_data = {}
    for symbol in symbols:
        stock_data = get_stock_data(symbol)
        if "error" not in stock_data:
            stocks_data[symbol] = stock_data
    
    if not stocks_data:
        return {"error": "No valid stock symbols provided"}
    
    # Create comparison metrics
    comparison = {
        "current_prices": {symbol: data["current_price"] for symbol, data in stocks_data.items()},
        "daily_changes": {symbol: data["change_percent"] for symbol, data in stocks_data.items()},
        "market_caps": {symbol: data["market_cap"] for symbol, data in stocks_data.items()},
        "pe_ratios": {symbol: data["pe_ratio"] for symbol, data in stocks_data.items()},
        "dividend_yields": {symbol: data["dividend_yield"] for symbol, data in stocks_data.items()}
    }
    
    return {
        "stocks": stocks_data,
        "comparison": comparison
    }

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
import numpy as np

# Get stock data
stock_data = get_stock_data("{symbol}")

# Extract historical data
dates = [item["date"] for item in stock_data["historical_data"][-{days}:]]
prices = [item["close"] for item in stock_data["historical_data"][-{days}:]]

# Create the chart
plt.figure(figsize=(10, 6))
plt.plot(dates, prices, marker='o', linestyle='-', color='blue')
plt.title(f"{{stock_data['name']}} ({symbol}) - {days} Day Price History")
plt.xlabel("Date")
plt.ylabel("Price ($)")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# Show the chart
plt.show()

# Return a description of the chart
return f"Generated price chart for {{stock_data['name']}} ({symbol}) showing the last {days} days of price data."
"""
    return code

# Create the stock information agent
stock_agent = Agent(
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    tools=[get_stock_data, compare_stocks, generate_stock_chart_code, calculator, python_repl],
    system_prompt="""
    You are a stock information assistant specialized in financial analysis and visualization.
    Your role is to:
    
    1. Provide current stock information and historical data
    2. Compare multiple stocks based on key metrics
    3. Generate visualizations of stock performance
    4. Offer basic analysis and insights on stock trends
    
    Use your tools to retrieve stock data, perform calculations, and create visualizations.
    Present information in a clear, organized manner and explain financial concepts when needed.
    """
)

# Example usage
if __name__ == "__main__":
    print("Stock Information System")
    print("------------------------")
    print("Type 'exit' to quit")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            break
            
        response = stock_agent(user_input)
        print(f"\nAssistant: {response.message}")
