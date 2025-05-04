"""
Streamlit application for the Stock SimpleAgent.

This module provides a web interface for interacting with the StockSimpleAgent
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

# Import the Stock SimpleAgent
from src.agents.simpleagents.stock_agent import StockSimpleAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../config/.env'))

# Initialize session state variables if they don't exist
def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'agent' not in st.session_state:
        # Default model configuration
        model_provider = "bedrock"
        model_name = "amazon.nova-pro-v1:0"
        
        # Initialize the Stock SimpleAgent
        try:
            st.session_state.agent = StockSimpleAgent(
                model_provider=model_provider,
                model_name=model_name
            )
            st.session_state.model_provider = model_provider
            st.session_state.model_name = model_name
        except Exception as e:
            st.error(f"Error initializing Stock SimpleAgent: {str(e)}")
            st.session_state.agent = None
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'processing' not in st.session_state:
        st.session_state.processing = False

def display_chat_message(message, is_user=False):
    """Display a chat message in the Streamlit UI."""
    if is_user:
        st.chat_message("user").write(message)
    else:
        st.chat_message("assistant").write(message)

def process_user_message(user_message):
    """Process a user message and update the chat."""
    if not user_message:
        return
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    # Set processing flag
    st.session_state.processing = True
    
    try:
        # Process the message with the agent
        with st.spinner("Thinking..."):
            response = st.session_state.agent.process_message(user_message)
        
        # Add agent response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    except Exception as e:
        # Handle errors
        error_message = f"Error: {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": error_message})
    
    # Clear processing flag
    st.session_state.processing = False

def main():
    """Main function to run the Streamlit app."""
    # Set page config
    st.set_page_config(
        page_title="Stock SimpleAgent",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("Stock SimpleAgent")
        st.write("A lightweight agent for stock information")
        
        # Model configuration
        st.subheader("Model Configuration")
        
        model_provider = st.selectbox(
            "Model Provider",
            options=["openai", "anthropic", "bedrock", "huggingface", "local"],
            index=0
        )
        
        # Model name options based on provider
        if model_provider == "openai":
            model_options = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        elif model_provider == "anthropic":
            model_options = ["claude-2", "claude-instant-1", "claude-3-sonnet-20240229-v1:0"]
        elif model_provider == "bedrock":
            model_options = ["anthropic.claude-v2:1", "amazon.nova-pro-v1:0", "anthropic.claude-3-sonnet-20240229-v1:0"]
        elif model_provider == "huggingface":
            model_options = ["mistralai/Mistral-7B-Instruct-v0.1", "meta-llama/Llama-2-7b-chat-hf"]
        else:  # local
            model_options = ["llama-2-7b-chat.gguf", "mistral-7b-instruct-v0.1.Q4_K_M.gguf"]
        
        model_name = st.selectbox(
            "Model Name",
            options=model_options,
            index=0
        )
        
        # Apply button
        if st.button("Apply Configuration"):
            if model_provider != st.session_state.model_provider or model_name != st.session_state.model_name:
                with st.spinner("Initializing agent with new model..."):
                    try:
                        st.session_state.agent = StockSimpleAgent(
                            model_provider=model_provider,
                            model_name=model_name
                        )
                        st.session_state.model_provider = model_provider
                        st.session_state.model_name = model_name
                        st.success(f"Model changed to {model_provider}/{model_name}")
                    except Exception as e:
                        st.error(f"Error changing model: {str(e)}")
        
        st.divider()
        
        # Quick actions
        st.subheader("Quick Actions")
        
        if st.button("Get Market Summary"):
            process_user_message("Give me a summary of the current market conditions")
        
        ticker = st.text_input("Stock Ticker")
        if ticker and st.button("Get Stock Info"):
            process_user_message(f"Tell me about {ticker} stock")
        
        tickers = st.text_input("Compare Stocks (comma-separated)")
        if tickers and st.button("Compare"):
            process_user_message(f"Compare these stocks: {tickers}")
        
        st.divider()
        
        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.agent.reset()
            st.success("Chat cleared")
    
    # Main content
    st.title("Stock SimpleAgent Chat")
    
    # Display current model
    st.caption(f"Using model: {st.session_state.model_provider}/{st.session_state.model_name}")
    
    # Display chat messages
    for message in st.session_state.messages:
        display_chat_message(message["content"], message["role"] == "user")
    
    # Chat input
    if st.session_state.processing:
        st.text_input("Your message", "", disabled=True)
    else:
        user_message = st.chat_input("Ask about stocks or the market...")
        if user_message:
            process_user_message(user_message)
            st.experimental_rerun()

if __name__ == "__main__":
    main()
