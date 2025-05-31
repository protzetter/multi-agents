"""
Streamlit application for the Strands Stock Information Agent.

This module provides a web interface for interacting with the Strands stock agent
using Streamlit with streaming responses.
"""
import os
import sys
import time
import logging
from typing import List, Dict, Any
import streamlit as st
from dotenv import load_dotenv

# Add the project root to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))


# Import the Strands Stock Information Agent
from src.agents.strands.stock_info_agent import stock_agent_streaming
from src.utils.finance.yahoo_finance import yahoo_finance

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../config/.env'))

# Initialize session state variables if they don't exist
def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    if 'market_overview' not in st.session_state:
        st.session_state.market_overview = None
    
    if 'last_market_update' not in st.session_state:
        st.session_state.last_market_update = None
        
    if 'streaming_response' not in st.session_state:
        st.session_state.streaming_response = ""

def display_stock_info(stock_info: Dict[str, Any]):
    """Display stock information in a formatted way."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="Current Price", 
            value=f"{stock_info.get('current_price', 'N/A')} {stock_info.get('currency', 'USD')}",
            delta=None
        )
        st.metric(
            label="Market Cap", 
            value=stock_info.get('market_cap_formatted', stock_info.get('market_cap', 'N/A')),
            delta=None
        )
        st.metric(
            label="P/E Ratio", 
            value=stock_info.get('pe_ratio', 'N/A'),
            delta=None
        )
    
    with col2:
        st.metric(
            label="52-Week Range", 
            value=f"{stock_info.get('fifty_two_week_low', 'N/A')} - {stock_info.get('fifty_two_week_high', 'N/A')}",
            delta=None
        )
        st.metric(
            label="Dividend Yield", 
            value=stock_info.get('dividend_yield_formatted', 'N/A'),
            delta=None
        )
        st.metric(
            label="Average Volume", 
            value=f"{stock_info.get('avg_volume', 'N/A'):,}",
            delta=None
        )
    
    st.write(f"**Sector:** {stock_info.get('sector', 'N/A')}")
    st.write(f"**Industry:** {stock_info.get('industry', 'N/A')}")
    
    if stock_info.get('business_summary'):
        with st.expander("Business Summary"):
            st.write(stock_info.get('business_summary', 'No summary available'))

def display_historical_data(historical_data: List[Dict[str, Any]]):
    """Display historical stock data."""
    if not historical_data:
        st.warning("No historical data available")
        return
    
    # Create a simple chart of closing prices
    chart_data = {
        'Date': [record['date'] for record in historical_data],
        'Close': [record['close'] for record in historical_data]
    }
    
    st.line_chart(chart_data, x='Date', y='Close')
    
    # Calculate some basic stats
    if historical_data:
        first_price = historical_data[0]['close']
        last_price = historical_data[-1]['close']
        change = last_price - first_price
        percent_change = (change / first_price) * 100 if first_price else 0
        
        # Find highest and lowest prices
        highest = max(historical_data, key=lambda x: x['close'])
        lowest = min(historical_data, key=lambda x: x['close'])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            change_color = "green" if change > 0 else "red"
            st.markdown(f"**Change:** <span style='color:{change_color}'>{change:.2f} ({percent_change:.2f}%)</span>", unsafe_allow_html=True)
        
        with col2:
            st.write(f"**Highest:** {highest['close']} on {highest['date']}")
        
        with col3:
            st.write(f"**Lowest:** {lowest['close']} on {lowest['date']}")

def display_news(news: List[Dict[str, Any]]):
    """Display news articles."""
    if not news:
        st.info("No recent news available")
        return
    
    for item in news:
        with st.expander(f"{item.get('title', 'No title')} ({item.get('publish_time', 'Unknown date')})"):
            st.write(f"**Publisher:** {item.get('publisher', 'Unknown')}")
            st.write(f"**Type:** {item.get('type', 'Article')}")
            
            if item.get('thumbnail'):
                st.image(item.get('thumbnail'), width=200)
            
            st.markdown(f"[Read more]({item.get('link', '#')})")

def display_market_overview():
    """Display market overview."""
    # Check if we need to update the market overview (every 15 minutes)
    current_time = time.time()
    if (st.session_state.last_market_update is None or 
        current_time - st.session_state.last_market_update > 900):  # 15 minutes = 900 seconds
        
        with st.spinner("Fetching market overview..."):
            try:
                # Get raw market data from Yahoo Finance first (while AI is thinking)
                market_data = yahoo_finance.get_market_summary()
                
                # Create a placeholder for streaming response
                response_placeholder = st.empty()
                st.session_state.streaming_response = ""
                
                # Define callback function for streaming
                def update_response(chunk):
                    try:
                        if chunk and hasattr(chunk, 'content') and chunk.content and len(chunk.content) > 0:
                            text_chunk = chunk.content[0].text if hasattr(chunk.content[0], 'text') else str(chunk.content[0])
                            st.session_state.streaming_response += text_chunk
                            response_placeholder.markdown(st.session_state.streaming_response)
                    except Exception as e:
                        st.error(f"Error in streaming callback: {str(e)}")
                
                # Use the Strands agent to get market overview with streaming
                query = "Get the current market overview with major indices"
                
                response = stock_agent_streaming(query, callback=update_response)
                
                # Extract the message from the response
                agent_analysis = st.session_state.streaming_response
                
                # If streaming didn't work, try to get the full response
                if not agent_analysis or len(agent_analysis.strip()) == 0:
                    st.warning("Streaming response was empty, trying to get full response...")
                    try:
                        # Try different ways to extract the response
                        if hasattr(response, 'content') and response.content:
                            agent_analysis = response.content[0].text
                        elif isinstance(response, dict) and 'content' in response:
                            agent_analysis = response['content'][0]['text']
                        elif hasattr(response, 'message'):
                            agent_analysis = response.message
                        else:
                            # Last resort: convert the whole response to string
                            agent_analysis = str(response)
                            
                        # Update the placeholder with the full response
                        response_placeholder.markdown(agent_analysis)
                    except (AttributeError, IndexError, KeyError) as e:
                        st.error(f"Error extracting response: {str(e)}")
                        agent_analysis = "Unable to retrieve market analysis. Please try again."
                
                # Parse the response to extract market data
                st.session_state.market_overview = {
                    'agent_response': agent_analysis,
                    'timestamp': current_time
                }
                
                # Add market data if available
                if 'error' not in market_data:
                    st.session_state.market_overview['indices'] = market_data.get('indices', {})
                
                st.session_state.last_market_update = current_time
            except Exception as e:
                st.error(f"Error fetching market overview: {str(e)}")
                return
    
    overview = st.session_state.market_overview
    
    # Display major indices if available
    if 'indices' in overview:
        st.subheader("Major Indices")
        
        cols = st.columns(3)
        col_index = 0
        
        for symbol, index in overview['indices'].items():
            if 'error' not in index:
                with cols[col_index % 3]:
                    change = index.get('change', 0)
                    change_color = "green" if change > 0 else "red"
                    
                    st.metric(
                        label=f"{index['name']} ({symbol})",
                        value=index['price'],
                        delta=f"{change} ({index.get('change_percent_formatted', 'N/A')})"
                    )
                    
                col_index += 1
    
    # Display agent's market analysis
    if ('agent_response' in overview and overview['agent_response'] and 
        isinstance(overview['agent_response'], str) and len(overview['agent_response'].strip()) > 0):
        st.subheader("Market Analysis")
        st.write(overview['agent_response'])
    else:
        st.error("No market analysis available. The model did not return a response.")
    
    # Display last update time
    if st.session_state.last_market_update:
        st.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.session_state.last_market_update))}")

def compare_stocks(tickers: List[str]):
    """Compare multiple stocks."""
    if not tickers:
        st.warning("Please enter at least one ticker symbol")
        return
    
    # Create a placeholder for streaming response
    response_placeholder = st.empty()
    st.session_state.streaming_response = ""
    
    with st.spinner(f"Comparing stocks: {', '.join(tickers)}..."):
        try:
            # Get raw comparison data from Yahoo Finance first (while AI is thinking)
            comparison_data = yahoo_finance.get_multiple_quotes(tickers)
            stock_infos = {}
            for ticker in tickers:
                stock_infos[ticker] = yahoo_finance.get_stock_info(ticker)
            
            # Define callback function for streaming
            def update_response(chunk):
                try:
                    if chunk and hasattr(chunk, 'content') and chunk.content and len(chunk.content) > 0:
                        text_chunk = chunk.content[0].text if hasattr(chunk.content[0], 'text') else str(chunk.content[0])
                        st.session_state.streaming_response += text_chunk
                        response_placeholder.markdown(st.session_state.streaming_response)
                except Exception as e:
                    st.error(f"Error in streaming callback: {str(e)}")
            
            # Use the Strands agent to compare stocks with streaming
            query = f"Compare these stocks in detail: {', '.join(tickers)}"
            
            response = stock_agent_streaming(query, callback=update_response)
            
            # Extract the message from the response
            comparison_analysis = st.session_state.streaming_response
            
            # If streaming didn't work, try to get the full response
            if not comparison_analysis or len(comparison_analysis.strip()) == 0:
                st.warning("Streaming response was empty, trying to get full response...")
                try:
                    # Try different ways to extract the response
                    if hasattr(response, 'content') and response.content:
                        comparison_analysis = response.content[0].text
                    elif isinstance(response, dict) and 'content' in response:
                        comparison_analysis = response['content'][0]['text']
                    elif hasattr(response, 'message'):
                        comparison_analysis = response.message
                    else:
                        # Last resort: convert the whole response to string
                        comparison_analysis = str(response)
                        
                    # Update the placeholder with the full response
                    response_placeholder.markdown(comparison_analysis)
                except (AttributeError, IndexError, KeyError) as e:
                    st.error(f"Error extracting response: {str(e)}")
                    comparison_analysis = "Unable to retrieve comparison analysis. Please try again."
            
        except Exception as e:
            st.error(f"Error comparing stocks: {str(e)}")
            return
    
    # Display comparison data
    st.subheader("Stock Comparison")
    
    # Create a table of key metrics
    table_data = []
    for ticker in tickers:
        info = stock_infos.get(ticker, {})
        quote = comparison_data.get(ticker, {})
        
        if 'error' not in info and 'error' not in quote:
            row = {
                'Ticker': ticker,
                'Name': info.get('name', 'N/A'),
                'Price': quote.get('price', info.get('current_price', 'N/A')),
                'Change': f"{quote.get('change', 'N/A')} ({quote.get('change_percent_formatted', 'N/A')})",
                'Market Cap': info.get('market_cap_formatted', info.get('market_cap', 'N/A')),
                'P/E Ratio': info.get('pe_ratio', 'N/A'),
                'Sector': info.get('sector', 'N/A'),
                'Industry': info.get('industry', 'N/A')
            }
            table_data.append(row)
    
    # Display the table
    if table_data:
        st.dataframe(table_data)
    
    # Display the agent's analysis
    st.subheader("Comparison Analysis")
    if (comparison_analysis and isinstance(comparison_analysis, str) and 
        len(comparison_analysis.strip()) > 0):
        st.write(comparison_analysis)
    else:
        st.error("No comparison analysis available. The model did not return a response.")

def get_stock_summary(ticker: str):
    """Get and display a comprehensive summary of a stock."""
    if not ticker:
        st.warning("Please enter a ticker symbol")
        return
    
    # Create a placeholder for streaming response
    response_placeholder = st.empty()
    st.session_state.streaming_response = ""
    
    with st.spinner(f"Fetching information for {ticker}..."):
        try:
            # Also get raw stock data for display first (while the AI is thinking)
            stock_info = yahoo_finance.get_stock_info(ticker)
            historical_data = yahoo_finance.get_historical_data(ticker, period='1mo', interval='1d')
            news = yahoo_finance.get_company_news(ticker, limit=3)
            
            # Define callback function for streaming
            def update_response(chunk):
                try:
                    if chunk and hasattr(chunk, 'content') and chunk.content and len(chunk.content) > 0:
                        text_chunk = chunk.content[0].text if hasattr(chunk.content[0], 'text') else str(chunk.content[0])
                        st.session_state.streaming_response += text_chunk
                        response_placeholder.markdown(st.session_state.streaming_response)
                except Exception as e:
                    st.error(f"Error in streaming callback: {str(e)}")
            
            # Use the Strands agent to get stock summary with streaming
            query = f"Give me a detailed analysis of {ticker} stock including current price, performance, and key metrics"
            
            # Call the agent with streaming
            response = stock_agent_streaming(query, callback=update_response)
            
            # Extract the message from the response
            agent_analysis = st.session_state.streaming_response
            
            # If streaming didn't work, try to get the full response
            if not agent_analysis or len(agent_analysis.strip()) == 0:
                st.warning("Streaming response was empty, trying to get full response...")
                try:
                    # Try different ways to extract the response
                    if hasattr(response, 'content') and response.content:
                        agent_analysis = response.content[0].text
                    elif isinstance(response, dict) and 'content' in response:
                        agent_analysis = response['content'][0]['text']
                    elif hasattr(response, 'message'):
                        agent_analysis = response.message
                    else:
                        # Last resort: convert the whole response to string
                        agent_analysis = str(response)
                        
                    # Update the placeholder with the full response
                    response_placeholder.markdown(agent_analysis)
                except (AttributeError, IndexError, KeyError) as e:
                    st.error(f"Error extracting response: {str(e)}")
                    agent_analysis = "Unable to retrieve stock analysis. Please try again."
            
            # Create a summary object
            summary = {
                'ticker': ticker,
                'stock_info': stock_info,
                'historical_data': historical_data.get('data', []),
                'news': news,
                'agent_analysis': agent_analysis,
                'timestamp': time.time()
            }
            
            # Add to history
            st.session_state.history.append(summary)
            
        except Exception as e:
            st.error(f"Error fetching stock summary: {str(e)}")
            return
    
    if 'error' in stock_info:
        st.error(f"Error: {stock_info['error']}")
        return
    
    # Display stock information
    st.header(f"{stock_info.get('name', ticker)} ({stock_info.get('symbol', ticker)})")
    display_stock_info(stock_info)
    
    # Display AI-generated summary
    st.subheader("AI Analysis")
    if (summary['agent_analysis'] and isinstance(summary['agent_analysis'], str) and 
        len(summary['agent_analysis'].strip()) > 0):
        st.write(summary['agent_analysis'])
    else:
        st.error("No AI analysis available. The model did not return a response.")
    
    # Display tabs for historical data and news
    tab1, tab2 = st.tabs(["Historical Performance", "Recent News"])
    
    with tab1:
        display_historical_data(summary['historical_data'])
    
    with tab2:
        display_news(summary['news'])

def search_stocks(query: str):
    """Search for stocks by name or ticker."""
    if not query:
        st.warning("Please enter a search query")
        return
    
    # Create a placeholder for streaming response
    response_placeholder = st.empty()
    st.session_state.streaming_response = ""
    
    with st.spinner(f"Searching for '{query}'..."):
        try:
            # Get raw search results first (while AI is thinking)
            results = yahoo_finance.search_stocks(query)
            
            # Define callback function for streaming
            def update_response(chunk):
                try:
                    if chunk and hasattr(chunk, 'content') and chunk.content and len(chunk.content) > 0:
                        text_chunk = chunk.content[0].text if hasattr(chunk.content[0], 'text') else str(chunk.content[0])
                        st.session_state.streaming_response += text_chunk
                        response_placeholder.markdown(st.session_state.streaming_response)
                except Exception as e:
                    st.error(f"Error in streaming callback: {str(e)}")
            
            # Use the Strands agent to search for stocks with streaming
            query_text = f"Search for stocks matching: {query}"
            
            response = stock_agent_streaming(query_text, callback=update_response)
            
            # Extract the message from the response
            search_analysis = st.session_state.streaming_response
            
            # If streaming didn't work, try to get the full response
            if not search_analysis or len(search_analysis.strip()) == 0:
                try:
                    # Try different ways to extract the response
                    if hasattr(response, 'content') and response.content:
                        search_analysis = response.content[0].text
                    elif isinstance(response, dict) and 'content' in response:
                        search_analysis = response['content'][0]['text']
                    elif hasattr(response, 'message'):
                        search_analysis = response.message
                    else:
                        # Last resort: convert the whole response to string
                        search_analysis = str(response)
                        
                    # Update the placeholder with the full response
                    response_placeholder.markdown(search_analysis)
                except (AttributeError, IndexError, KeyError) as e:
                    st.error(f"Error extracting response: {str(e)}")
                    search_analysis = "Unable to retrieve search results. Please try again."
                
        except Exception as e:
            st.error(f"Error searching for stocks: {str(e)}")
            return
    
    if 'error' in results:
        st.error(f"Error: {results['error']}")
        return
    
    if not results:
        st.info(f"No results found for '{query}'")
        return
    
    # Display search results
    st.subheader("Search Results")
    
    for result in results:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**{result.get('name', 'Unknown')}** ({result.get('symbol', 'N/A')})")
            st.caption(f"Exchange: {result.get('exchange', 'N/A')}")
        
        with col2:
            if st.button("View", key=f"view_{result.get('symbol', 'unknown')}"):
                get_stock_summary(result.get('symbol'))
    
    # Display agent's search analysis
    with st.expander("AI Search Analysis"):
        if (search_analysis and isinstance(search_analysis, str) and 
            len(search_analysis.strip()) > 0):
            st.write(search_analysis)
        else:
            st.error("No AI search analysis available. The model did not return a response.")

def main():
    """Main function to run the Streamlit app."""
    # Set page config
    st.set_page_config(
        page_title="Strands Stock Information Agent",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("Strands Stock Information Agent")
        st.write("Powered by Strands SDK and Amazon Bedrock", )
        st.divider()
        
        # Navigation
        st.subheader("Navigation")
        page = st.radio(
            "Select a page",
            options=["Stock Lookup", "Compare Stocks", "Market Overview", "Search", "History"]
        )
        
        st.divider()
        
        # Quick lookup
        st.subheader("Quick Lookup")
        quick_ticker = st.text_input("Enter ticker symbol", key="quick_ticker")
        if st.button("Look Up"):
            page = "Stock Lookup"
            st.session_state.current_ticker = quick_ticker.upper()
    
    # Main content
    if page == "Stock Lookup":
        st.title("Stock Lookup")
        
        # Get ticker from session state or input
        ticker = st.session_state.get('current_ticker', '')
        if not ticker:
            ticker = st.text_input("Enter ticker symbol (e.g., AAPL)", key="main_ticker")
            ticker = ticker.upper()
        
        if ticker:
            get_stock_summary(ticker)
            # Reset current_ticker after use
            st.session_state.current_ticker = ''
    
    elif page == "Compare Stocks":
        st.title("Compare Stocks")
        
        tickers_input = st.text_input(
            "Enter ticker symbols separated by commas (e.g., AAPL,MSFT,GOOGL)",
            key="compare_tickers"
        )
        
        if st.button("Compare") or tickers_input:
            tickers = [t.strip().upper() for t in tickers_input.split(',')]
            compare_stocks(tickers)
    
    elif page == "Market Overview":
        st.title("Market Overview")
        
        # Add a refresh button
        if st.button("Refresh"):
            st.session_state.last_market_update = None
        
        display_market_overview()
    
    elif page == "Search":
        st.title("Search Stocks")
        
        query = st.text_input("Search by company name or ticker", key="search_query")
        
        if st.button("Search") or query:
            search_stocks(query)
    
    elif page == "History":
        st.title("Search History")
        
        if not st.session_state.history:
            st.info("No search history yet")
        else:
            # Sort history by timestamp (newest first)
            sorted_history = sorted(
                st.session_state.history,
                key=lambda x: x['timestamp'],
                reverse=True
            )
            
            for i, item in enumerate(sorted_history):
                with st.expander(
                    f"{item['ticker']} - {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['timestamp']))}",
                    expanded=(i == 0)  # Expand the most recent item
                ):
                    if st.button("View Details", key=f"history_{i}"):
                        st.session_state.current_ticker = item['ticker']
                        st.rerun()
                    
                    if 'stock_info' in item:
                        stock_info = item['stock_info']
                        st.write(f"**{stock_info.get('name', item['ticker'])}** ({stock_info.get('symbol', item['ticker'])})")
                        st.write(f"Price: {stock_info.get('current_price', 'N/A')} {stock_info.get('currency', 'USD')}")
                        st.write(f"Sector: {stock_info.get('sector', 'N/A')}")

if __name__ == "__main__":
    main()
