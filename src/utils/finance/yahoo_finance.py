"""
Yahoo Finance stock information fetcher.

This module provides functionality to fetch stock information from Yahoo Finance.
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Any, List, Optional, Union
import logging
import time
from datetime import datetime, timedelta

# Set up logging
logger = logging.getLogger(__name__)

class YahooFinanceClient:
    """
    Client for fetching stock information from Yahoo Finance.
    
    This class provides methods to fetch stock quotes, historical data,
    company information, and other financial data from Yahoo Finance.
    """
    
    def __init__(self):
        """Initialize the Yahoo Finance client."""
        pass
    
    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get basic information about a stock.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL' for Apple)
            
        Returns:
            Dict containing stock information
        """
        try:
            if not ticker or not ticker.strip():
                logger.error("Empty ticker symbol provided")
                return {
                    'symbol': ticker,
                    'error': "Empty ticker symbol provided",
                    'status': 'error'
                }
                
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Check if we got valid info
            if not info or len(info) < 5:  # Basic check for minimal info
                logger.error(f"Could not retrieve information for ticker: {ticker}")
                return {
                    'symbol': ticker,
                    'error': f"Could not retrieve information for ticker: {ticker}",
                    'status': 'error'
                }
            
            # Extract the most relevant information
            relevant_info = {
                'symbol': ticker,
                'name': info.get('shortName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
                'avg_volume': info.get('averageVolume', 'N/A'),
                'beta': info.get('beta', 'N/A'),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'N/A'),
                'business_summary': info.get('longBusinessSummary', 'N/A')
            }
            
            # Format numbers for better readability
            if isinstance(relevant_info['market_cap'], (int, float)):
                if relevant_info['market_cap'] >= 1e12:
                    relevant_info['market_cap_formatted'] = f"${relevant_info['market_cap']/1e12:.2f}T"
                elif relevant_info['market_cap'] >= 1e9:
                    relevant_info['market_cap_formatted'] = f"${relevant_info['market_cap']/1e9:.2f}B"
                elif relevant_info['market_cap'] >= 1e6:
                    relevant_info['market_cap_formatted'] = f"${relevant_info['market_cap']/1e6:.2f}M"
                    
            if isinstance(relevant_info['dividend_yield'], (int, float)):
                relevant_info['dividend_yield_formatted'] = f"{relevant_info['dividend_yield']*100:.2f}%"
                
            return relevant_info
            
        except Exception as e:
            logger.error(f"Error fetching stock info for {ticker}: {str(e)}")
            return {
                'symbol': ticker,
                'error': str(e),
                'status': 'error'
            }
    
    def get_historical_data(self, ticker: str, period: str = '1mo', interval: str = '1d') -> Dict[str, Any]:
        """
        Get historical price data for a stock.
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            Dict containing historical data
        """
        try:
            if not ticker or not ticker.strip():
                logger.error("Empty ticker symbol provided")
                return {
                    'symbol': ticker,
                    'period': period,
                    'interval': interval,
                    'error': "Empty ticker symbol provided",
                    'status': 'error'
                }
                
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            
            # Check if we got valid data
            if hist.empty:
                logger.error(f"No historical data available for {ticker}")
                return {
                    'symbol': ticker,
                    'period': period,
                    'interval': interval,
                    'error': f"No historical data available for {ticker}",
                    'status': 'error',
                    'data': [],
                    'stats': {
                        'error': 'No data available'
                    }
                }
            
            # Convert to records format for easier processing
            data_records = []
            for date, row in hist.iterrows():
                data_records.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': round(row['Open'], 2) if not pd.isna(row['Open']) else None,
                    'high': round(row['High'], 2) if not pd.isna(row['High']) else None,
                    'low': round(row['Low'], 2) if not pd.isna(row['Low']) else None,
                    'close': round(row['Close'], 2) if not pd.isna(row['Close']) else None,
                    'volume': int(row['Volume']) if not pd.isna(row['Volume']) else 0
                })
            
            # Calculate some basic statistics
            if data_records:
                latest = data_records[-1]['close'] or 0
                earliest = data_records[0]['close'] or 0
                change = latest - earliest
                percent_change = (change / earliest) * 100 if earliest != 0 else 0
                
                # Find highest and lowest points
                valid_records = [r for r in data_records if r['high'] is not None and r['low'] is not None]
                if valid_records:
                    highest = max(valid_records, key=lambda x: x['high'])
                    lowest = min(valid_records, key=lambda x: x['low'])
                    
                    stats = {
                        'start_price': earliest,
                        'end_price': latest,
                        'change': round(change, 2),
                        'percent_change': round(percent_change, 2),
                        'highest': {
                            'price': highest['high'],
                            'date': highest['date']
                        },
                        'lowest': {
                            'price': lowest['low'],
                            'date': lowest['date']
                        }
                    }
                else:
                    stats = {
                        'error': 'Insufficient valid data points'
                    }
            else:
                stats = {
                    'error': 'No data available for the specified period'
                }
            
            return {
                'symbol': ticker,
                'period': period,
                'interval': interval,
                'data': data_records,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {ticker}: {str(e)}")
            return {
                'symbol': ticker,
                'period': period,
                'interval': interval,
                'error': str(e),
                'status': 'error',
                'data': [],
                'stats': {
                    'error': str(e)
                }
            }
    
    def get_multiple_quotes(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get current quotes for multiple stocks.
        
        Args:
            tickers: List of stock ticker symbols
            
        Returns:
            Dict mapping ticker symbols to their quote information
        """
        results = {}
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                quote = stock.info
                
                # Extract just the quote information
                quote_info = {
                    'price': quote.get('currentPrice', quote.get('regularMarketPrice', 'N/A')),
                    'change': quote.get('regularMarketChange', 'N/A'),
                    'change_percent': quote.get('regularMarketChangePercent', 'N/A'),
                    'volume': quote.get('regularMarketVolume', 'N/A'),
                    'market_cap': quote.get('marketCap', 'N/A'),
                    'name': quote.get('shortName', 'N/A')
                }
                
                # Format the percent change
                if isinstance(quote_info['change_percent'], (int, float)):
                    quote_info['change_percent_formatted'] = f"{quote_info['change_percent']:.2f}%"
                
                results[ticker] = quote_info
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error fetching quote for {ticker}: {str(e)}")
                results[ticker] = {
                    'error': str(e),
                    'status': 'error'
                }
        
        return results
    
    def get_company_news(self, ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent news articles about a company.
        
        Args:
            ticker: Stock ticker symbol
            limit: Maximum number of news items to return
            
        Returns:
            List of news article information
        """
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            # Limit the number of news items and extract relevant information
            limited_news = []
            for i, item in enumerate(news):
                if i >= limit:
                    break
                    
                news_item = {
                    'title': item.get('title', 'N/A'),
                    'publisher': item.get('publisher', 'N/A'),
                    'link': item.get('link', '#'),
                    'publish_time': datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                    'type': item.get('type', 'N/A'),
                    'thumbnail': item.get('thumbnail', {}).get('resolutions', [{}])[0].get('url', None)
                }
                limited_news.append(news_item)
            
            return limited_news
            
        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {str(e)}")
            return [{
                'error': str(e),
                'status': 'error'
            }]
    
    def search_stocks(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for stocks by name or ticker.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching stocks
        """
        try:
            # This is a simple implementation since yfinance doesn't have a direct search function
            # For a production system, you might want to use a more robust solution
            tickers = yf.Tickers(query)
            results = []
            
            # Try to get info for the exact ticker match
            try:
                info = tickers.tickers[query].info
                results.append({
                    'symbol': query,
                    'name': info.get('shortName', 'N/A'),
                    'exchange': info.get('exchange', 'N/A'),
                    'type': 'Exact Match'
                })
            except:
                pass
            
            # For a more comprehensive search, you would need to use a different API
            # or maintain your own database of ticker symbols and company names
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error searching for stocks with query '{query}': {str(e)}")
            return [{
                'error': str(e),
                'status': 'error'
            }]
    
    def get_market_summary(self) -> Dict[str, Any]:
        """
        Get a summary of major market indices.
        
        Returns:
            Dict containing market summary information
        """
        indices = ['^GSPC', '^DJI', '^IXIC', '^FTSE', '^N225']  # S&P 500, Dow Jones, NASDAQ, FTSE 100, Nikkei 225
        
        try:
            results = {}
            for index in indices:
                try:
                    idx = yf.Ticker(index)
                    info = idx.info
                    
                    results[index] = {
                        'name': info.get('shortName', 'N/A'),
                        'price': info.get('regularMarketPrice', 'N/A'),
                        'change': info.get('regularMarketChange', 'N/A'),
                        'change_percent': info.get('regularMarketChangePercent', 'N/A'),
                        'previous_close': info.get('regularMarketPreviousClose', 'N/A')
                    }
                    
                    # Format the percent change
                    if isinstance(results[index]['change_percent'], (int, float)):
                        results[index]['change_percent_formatted'] = f"{results[index]['change_percent']:.2f}%"
                    
                    # Add a small delay to avoid rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error fetching data for index {index}: {str(e)}")
                    results[index] = {
                        'name': index,
                        'error': str(e),
                        'status': 'error'
                    }
            
            return {
                'indices': results,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"Error fetching market summary: {str(e)}")
            return {
                'error': str(e),
                'status': 'error'
            }

# Create a singleton instance for easy importing
yahoo_finance = YahooFinanceClient()
