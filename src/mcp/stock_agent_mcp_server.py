#!/usr/bin/env python3
"""
MCP Server for Strands Stock Agent
This server exposes the Strands stock agent functionality through MCP.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional


# Add the project root to the path so we can import our modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)
# Import the Yahoo Finance client
from src.utils.finance.yahoo_finance import yahoo_finance

from mcp.server import FastMCP
from src.agents.strands.stock_info_agent import (
    get_stock_data, 
    compare_stocks, 
    get_market_overview, 
    generate_stock_chart_code, 
    search_stocks,
    stock_agent
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
app = FastMCP()
app.logger = logger

# @app.tool(description= "Get current and historical stock data for a given symbol.")
# def get_stock_info(symbol: str) -> Dict[str, Any]:
#     """
#     Get current and historical stock data for a given symbol.
    
#     Args:
#         symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        
#     Returns:
#         dict: Stock data including current price and historical data
#     """
#     app.logger.info(f"Fetching stock data for {symbol}")
#     result = get_stock_data(symbol)
#     return result

# @app.tool(description="Compare multiple stocks based on key metrics.")
# def compare_multiple_stocks(symbols: List[str]) -> Dict[str, Any]:
#     """
#     Compare multiple stocks based on key metrics.
    
#     Args:
#         symbols: List of stock ticker symbols to compare (e.g., ["AAPL", "MSFT", "GOOGL"])
        
#     Returns:
#         dict: Comparison data for the requested stocks
#     """
#     app.logger.info(f"Comparing stocks: {', '.join(symbols)}")
#     result = compare_stocks(symbols)
#     return result

# # @app.tool(description="Get an overview of the current market conditions.")
# # def get_market_summary() -> Dict[str, Any]:
# #     """
# #     Get an overview of the current market conditions.
    
# #     Returns:
# #         dict: Market overview information including major indices
# #     """
# #     app.logger.debug("Fetching market overview")
# #     result = get_market_overview()
# #     return result

# @app.tool(description="Get an overview of the current market conditions.")
# def get_market_summary() -> Dict[str, Any]:
#     """
#     Get an overview of the current market conditions.
    
#     Returns:
#         dict: Market overview information including major indices
#     """
#     try:
#         # Fetch market summary
#         market_summary = yahoo_finance.get_market_summary()
#         print(market_summary)
        
#         if 'error' in market_summary:
#             return {"error": f"Error fetching market data: {market_summary['error']}"}
#         return market_summary
#     except Exception as e:
#         logger.error(f"Error in get_market_overview: {str(e)}")
#         return {"error": f"Failed to retrieve market overview: {str(e)}"}


# @app.tool(description= "Generate Python code to create a stock price chart.")
# def generate_chart_code(symbol: str, days: int = 7) -> str:
#     """
#     Generate Python code to create a stock price chart.
    
#     Args:
#         symbol: Stock ticker symbol
#         days: Number of days of historical data to include
        
#     Returns:
#         str: Python code to generate the chart
#     """
#     app.logger.info(f"Generating chart code for {symbol} over {days} days")
#     result = generate_stock_chart_code(symbol, days)
#     return result

# @app.tool(description= "Search for stocks by name or ticker symbol.")
# def search_for_stocks(query: str, limit: int = 5) -> List[Dict[str, Any]]:
#     """
#     Search for stocks by name or ticker symbol.
    
#     Args:
#         query: Search query (company name or ticker symbol)
#         limit: Maximum number of results to return
        
#     Returns:
#         list: Matching stock information
#     """
#     app.logger.info(f"Searching for stocks matching '{query}'")
#     result = search_stocks(query, limit)
#     return result

@app.tool(description= "Ask the stock agent a question about stocks, markets, or financial analysis.")
def ask_stock_agent(query: str) -> Dict[str, Any]:
    """
    Ask the stock agent a question about stocks, markets, or financial analysis.
    
    Args:
        query: User query about stocks, markets, or financial analysis
        
    Returns:
        dict: Response from the stock agent
    """
    app.logger.info(f"Asking stock agent: {query}")
    
    # Call the stock agent with the query
    try:
        response = stock_agent(query,streaming=False)
        print(response)
        
        # Return the response in a structured format
        if hasattr(response, 'message') and isinstance(response.message, str):
            return {
                "response": response.message,
                "metadata": {
                    "agent": "stock_agent",
                    "timestamp": str(response.created_at) if hasattr(response, 'created_at') else None
                }
            }
        else:
            return {
                "response": str(response),
                "metadata": {
                    "agent": "stock_agent"
                }
            }
    except Exception as e:
        logger.error(f"Error in ask_stock_agent: {str(e)}")
        return {
            "error": str(e),
            "metadata": {
                "agent": "stock_agent",
                "status": "error"
            }
        }

if __name__ == "__main__":
    # Start the MCP server
    print("Starting Stock Agent MCP Server...")
    app.run(transport="sse")
