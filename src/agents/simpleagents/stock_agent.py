"""
SimpleAgent implementation for stock information.

This module provides a Simple Language Model Agent specialized for
retrieving and analyzing stock information.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import sys

# Add the project root to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

# Import the base SimpleAgent class
from src.agents.simpleagents.base_agent import SimpleAgent

# Import the Yahoo Finance client
from src.utils.finance.yahoo_finance import yahoo_finance

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockSimpleAgent(SimpleAgent):
    """
    SimpleAgent specialized for stock information.
    
    This agent can retrieve stock quotes, historical data, company information,
    and provide analysis using a smaller, more efficient language model.
    """
    
    def __init__(
        self,
        model_provider: str = "bedrock",
        model_name: str = "amazon.nova-pro-v1:0",
        temperature: float = 0.2,
        max_tokens: int = 512
    ):
        """
        Initialize the Stock SimpleAgent.
        
        Args:
            model_provider: Provider of the language model
            model_name: Name of the language model to use
            temperature: Temperature parameter for generation
            max_tokens: Maximum number of tokens to generate
        """
        # Define the tools this agent can use
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_stock_quote",
                    "description": "Get the current quote for a stock",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticker": {
                                "type": "string",
                                "description": "Stock ticker symbol (e.g., AAPL for Apple)"
                            }
                        },
                        "required": ["ticker"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_stock_history",
                    "description": "Get historical price data for a stock",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticker": {
                                "type": "string",
                                "description": "Stock ticker symbol (e.g., AAPL for Apple)"
                            },
                            "period": {
                                "type": "string",
                                "description": "Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)",
                                "default": "1mo"
                            },
                            "interval": {
                                "type": "string",
                                "description": "Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)",
                                "default": "1d"
                            }
                        },
                        "required": ["ticker"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_company_news",
                    "description": "Get recent news articles about a company",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticker": {
                                "type": "string",
                                "description": "Stock ticker symbol (e.g., AAPL for Apple)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of news items to return",
                                "default": 5
                            }
                        },
                        "required": ["ticker"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "compare_stocks",
                    "description": "Compare multiple stocks",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tickers": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "List of stock ticker symbols to compare"
                            }
                        },
                        "required": ["tickers"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_market_summary",
                    "description": "Get a summary of major market indices",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]
        
        # Define the system prompt
        system_prompt = """
        You are StockSimpleAgent, a specialized agent for retrieving and analyzing stock information.
        You can provide stock quotes, historical data, company news, and market summaries.
        
        When asked about stocks or the market, use the appropriate tools to fetch the most up-to-date information.
        Provide concise, accurate responses focused on the most relevant information.
        
        For stock analysis:
        1. Focus on key metrics like price, market cap, P/E ratio, and recent performance
        2. Highlight significant news that might impact the stock
        3. Provide brief context about the company and its industry
        
        For market analysis:
        1. Focus on major indices and their recent performance
        2. Highlight significant market trends
        3. Provide brief context about market conditions
        
        Always be factual and avoid speculation. If you don't have enough information, say so and suggest what additional information would be helpful.
        """
        
        # Initialize the base SimpleAgent
        super().__init__(
            name="StockSimpleAgent",
            description="A specialized agent for retrieving and analyzing stock information",
            model_provider=model_provider,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            system_prompt=system_prompt
        )
        
        # Register tool implementations
        self.register_tool("get_stock_quote", self._get_stock_quote)
        self.register_tool("get_stock_history", self._get_stock_history)
        self.register_tool("get_company_news", self._get_company_news)
        self.register_tool("compare_stocks", self._compare_stocks)
        self.register_tool("get_market_summary", self._get_market_summary)
    
    def _get_stock_quote(self, ticker: str) -> Dict[str, Any]:
        """
        Get the current quote for a stock.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Stock quote information
        """
        try:
            stock_info = yahoo_finance.get_stock_info(ticker)
            return stock_info
        except Exception as e:
            logger.error(f"Error getting stock quote for {ticker}: {str(e)}")
            return {"error": str(e)}
    
    def _get_stock_history(self, ticker: str, period: str = "1mo", interval: str = "1d") -> Dict[str, Any]:
        """
        Get historical price data for a stock.
        
        Args:
            ticker: Stock ticker symbol
            period: Time period
            interval: Data interval
            
        Returns:
            Historical stock data
        """
        try:
            historical_data = yahoo_finance.get_historical_data(ticker, period, interval)
            
            # Simplify the data for smaller models
            if "data" in historical_data:
                # Limit the number of data points to reduce token usage
                historical_data["data"] = historical_data["data"][-10:]
            logger.debug(f"Historical data for {ticker}: {json.dumps(historical_data, indent=2)}")
            return historical_data
        except Exception as e:
            logger.error(f"Error getting stock history for {ticker}: {str(e)}")
            return {"error": str(e)}
    
    def _get_company_news(self, ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent news articles about a company.
        
        Args:
            ticker: Stock ticker symbol
            limit: Maximum number of news items to return
            
        Returns:
            List of news articles
        """
        try:
            news = yahoo_finance.get_company_news(ticker, limit)
            return news
        except Exception as e:
            logger.error(f"Error getting company news for {ticker}: {str(e)}")
            return [{"error": str(e)}]
    
    def _compare_stocks(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Compare multiple stocks.
        
        Args:
            tickers: List of stock ticker symbols to compare
            
        Returns:
            Comparison data
        """
        try:
            quotes = yahoo_finance.get_multiple_quotes(tickers)
            
            # Get basic info for each ticker
            stock_infos = {}
            for ticker in tickers:
                stock_infos[ticker] = yahoo_finance.get_stock_info(ticker)
            
            return {
                "quotes": quotes,
                "stock_infos": stock_infos
            }
        except Exception as e:
            logger.error(f"Error comparing stocks {tickers}: {str(e)}")
            return {"error": str(e)}
    
    def _get_market_summary(self) -> Dict[str, Any]:
        """
        Get a summary of major market indices.
        
        Returns:
            Market summary data
        """
        try:
            market_summary = yahoo_finance.get_market_summary()
            return market_summary
        except Exception as e:
            logger.error(f"Error getting market summary: {str(e)}")
            return {"error": str(e)}
    
    def get_stock_analysis(self, ticker: str) -> str:
        """
        Get a comprehensive analysis of a stock.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Natural language analysis of the stock
        """
        prompt = f"""
        I need a comprehensive analysis of the stock {ticker}.
        Please provide information about the current price, recent performance,
        key financial metrics, and any relevant news that might impact the stock.
        """
        
        return self.process_message(prompt)
    
    def get_market_analysis(self) -> str:
        """
        Get a comprehensive analysis of the current market conditions.
        
        Returns:
            Natural language analysis of the market
        """
        prompt = """
        I need a comprehensive analysis of the current market conditions.
        Please provide information about major indices, recent performance,
        and any significant trends or events affecting the market.
        """
        
        return self.process_message(prompt)
    
    def compare_stock_analysis(self, tickers: List[str]) -> str:
        """
        Get a comparative analysis of multiple stocks.
        
        Args:
            tickers: List of stock ticker symbols to compare
            
        Returns:
            Natural language comparative analysis
        """
        tickers_str = ", ".join(tickers)
        prompt = f"""
        I need a comparative analysis of the following stocks: {tickers_str}.
        Please compare their current prices, recent performance, key financial metrics,
        and provide insights on which might be the better investment based on the data.
        """
        
        return self.process_message(prompt)
