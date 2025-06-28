"""
Stock Info Agent Tool for Strands Agents

This tool provides access to the specialized stock information agent,
allowing other agents to leverage stock analysis capabilities.
"""

from typing import Dict, Any, Optional, List
from strands import tool
import os
import sys

# Add the project root to the path so we can import our agents
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the stock agent (lazy import to avoid circular dependencies)
def get_stock_agent():
    """Lazy import of stock agent to avoid circular dependencies."""
    try:
        from agents.strands.stock_info_agent import stock_agent
        return stock_agent
    except ImportError as e:
        print(f"Warning: Could not import stock_agent: {e}")
        return None


@tool
def analyze_with_stock_agent(query: str) -> Dict[str, Any]:
    """
    Use the specialized Stock Information agent to analyze stocks and market data.
    
    This tool provides access to a specialized stock analysis agent that can:
    - Get real-time stock prices and historical data
    - Compare multiple stocks based on key metrics
    - Provide market overviews and trends
    - Generate stock charts and visualizations
    - Search for stocks by name or ticker
    - Analyze financial ratios and performance metrics
    
    Args:
        query: The question or analysis request for the Stock agent
        
    Returns:
        dict: Response from the Stock agent with analysis results
    """
    try:
        # Get the stock agent
        stock_agent = get_stock_agent()
        
        if stock_agent is None:
            return {
                "error": "Stock agent is not available",
                "message": "Could not load the Stock Information agent. Please check the agent configuration."
            }
        
        # Get response from the stock agent
        response = stock_agent(query)
        
        # Extract the message content
        if hasattr(response, 'message'):
            if isinstance(response.message, dict) and 'content' in response.message:
                # Handle structured message format
                content = response.message['content']
                if isinstance(content, list) and len(content) > 0:
                    message_text = content[0].get('text', str(response.message))
                else:
                    message_text = str(content)
            else:
                # Handle simple string message
                message_text = str(response.message)
        else:
            message_text = str(response)
        
        return {
            "status": "success",
            "query": query,
            "analysis": message_text,
            "agent": "Stock Information Agent",
            "message": "Stock analysis completed successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to analyze with Stock agent: {str(e)}",
            "query": query,
            "message": "Stock analysis failed due to an error"
        }


@tool
def get_stock_price(symbol: str) -> Dict[str, Any]:
    """
    Get current stock price and basic information for a specific symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)
        
    Returns:
        dict: Current stock price and basic information
    """
    try:
        stock_agent = get_stock_agent()
        
        if stock_agent is None:
            return {
                "error": "Stock agent is not available",
                "message": "Could not load the Stock Information agent."
            }
        
        query = f"Get the current stock price and basic information for {symbol}"
        response = stock_agent(query)
        
        # Extract message content
        if hasattr(response, 'message'):
            if isinstance(response.message, dict) and 'content' in response.message:
                content = response.message['content']
                if isinstance(content, list) and len(content) > 0:
                    message_text = content[0].get('text', str(response.message))
                else:
                    message_text = str(content)
            else:
                message_text = str(response.message)
        else:
            message_text = str(response)
        
        return {
            "status": "success",
            "symbol": symbol.upper(),
            "analysis": message_text,
            "agent": "Stock Information Agent",
            "message": f"Retrieved stock information for {symbol.upper()}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to get stock price for {symbol}: {str(e)}",
            "symbol": symbol.upper(),
            "message": "Stock price retrieval failed"
        }


@tool
def compare_multiple_stocks(symbols: List[str]) -> Dict[str, Any]:
    """
    Compare multiple stocks using the stock agent.
    
    Args:
        symbols: List of stock ticker symbols to compare
        
    Returns:
        dict: Comparison analysis from the stock agent
    """
    try:
        stock_agent = get_stock_agent()
        
        if stock_agent is None:
            return {
                "error": "Stock agent is not available",
                "message": "Could not load the Stock Information agent."
            }
        
        symbols_str = ", ".join([s.upper() for s in symbols])
        query = f"Compare these stocks and provide analysis: {symbols_str}"
        response = stock_agent(query)
        
        # Extract message content
        if hasattr(response, 'message'):
            if isinstance(response.message, dict) and 'content' in response.message:
                content = response.message['content']
                if isinstance(content, list) and len(content) > 0:
                    message_text = content[0].get('text', str(response.message))
                else:
                    message_text = str(content)
            else:
                message_text = str(response.message)
        else:
            message_text = str(response)
        
        return {
            "status": "success",
            "symbols": [s.upper() for s in symbols],
            "comparison": message_text,
            "agent": "Stock Information Agent",
            "message": f"Compared {len(symbols)} stocks successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to compare stocks {symbols}: {str(e)}",
            "symbols": [s.upper() for s in symbols],
            "message": "Stock comparison failed"
        }


