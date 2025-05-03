"""
Streamlit application for the Stock Information Agent.

This module provides a web interface for interacting with the StockInfoAgent
using Streamlit.
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

# Import the Stock Information Agent
from src.agents.bedrock.stock_info_agent import StockInfoAgent
from src.utils.finance.yahoo_finance import yahoo_finance

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../config/.env'))

# Initialize session state variables if they don't exist
def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'agent' not in st.session_state:
        # Get AWS region from environment variables or use default
        aws_region = os.environ.get('AWS_REGION', 'us-east-1')
        
        # Get model ID from environment variables or use default
        model_id = os.environ.get('BEDROCK_MODEL_ID', 'amazon.nova-pro-v1:0')
        
        # Initialize the Stock Information Agent
        try:
            st.session_state.agent = StockInfoAgent(model_id=model_id, region=aws_region)
            st.session_state.model_id = model_id
            st.session_state.region = aws_region
        except Exception as e:
            st.error(f"Error initializing Stock Information Agent: {str(e)}")
            st.session_state.agent = None
    
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    if 'market_overview' not in st.session_state:
        st.session_state.market_overview = None
    
    if 'last_market_update' not in st.session_state:
        st.session_state.last_market_update = None

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

def display_historical_data(historical_data: Dict[str, Any]):
    """Display historical stock data."""
    if 'error' in historical_data:
        st.error(f"Error retrieving historical data: {historical_data['error']}")
        return
    
    if 'stats' in historical_data and 'error' not in historical_data['stats']:
        stats = historical_data['stats']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            change_color = "green" if stats['change'] > 0 else "red"
            st.markdown(f"**Change:** <span style='color:{change_color}'>{stats['change']} ({stats['percent_change']}%)</span>", unsafe_allow_html=True)
        
        with col2:
            st.write(f"**Highest:** {stats['highest']['price']} on {stats['highest']['date']}")
        
        with col3:
            st.write(f"**Lowest:** {stats['lowest']['price']} on {stats['lowest']['date']}")
        
        # Create a simple chart of closing prices
        if 'data' in historical_data and historical_data['data']:
            chart_data = {
                'Date': [record['date'] for record in historical_data['data']],
                'Close': [record['close'] for record in historical_data['data']]
            }
            
            st.line_chart(chart_data, x='Date', y='Close')
    else:
        st.warning("No historical data statistics available")

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
                st.session_state.market_overview = st.session_state.agent.get_market_overview()
                st.session_state.last_market_update = current_time
            except Exception as e:
                st.error(f"Error fetching market overview: {str(e)}")
                return
    
    overview = st.session_state.market_overview
    
    if 'error' in overview:
        st.error(f"Error: {overview['error']}")
        return
    
    # Display major indices
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
    
    # Display market analysis
    if 'analysis' in overview:
        st.subheader("Market Analysis")
        st.write(overview['analysis'])
    
    # Display last update time
    if st.session_state.last_market_update:
        st.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.session_state.last_market_update))}")

def compare_stocks(tickers: List[str]):
    """Compare multiple stocks."""
    if not tickers:
        st.warning("Please enter at least one ticker symbol")
        return
    
    with st.spinner(f"Comparing stocks: {', '.join(tickers)}..."):
        try:
            comparison = st.session_state.agent.compare_stocks(tickers)
        except Exception as e:
            st.error(f"Error comparing stocks: {str(e)}")
            return
    
    if 'error' in comparison:
        st.error(f"Error: {comparison['error']}")
        return
    
    # Display comparison data
    st.subheader("Stock Comparison")
    
    # Create a table of key metrics
    if 'stock_infos' in comparison and 'quotes' in comparison:
        stock_infos = comparison['stock_infos']
        quotes = comparison['quotes']
        
        # Prepare data for the table
        table_data = []
        for ticker in tickers:
            info = stock_infos.get(ticker, {})
            quote = quotes.get(ticker, {})
            
            row = {
                'Ticker': ticker,
                'Name': info.get('name', 'N/A'),
                'Price': quote.get('price', 'N/A'),
                'Change': f"{quote.get('change', 'N/A')} ({quote.get('change_percent_formatted', 'N/A')})",
                'Market Cap': info.get('market_cap_formatted', info.get('market_cap', 'N/A')),
                'P/E Ratio': info.get('pe_ratio', 'N/A'),
                'Sector': info.get('sector', 'N/A'),
                'Industry': info.get('industry', 'N/A')
            }
            table_data.append(row)
        
        # Display the table
        st.dataframe(table_data)
    
    # Display the analysis
    if 'analysis' in comparison:
        st.subheader("Comparison Analysis")
        st.write(comparison['analysis'])

def get_stock_summary(ticker: str):
    """Get and display a comprehensive summary of a stock."""
    if not ticker:
        st.warning("Please enter a ticker symbol")
        return
    
    with st.spinner(f"Fetching information for {ticker}..."):
        try:
            summary = st.session_state.agent.get_stock_summary(ticker)
        except Exception as e:
            st.error(f"Error fetching stock summary: {str(e)}")
            return
    
    if 'error' in summary:
        st.error(f"Error: {summary['error']}")
        return
    
    # Add to history
    st.session_state.history.append({
        'ticker': ticker,
        'summary': summary,
        'timestamp': time.time()
    })
    
    # Display stock information
    if 'stock_info' in summary:
        stock_info = summary['stock_info']
        st.header(f"{stock_info.get('name', ticker)} ({stock_info.get('symbol', ticker)})")
        
        display_stock_info(stock_info)
    
    # Display AI-generated summary
    if 'natural_language_summary' in summary:
        st.subheader("AI Analysis")
        st.write(summary['natural_language_summary'])
    
    # Display tabs for historical data and news
    tab1, tab2 = st.tabs(["Historical Performance", "Recent News"])
    
    with tab1:
        if 'historical_data' in summary:
            display_historical_data(summary['historical_data'])
    
    with tab2:
        if 'news' in summary:
            display_news(summary['news'])

def search_stocks(query: str):
    """Search for stocks by name or ticker."""
    if not query:
        st.warning("Please enter a search query")
        return
    
    with st.spinner(f"Searching for '{query}'..."):
        try:
            results = yahoo_finance.search_stocks(query)
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

def main():
    """Main function to run the Streamlit app."""
    # Set page config
    st.set_page_config(
        page_title="Stock Information Agent",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("Stock Information Agent")
        st.write(f"Using model: {st.session_state.model_id}")
        
        # Model selection
        new_model = st.selectbox(
            "Select Bedrock Model",
            options=[
                "amazon.nova-pro-v1:0",
                "anthropic.claude-v2:1",
                "anthropic.claude-3-sonnet-20240229-v1:0",
                "anthropic.claude-3-haiku-20240307-v1:0"
            ],
            index=0
        )
        
        if new_model != st.session_state.model_id:
            if st.button("Change Model"):
                with st.spinner("Initializing agent with new model..."):
                    try:
                        st.session_state.agent = StockInfoAgent(model_id=new_model, region=st.session_state.region)
                        st.session_state.model_id = new_model
                        st.success(f"Model changed to {new_model}")
                    except Exception as e:
                        st.error(f"Error changing model: {str(e)}")
        
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
                        st.experimental_rerun()
                    
                    if 'stock_info' in item['summary']:
                        stock_info = item['summary']['stock_info']
                        st.write(f"**{stock_info.get('name', item['ticker'])}** ({stock_info.get('symbol', item['ticker'])})")
                        st.write(f"Price: {stock_info.get('current_price', 'N/A')} {stock_info.get('currency', 'USD')}")
                        st.write(f"Sector: {stock_info.get('sector', 'N/A')}")

if __name__ == "__main__":
    main()
