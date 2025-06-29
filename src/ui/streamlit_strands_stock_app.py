"""
Streamlit application for the Strands Stock Information Agent.

This module provides a web interface for interacting with the Strands stock agent
using Streamlit with streaming responses.
"""
import os
import sys
import time
import logging
from typing import List, Dict, Any, Optional
import streamlit as st
from dotenv import load_dotenv
import pandas as pd

# Add the project root to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

try:
    # Import the Strands Stock Information Agent
    from src.agents.strands.stock_info_agent import ask_stock_agent
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure the required modules are available in the project structure.")
    st.stop()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def safe_format_number(value: Any, default: str = "N/A") -> str:
    """Safely format a number for display."""
    if value is None:
        return default
    try:
        if isinstance(value, (int, float)):
            return f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
        return str(value)
    except (ValueError, TypeError):
        return default

def display_stock_info(stock_info: Dict[str, Any]):
    """Display stock information in a formatted way."""
    if not stock_info or 'error' in stock_info:
        st.error(f"Error loading stock info: {stock_info.get('error', 'Unknown error')}")
        return
        
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="Current Price", 
            value=f"{safe_format_number(stock_info.get('current_price'))} {stock_info.get('currency', 'USD')}",
            delta=None
        )
        st.metric(
            label="Market Cap", 
            value=stock_info.get('market_cap_formatted', safe_format_number(stock_info.get('market_cap'))),
            delta=None
        )
        st.metric(
            label="P/E Ratio", 
            value=safe_format_number(stock_info.get('pe_ratio')),
            delta=None
        )
    
    with col2:
        fifty_two_low = safe_format_number(stock_info.get('fifty_two_week_low'))
        fifty_two_high = safe_format_number(stock_info.get('fifty_two_week_high'))
        st.metric(
            label="52-Week Range", 
            value=f"{fifty_two_low} - {fifty_two_high}",
            delta=None
        )
        st.metric(
            label="Dividend Yield", 
            value=stock_info.get('dividend_yield_formatted', safe_format_number(stock_info.get('dividend_yield'))),
            delta=None
        )
        st.metric(
            label="Average Volume", 
            value=safe_format_number(stock_info.get('avg_volume')),
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
    
    try:
        # Create a DataFrame for better chart handling
        df = pd.DataFrame(historical_data)
        
        if 'date' in df.columns and 'close' in df.columns:
            # Convert date column to datetime if it's not already
            df['date'] = pd.to_datetime(df['date'])
            
            # Create a line chart
            st.line_chart(df.set_index('date')['close'])
            
            # Calculate some basic stats
            if len(historical_data) > 1:
                first_price = historical_data[0]['close']
                last_price = historical_data[-1]['close']
                change = last_price - first_price
                percent_change = (change / first_price) * 100 if first_price else 0
                
                # Find highest and lowest prices
                highest = max(historical_data, key=lambda x: x.get('close', 0))
                lowest = min(historical_data, key=lambda x: x.get('close', float('inf')))
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    change_color = "green" if change > 0 else "red"
                    st.markdown(f"**Change:** <span style='color:{change_color}'>{change:.2f} ({percent_change:.2f}%)</span>", unsafe_allow_html=True)
                
                with col2:
                    st.write(f"**Highest:** {highest.get('close', 'N/A')} on {highest.get('date', 'N/A')}")
                
                with col3:
                    st.write(f"**Lowest:** {lowest.get('close', 'N/A')} on {lowest.get('date', 'N/A')}")
        else:
            st.warning("Historical data format not recognized")
            
    except Exception as e:
        st.error(f"Error displaying historical data: {str(e)}")
        logger.error(f"Error in display_historical_data: {e}")

def display_news(news: List[Dict[str, Any]]):
    """Display news articles."""
    if not news:
        st.info("No recent news available")
        return
    
    for item in news:
        title = item.get('title', 'No title')
        publish_time = item.get('publish_time', 'Unknown date')
        
        with st.expander(f"{title} ({publish_time})"):
            st.write(f"**Publisher:** {item.get('publisher', 'Unknown')}")
            st.write(f"**Type:** {item.get('type', 'Article')}")
            
            if item.get('thumbnail'):
                try:
                    st.image(item.get('thumbnail'), width=200)
                except Exception as e:
                    logger.warning(f"Could not load thumbnail: {e}")
            
            link = item.get('link', '#')
            if link != '#':
                st.markdown(f"[Read more]({link})")

def display_market_overview():
    """Display market overview."""
    # Check if we need to update the market overview (every 15 minutes)
    current_time = time.time()
    if (st.session_state.last_market_update is None or 
        current_time - st.session_state.last_market_update > 900):  # 15 minutes = 900 seconds
        
        with st.spinner("Fetching market overview..."):
            try:
                # Create a placeholder for streaming response
                response_placeholder = st.empty()
                st.session_state.streaming_response = ""
                
                # Use the Strands agent to get market overview
                query = "Get the current market overview with major indices"
                
                # Get agent analysis
                agent_analysis = ask_stock_agent(query)
                
                # Validate response
                if not agent_analysis or (isinstance(agent_analysis, str) and len(agent_analysis.strip()) == 0):
                    agent_analysis = "Unable to retrieve market analysis at this time. Please try again later."
                
                # Update the placeholder with the response
                response_placeholder.markdown(agent_analysis)
                
                # Store the market overview
                st.session_state.market_overview = {
                    'agent_response': agent_analysis,
                    'timestamp': current_time
                }             
                st.session_state.last_market_update = current_time
                
            except Exception as e:
                st.error(f"Error fetching market overview: {str(e)}")
                logger.error(f"Error in display_market_overview: {e}")
                return
    
    overview = st.session_state.market_overview
    if not overview:
        st.error("No market overview available")
        return
    
    # Display major indices if available
    if 'indices' in overview and overview['indices']:
        st.subheader("Major Indices")
        
        cols = st.columns(3)
        col_index = 0
        
        for symbol, index in overview['indices'].items():
            if isinstance(index, dict) and 'error' not in index:
                with cols[col_index % 3]:
                    change = index.get('change', 0)
                    
                    st.metric(
                        label=f"{index.get('name', symbol)} ({symbol})",
                        value=safe_format_number(index.get('price')),
                        delta=f"{safe_format_number(change)} ({index.get('change_percent_formatted', 'N/A')})"
                    )
                    
                col_index += 1
    
   

def compare_stocks(tickers: List[str]):
    """Compare multiple stocks."""
    if not tickers:
        st.warning("Please enter at least one ticker symbol")
        return
    
    # Filter out empty tickers
    tickers = [t for t in tickers if t.strip()]
    if not tickers:
        st.warning("Please enter valid ticker symbols")
        return
    
    # Create a placeholder for streaming response
    response_placeholder = st.empty()
    st.session_state.streaming_response = ""
    
    with st.spinner(f"Comparing stocks: {', '.join(tickers)}..."):
        try:
            # Use the Strands agent to compare stocks
            query = f"Compare these stocks in detail: {', '.join(tickers)}"
            
            comparison_analysis = ask_stock_agent(query)
            
            # Validate response
            if not comparison_analysis or (isinstance(comparison_analysis, str) and len(comparison_analysis.strip()) == 0):
                comparison_analysis = "Unable to retrieve comparison analysis. Please try again."
            
            # Update the placeholder with the response
            response_placeholder.markdown(comparison_analysis)
            
        except Exception as e:
            st.error(f"Error comparing stocks: {str(e)}")
            logger.error(f"Error in compare_stocks: {e}")
            return

def get_stock_summary(ticker: str):
    """Get and display a comprehensive summary of a stock."""
    if not ticker or not ticker.strip():
        st.warning("Please enter a ticker symbol")
        return
    
    ticker = ticker.strip().upper()
    
    # Create a placeholder for streaming response
    response_placeholder = st.empty()
    st.session_state.streaming_response = ""
    
    with st.spinner(f"Fetching information for {ticker}..."):
        try:           
            # Use the Strands agent to get stock summary
            query = f"Give me a detailed analysis of {ticker} stock including current price, performance, and key metrics"
            
            agent_analysis = ask_stock_agent(query)
            
            # Validate response
            if not agent_analysis or (isinstance(agent_analysis, str) and len(agent_analysis.strip()) == 0):
                agent_analysis = f"Unable to retrieve detailed analysis for {ticker}. Please try again."
            
            # Update the placeholder with the response
            response_placeholder.markdown(agent_analysis)
            
            # Create a summary object
            summary = {
                'ticker': ticker,
                'agent_analysis': agent_analysis,
                'timestamp': time.time()
            }
            
            # Add to history
            st.session_state.history.append(summary)
            
        except Exception as e:
            st.error(f"Error fetching stock summary: {str(e)}")
            logger.error(f"Error in get_stock_summary: {e}")
            return

def search_stocks(query: str):
    """Search for stocks by name or ticker."""
    if not query or not query.strip():
        st.warning("Please enter a search query")
        return
    
    query = query.strip()
    
    # Create a placeholder for streaming response
    response_placeholder = st.empty()
    st.session_state.streaming_response = ""
    
    with st.spinner(f"Searching for '{query}'..."):
        try:
            # Get raw search results first
            results = []
            try:
                search_results = yahoo_finance.search_stocks(query)
                if isinstance(search_results, list):
                    # Filter out error results
                    results = [r for r in search_results if isinstance(r, dict) and 'error' not in r]
                    
                    # If no results from search, try treating the query as a direct ticker
                    if not results:
                        try:
                            # Try to get stock info directly (in case it's a valid ticker)
                            direct_info = yahoo_finance.get_stock_info(query.upper())
                            if direct_info and 'error' not in direct_info:
                                results = [{
                                    'symbol': direct_info.get('symbol', query.upper()),
                                    'name': direct_info.get('name', 'N/A'),
                                    'exchange': direct_info.get('exchange', 'N/A'),
                                    'type': 'Direct Match'
                                }]
                        except Exception as e:
                            logger.debug(f"Direct ticker lookup failed for {query}: {e}")
                            
                elif isinstance(search_results, dict) and 'error' in search_results:
                    logger.warning(f"Search error: {search_results['error']}")
                    results = []
            except Exception as e:
                logger.warning(f"Could not search stocks: {e}")
                results = []
            
            # Use the Strands agent to search for stocks
            query_text = f"Search for stocks matching: {query}"
            
            search_analysis = ask_stock_agent(query_text)
            
            # Validate response
            if not search_analysis or (isinstance(search_analysis, str) and len(search_analysis.strip()) == 0):
                search_analysis = f"Unable to retrieve search analysis for '{query}'. Please try again."
            
            # Update the placeholder with the response
            response_placeholder.markdown(search_analysis)
                
        except Exception as e:
            st.error(f"Error searching for stocks: {str(e)}")
            logger.error(f"Error in search_stocks: {e}")
            return

    # Display agent's search analysis
    with st.expander("AI Search Analysis"):
        if search_analysis and isinstance(search_analysis, str) and len(search_analysis.strip()) > 0:
            st.write(search_analysis)
        else:
            st.error("No AI search analysis available.")

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
        st.write("Powered by Strands SDK and Amazon Bedrock")
        st.divider()
        
        # Navigation
        st.subheader("Navigation")
        page = st.radio(
            "Select a page",
            options=["Stock Lookup", "Compare Stocks", "Market Overview"]
        )
        
    # Main content
    if page == "Stock Lookup":
        st.title("Stock Lookup")
        
        # Get ticker from session state or input
        ticker = st.session_state.get('current_ticker', '')
        if not ticker:
            ticker = st.text_input("Enter ticker symbol (e.g., AAPL)", key="main_ticker")
            if ticker:
                ticker = ticker.upper().strip()
        
        if ticker:
            get_stock_summary(ticker)
            # Reset current_ticker after use
            if 'current_ticker' in st.session_state:
                del st.session_state.current_ticker
    
    elif page == "Compare Stocks":
        st.title("Compare Stocks")
        
        tickers_input = st.text_input(
            "Enter ticker symbols separated by commas (e.g., AAPL,MSFT,GOOGL)",
            key="compare_tickers"
        )
        
        if st.button("Compare") and tickers_input.strip():
            tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
            if tickers:
                compare_stocks(tickers)
            else:
                st.warning("Please enter valid ticker symbols")
    
    elif page == "Market Overview":
        st.title("Market Overview")
        
        # Add a refresh button
        if st.button("Refresh"):
            st.session_state.last_market_update = None
            st.rerun()
        
        display_market_overview()
    
    elif page == "Search":
        st.title("Search Stocks")
        
        query = st.text_input("Search by company name or ticker", key="search_query")
        
        if st.button("Search") and query.strip():
            search_stocks(query)
    
    elif page == "History":
        st.title("Search History")
        
        if not st.session_state.history:
            st.info("No search history yet")
        else:
            # Sort history by timestamp (newest first)
            sorted_history = sorted(
                st.session_state.history,
                key=lambda x: x.get('timestamp', 0),
                reverse=True
            )
            
            for i, item in enumerate(sorted_history):
                ticker = item.get('ticker', 'Unknown')
                timestamp = item.get('timestamp', time.time())
                formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
                
                with st.expander(
                    f"{ticker} - {formatted_time}",
                    expanded=(i == 0)  # Expand the most recent item
                ):
                    if st.button("View Details", key=f"history_{i}"):
                        st.session_state.current_ticker = ticker
                        st.rerun()
                    
                    stock_info = item.get('stock_info', {})
                    if stock_info and 'error' not in stock_info:
                        name = stock_info.get('name', ticker)
                        symbol = stock_info.get('symbol', ticker)
                        price = safe_format_number(stock_info.get('current_price'))
                        currency = stock_info.get('currency', 'USD')
                        sector = stock_info.get('sector', 'N/A')
                        
                        st.write(f"**{name}** ({symbol})")
                        st.write(f"Price: {price} {currency}")
                        st.write(f"Sector: {sector}")
                    else:
                        st.write(f"**{ticker}**")
                        st.write("Stock information not available")

if __name__ == "__main__":
    main()