@tool
def get_market_overview() -> Dict[str, Any]:
    """
    Get current market overview and trends using the stock agent.
    
    Returns:
        dict: Market overview and analysis
    """
    try:
        stock_agent = get_stock_agent()
        
        if stock_agent is None:
            return {
                "error": "Stock agent is not available",
                "message": "Could not load the Stock Information agent."
            }
        
        query = "Provide a current market overview including major indices and trends"
        response = stock_agent(query)
        
        # Extract message content
        if hasattr(response, 'message'):
            if isinstance(response.message, dict) and 'content' in response.message:
                content = response.message['content']
                if isinstance(content, list) and len(content) > 0:
                    message_text = content[0].get('text', str(response.message))
                else:
                    message_text = str(content)
            else:
                message_text = str(response.message)
        else:
            message_text = str(response)
        
        return {
            "status": "success",
            "overview": message_text,
            "agent": "Stock Information Agent",
            "message": "Market overview retrieved successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to get market overview: {str(e)}",
            "message": "Market overview retrieval failed"
        }


@tool
def search_stocks_by_name(company_name: str, limit: int = 5) -> Dict[str, Any]:
    """
    Search for stocks by company name using the stock agent.
    
    Args:
        company_name: Name of the company to search for
        limit: Maximum number of results to return
        
    Returns:
        dict: Search results from the stock agent
    """
    try:
        stock_agent = get_stock_agent()
        
        if stock_agent is None:
            return {
                "error": "Stock agent is not available",
                "message": "Could not load the Stock Information agent."
            }
        
        query = f"Search for stocks related to '{company_name}' and show up to {limit} results"
        response = stock_agent(query)
        
        # Extract message content
        if hasattr(response, 'message'):
            if isinstance(response.message, dict) and 'content' in response.message:
                content = response.message['content']
                if isinstance(content, list) and len(content) > 0:
                    message_text = content[0].get('text', str(response.message))
                else:
                    message_text = str(content)
            else:
                message_text = str(response.message)
        else:
            message_text = str(response)
        
        return {
            "status": "success",
            "search_query": company_name,
            "limit": limit,
            "results": message_text,
            "agent": "Stock Information Agent",
            "message": f"Search completed for '{company_name}'"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to search for stocks: {str(e)}",
            "search_query": company_name,
            "message": "Stock search failed"
        }


@tool
def get_stock_agent_capabilities() -> Dict[str, Any]:
    """
    Get information about the Stock Information agent's capabilities and usage.
    
    Returns:
        dict: Information about what the Stock agent can do
    """
    return {
        "agent_name": "Stock Information Agent",
        "capabilities": [
            "Get real-time stock prices and historical data",
            "Compare multiple stocks based on key financial metrics",
            "Provide market overviews and trend analysis",
            "Generate stock price charts and visualizations",
            "Search for stocks by company name or ticker symbol",
            "Analyze financial ratios (P/E, dividend yield, market cap)",
            "Retrieve company news and business summaries",
            "Track 52-week highs and lows",
            "Monitor daily price changes and percentage movements"
        ],
        "data_sources": ["Yahoo Finance API"],
        "supported_metrics": [
            "Current stock price",
            "Daily change and percentage change",
            "Market capitalization",
            "Price-to-Earnings (P/E) ratio",
            "Dividend yield",
            "52-week high and low",
            "Trading volume",
            "Sector and industry classification"
        ],
        "analysis_types": [
            "Individual stock analysis",
            "Multi-stock comparison",
            "Market trend analysis",
            "Technical indicator analysis",
            "Fundamental analysis",
            "News impact assessment"
        ],
        "usage_examples": [
            "What's the current price of Apple stock?",
            "Compare AAPL, MSFT, and GOOGL",
            "Show me the market overview today",
            "Search for Tesla stock information",
            "Analyze the performance of tech stocks this week",
            "What are the best dividend-paying stocks?"
        ],
        "limitations": [
            "Data is delayed by 15-20 minutes for most exchanges",
            "Historical data availability varies by symbol",
            "News data may be limited for smaller companies",
            "Chart generation requires additional visualization libraries"
        ],
        "message": "Stock Information agent is ready to analyze markets and stocks"
    }
