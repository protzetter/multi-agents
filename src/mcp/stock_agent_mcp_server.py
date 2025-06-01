#!/usr/bin/env python3
"""
MCP Server for Strands Stock Agent
This server exposes the Strands stock agent functionality through MCP.
"""

import os
import sys
import logging
from typing import Dict, Any, Callable


# Add the project root to the path so we can import our modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)
# Import the Yahoo Finance client
from src.utils.finance.yahoo_finance import yahoo_finance

from mcp.server.fastmcp import FastMCP

from src.agents.strands.stock_info_agent import stock_agent, stock_agent_streaming

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
mcp = FastMCP('stock_agent')
mcp.logger = logger


#only for sync queries
@mcp.tool(description= "Ask the stock agent a question about stocks, markets, or financial analysis.")
def ask_stock_agent(query: str) -> Dict[str, Any]:
    """
    Ask the stock agent a question about stocks, markets, or financial analysis.
    
    Args:
        query: User query about stocks, markets, or financial analysis
        
    Returns:
        dict: Response from the stock agent
    """
    mcp.logger.info(f"Asking stock agent: {query}")
    
    # Call the stock agent with the query
    try:
        response = stock_agent(query,streaming=False)
            
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
    
    print("Starting Stock Agent MCP Server...")
    mcp.run(transport="sse")
