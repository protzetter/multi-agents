"""
Stock Information Agent using AWS Bedrock.

This module provides an agent that can fetch stock information from Yahoo Finance
and use AWS Bedrock to analyze and present the information.
"""
import os
import sys
import logging
import json
from typing import Dict, Any, List, Optional
import boto3
from dotenv import load_dotenv

# Add the project root to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

# Import the Yahoo Finance client
from src.utils.finance.yahoo_finance import yahoo_finance

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../config/.env'))

class StockInfoAgent:
    """
    Agent for fetching and analyzing stock information.
    
    This agent uses Yahoo Finance to fetch stock data and AWS Bedrock
    to analyze and present the information in a user-friendly format.
    """
    
    def __init__(self, model_id: str = None, region: str = None):
        """
        Initialize the Stock Information Agent.
        
        Args:
            model_id: AWS Bedrock model ID to use (defaults to environment variable or Claude)
            region: AWS region to use (defaults to environment variable or us-east-1)
        """
        # Get configuration from environment variables if not provided
        self.region = region or os.environ.get('AWS_REGION', 'us-east-1')
        self.model_id = model_id or os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-v2:1')
        
        logger.info(f"Initializing StockInfoAgent with region={self.region}, model_id={self.model_id}")
        
        try:
            self.bedrock_client = boto3.client('bedrock-runtime', region_name=self.region)
            logger.info("Successfully created Bedrock client")
        except Exception as e:
            logger.error(f"Error creating Bedrock client: {str(e)}")
            raise
    
    def get_stock_summary(self, ticker: str) -> Dict[str, Any]:
        """
        Get a comprehensive summary of a stock.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL' for Apple)
            
        Returns:
            Dict containing stock summary information
        """
        try:
            # Fetch basic stock information
            stock_info = yahoo_finance.get_stock_info(ticker)
            
            # Fetch historical data for the past month
            historical_data = yahoo_finance.get_historical_data(ticker, period='1mo')
            
            # Fetch recent news about the company
            news = yahoo_finance.get_company_news(ticker, limit=3)
            
            # Combine all the information
            summary = {
                'stock_info': stock_info,
                'historical_data': historical_data,
                'news': news
            }
            
            # Use Bedrock to generate a natural language summary
            nl_summary = self._generate_summary(summary)
            if nl_summary:
                summary['natural_language_summary'] = nl_summary
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting stock summary for {ticker}: {str(e)}")
            return {
                'symbol': ticker,
                'error': str(e),
                'status': 'error'
            }
    
    def compare_stocks(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Compare multiple stocks.
        
        Args:
            tickers: List of stock ticker symbols to compare
            
        Returns:
            Dict containing comparison information
        """
        try:
            # Fetch quotes for all tickers
            quotes = yahoo_finance.get_multiple_quotes(tickers)
            
            # Fetch basic info for all tickers
            stock_infos = {}
            for ticker in tickers:
                stock_infos[ticker] = yahoo_finance.get_stock_info(ticker)
            
            # Combine the information
            comparison = {
                'quotes': quotes,
                'stock_infos': stock_infos
            }
            
            # Use Bedrock to generate a comparison analysis
            analysis = self._generate_comparison(comparison)
            if analysis:
                comparison['analysis'] = analysis
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing stocks {tickers}: {str(e)}")
            return {
                'tickers': tickers,
                'error': str(e),
                'status': 'error'
            }
    
    def get_market_overview(self) -> Dict[str, Any]:
        """
        Get an overview of the current market conditions.
        
        Returns:
            Dict containing market overview information
        """
        try:
            # Fetch market summary
            market_summary = yahoo_finance.get_market_summary()
            
            # Use Bedrock to generate a market analysis
            analysis = self._generate_market_analysis(market_summary)
            if analysis:
                market_summary['analysis'] = analysis
            
            return market_summary
            
        except Exception as e:
            logger.error(f"Error getting market overview: {str(e)}")
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def _generate_summary(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Generate a natural language summary of stock information using AWS Bedrock.
        
        Args:
            data: Stock information data
            
        Returns:
            String containing the natural language summary, or None if generation fails
        """
        try:
            # Extract the most relevant information for the summary
            stock_info = data['stock_info']
            historical_data = data['historical_data']
            news = data['news']
            
            # Create a prompt for the model
            prompt_text = f"""
            Generate a concise summary of {stock_info.get('name', 'the company')} ({stock_info.get('symbol', '')}) based on the following information:
            
            COMPANY INFORMATION:
            - Current Price: {stock_info.get('current_price', 'N/A')} {stock_info.get('currency', 'USD')}
            - Market Cap: {stock_info.get('market_cap_formatted', stock_info.get('market_cap', 'N/A'))}
            - P/E Ratio: {stock_info.get('pe_ratio', 'N/A')}
            - Dividend Yield: {stock_info.get('dividend_yield_formatted', stock_info.get('dividend_yield', 'N/A'))}
            - 52-Week Range: {stock_info.get('fifty_two_week_low', 'N/A')} - {stock_info.get('fifty_two_week_high', 'N/A')}
            - Sector: {stock_info.get('sector', 'N/A')}
            - Industry: {stock_info.get('industry', 'N/A')}
            
            RECENT PERFORMANCE:
            """
            
            # Add performance data if available
            if 'stats' in historical_data and 'error' not in historical_data['stats']:
                prompt_text += f"""
                - Period: {historical_data['period']}
                - Price Change: {historical_data['stats'].get('change', 'N/A')} ({historical_data['stats'].get('percent_change', 'N/A')}%)
                - Highest: {historical_data['stats'].get('highest', {}).get('price', 'N/A')} on {historical_data['stats'].get('highest', {}).get('date', 'N/A')}
                - Lowest: {historical_data['stats'].get('lowest', {}).get('price', 'N/A')} on {historical_data['stats'].get('lowest', {}).get('date', 'N/A')}
                """
            else:
                prompt_text += "\n- Historical performance data not available\n"
            
            # Add news items to the prompt
            prompt_text += "\nRECENT NEWS:\n"
            if news and len(news) > 0:
                for item in news:
                    prompt_text += f"- {item.get('title', 'No title')} ({item.get('publish_time', 'No date')})\n"
            else:
                prompt_text += "- No recent news available\n"
            
            prompt_text += """
            Based on this information, provide a concise 3-paragraph summary that covers:
            1. Current company status and financial position
            2. Recent stock performance and key metrics
            3. Brief outlook based on recent news and industry trends
            
            Keep your response under 300 words and focus on the most important information for an investor.
            """
            
            # Check if we're using a Nova model
            if 'nova' in self.model_id.lower():
                # Nova models use a chat-based API
                body = json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": prompt_text
                                }
                            ]
                        }
                    ]
                })
            elif 'claude' in self.model_id.lower():
                # Claude models use a different format
                body = json.dumps({
                    "prompt": f"\n\nHuman: {prompt_text}\n\nAssistant:",
                    "max_tokens_to_sample": 1024,
                    "temperature": 0.2,
                    "top_p": 0.9
                })
            else:
                # Generic format for other models
                body = json.dumps({
                    "prompt": prompt_text,
                    "max_tokens": 1024,
                    "temperature": 0.2,
                    "top_p": 0.9
                })
            
            # Call the Bedrock model
            logger.info(f"Calling Bedrock model: {self.model_id}")
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            # Parse the response based on the model
            response_body = json.loads(response['body'].read().decode('utf-8'))
            logger.debug(f"Response body keys: {response_body.keys()}")
            
            # Different models have different response formats
            if 'completion' in response_body:
                # Claude-style response
                summary = response_body['completion']
            elif 'output' in response_body and 'message' in response_body['output']:
                # Nova-style response
                summary = response_body['output']['message']['content'][0]['text']
            elif 'generated_text' in response_body:
                # Mistral/Llama style response
                summary = response_body['generated_text']
            elif 'results' in response_body and len(response_body['results']) > 0:
                # Some models use this format
                summary = response_body['results'][0]['outputText']
            else:
                # Fallback - try to find any text field
                for key, value in response_body.items():
                    if isinstance(value, str) and len(value) > 50:
                        summary = value
                        break
                else:
                    logger.error(f"Could not parse model response: {response_body}")
                    return None
                
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return None
    
    def _generate_comparison(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Generate a comparison analysis of multiple stocks using AWS Bedrock.
        
        Args:
            data: Stock comparison data
            
        Returns:
            String containing the comparison analysis, or None if generation fails
        """
        try:
            quotes = data['quotes']
            stock_infos = data['stock_infos']
            
            # Create a prompt for the model
            prompt_text = "Compare the following stocks based on their key metrics:\n\n"
            
            for ticker, info in stock_infos.items():
                quote = quotes.get(ticker, {})
                prompt_text += f"""
                {info.get('name', ticker)} ({ticker}):
                - Price: {quote.get('price', 'N/A')} {info.get('currency', 'USD')}
                - Change: {quote.get('change', 'N/A')} ({quote.get('change_percent_formatted', 'N/A')})
                - Market Cap: {info.get('market_cap_formatted', info.get('market_cap', 'N/A'))}
                - P/E Ratio: {info.get('pe_ratio', 'N/A')}
                - Sector: {info.get('sector', 'N/A')}
                - Industry: {info.get('industry', 'N/A')}
                
                """
            
            prompt_text += """
            Provide a comparative analysis of these stocks, including:
            1. Which stock(s) appear to be performing better recently
            2. Key differences in valuation metrics
            3. Industry and sector comparisons
            4. Brief investment recommendation based on the data
            
            Keep your response under 400 words and focus on the most important comparative insights.
            """
            
            # Check if we're using a Nova model
            if 'nova' in self.model_id.lower():
                # Nova models use a chat-based API
                body = json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": prompt_text
                                }
                            ]
                        }
                    ]
                })
            elif 'claude' in self.model_id.lower():
                # Claude models use a different format
                body = json.dumps({
                    "prompt": f"\n\nHuman: {prompt_text}\n\nAssistant:",
                    "max_tokens_to_sample": 1024,
                    "temperature": 0.2,
                    "top_p": 0.9
                })
            else:
                # Generic format for other models
                body = json.dumps({
                    "prompt": prompt_text,
                    "max_tokens": 1024,
                    "temperature": 0.2
                })
            
            # Call the Bedrock model
            logger.info(f"Calling Bedrock model: {self.model_id}")
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            # Parse the response based on the model
            response_body = json.loads(response['body'].read().decode('utf-8'))
            logger.debug(f"Response body keys: {response_body.keys()}")
            
            # Different models have different response formats
            if 'completion' in response_body:
                # Claude-style response
                analysis = response_body['completion']
            elif 'output' in response_body and 'message' in response_body['output']:
                # Nova-style response
                analysis = response_body['output']['message']['content'][0]['text']
            elif 'generated_text' in response_body:
                # Mistral/Llama style response
                analysis = response_body['generated_text']
            elif 'results' in response_body and len(response_body['results']) > 0:
                # Some models use this format
                analysis = response_body['results'][0]['outputText']
            else:
                # Fallback - try to find any text field
                for key, value in response_body.items():
                    if isinstance(value, str) and len(value) > 50:
                        analysis = value
                        break
                else:
                    logger.error(f"Could not parse model response: {response_body}")
                    return None
                
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating comparison: {str(e)}")
            return None
    
    def _generate_market_analysis(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Generate a market analysis using AWS Bedrock.
        
        Args:
            data: Market summary data
            
        Returns:
            String containing the market analysis, or None if generation fails
        """
        try:
            indices = data['indices']
            
            # Create a prompt for the model
            prompt_text = f"""
            Generate a market overview based on the following major indices as of {data['timestamp']}:
            
            """
            
            for symbol, index in indices.items():
                if 'error' not in index:
                    prompt_text += f"""
                    {index['name']} ({symbol}):
                    - Current: {index['price']}
                    - Change: {index['change']} ({index.get('change_percent_formatted', 'N/A')})
                    - Previous Close: {index['previous_close']}
                    
                    """
            
            prompt_text += """
            Provide a concise market overview that includes:
            1. General market sentiment based on the performance of these indices
            2. Notable movements and possible reasons
            3. Brief outlook for the near term
            
            Keep your response under 250 words and focus on the most important market insights.
            """
            
            # Check if we're using a Nova model
            if 'nova' in self.model_id.lower():
                # Nova models use a chat-based API
                body = json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": prompt_text
                                }
                            ]
                        }
                    ]
                })
            elif 'claude' in self.model_id.lower():
                # Claude models use a different format
                body = json.dumps({
                    "prompt": f"\n\nHuman: {prompt_text}\n\nAssistant:",
                    "max_tokens_to_sample": 1024,
                    "temperature": 0.2,
                    "top_p": 0.9
                })
            else:
                # Generic format for other models
                body = json.dumps({
                    "prompt": prompt_text,
                    "max_tokens": 1024,
                    "temperature": 0.2,
                    "top_p": 0.9
                })
            
            # Call the Bedrock model
            logger.info(f"Calling Bedrock model: {self.model_id}")
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            # Parse the response based on the model
            response_body = json.loads(response['body'].read().decode('utf-8'))
            logger.debug(f"Response body keys: {response_body.keys()}")
            
            # Different models have different response formats
            if 'completion' in response_body:
                # Claude-style response
                analysis = response_body['completion']
            elif 'output' in response_body and 'message' in response_body['output']:
                # Nova-style response
                analysis = response_body['output']['message']['content'][0]['text']
            elif 'generated_text' in response_body:
                # Mistral/Llama style response
                analysis = response_body['generated_text']
            elif 'results' in response_body and len(response_body['results']) > 0:
                # Some models use this format
                analysis = response_body['results'][0]['outputText']
            else:
                # Fallback - try to find any text field
                for key, value in response_body.items():
                    if isinstance(value, str) and len(value) > 50:
                        analysis = value
                        break
                else:
                    logger.error(f"Could not parse model response: {response_body}")
                    return None
                
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating market analysis: {str(e)}")
            return None
