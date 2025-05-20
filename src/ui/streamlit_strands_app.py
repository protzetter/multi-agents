import streamlit as st
import os
import sys
from pathlib import Path

# Add the project root to the path to import our modules
sys.path.append(str(Path(__file__).parent.parent.parent))

# Add the project root to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Import our Strands agents
try:
    from src.agents.strands.banking_onboarding_agent import orchestrate_onboarding
    from src.agents.strands.document_processing_agent import document_agent
    from src.agents.strands.stock_info_agent import stock_agent
    from src.agents.strands.multi_agent_orchestrator import process_with_orchestration
    from src.agents.strands.rag_agent import rag_agent
except ImportError:
    st.error("Failed to import agent modules. Make sure all required files exist and dependencies are installed.")
    st.stop()

# Set page configuration
st.set_page_config(
    page_title="Multi-Agent System with Strands",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{os.urandom(4).hex()}"
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{os.urandom(4).hex()}"
if "current_agent" not in st.session_state:
    st.session_state.current_agent = "orchestrator"

# Sidebar for agent selection
st.sidebar.title("Multi-Agent System")
st.sidebar.image("https://github.com/user-attachments/assets/48b063e7-7d69-4880-b59f-52fd13e85d3a", use_column_width=True)

agent_options = {
    "orchestrator": "🧠 Orchestrator (Auto-route)",
    "banking": "🏦 Banking Onboarding Agent",
    "document": "📄 Document Processing Agent",
    "stock": "📈 Stock Information Agent",
    "rag": "📚 Knowledge Base Agent"
}

st.sidebar.subheader("Select Agent")
selected_agent = st.sidebar.radio("", list(agent_options.values()), index=0)

# Map the display name back to the agent key
for key, value in agent_options.items():
    if value == selected_agent:
        st.session_state.current_agent = key
        break

# Display agent information
agent_descriptions = {
    "orchestrator": "This agent automatically routes your query to the most appropriate specialized agent.",
    "banking": "Helps with banking onboarding processes, account opening, and compliance requirements.",
    "document": "Processes and validates documents like passports and bank statements.",
    "stock": "Provides stock information, analysis, and visualizations.",
    "rag": "Retrieves information from the knowledge base to answer banking and finance questions."
}

st.sidebar.markdown("---")
st.sidebar.subheader("About this Agent")
st.sidebar.info(agent_descriptions[st.session_state.current_agent])

# Main content area
st.title("Multi-Agent System with Strands")

# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        with st.chat_message("assistant", avatar=message.get("avatar", "🤖")):
            st.write(message["content"])
            if "metadata" in message and message["metadata"]:
                with st.expander("View Agent Metadata"):
                    st.json(message["metadata"])

# User input
user_input = st.chat_input("Ask something...")

if user_input:
    # Display user message
    st.chat_message("user").write(user_input)
    
    # Add to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Process with the selected agent
    with st.spinner("Thinking..."):
        try:
            if st.session_state.current_agent == "orchestrator":
                response = process_with_orchestration(user_input, st.session_state.session_id)
                agent_name = response["agent"]
                message = response["response"]
                avatar = "🧠"
            elif st.session_state.current_agent == "banking":
                response = orchestrate_onboarding(user_input, st.session_state.user_id, st.session_state.session_id, st.session_state.chat_history)
                agent_name = response["agent"]
                message = response["response"]
                avatar = "🏦"
            elif st.session_state.current_agent == "document":
                response = document_agent(user_input)
                agent_name = "Document Agent"
                message = response.message
                avatar = "📄"
            elif st.session_state.current_agent == "stock":
                response = stock_agent(user_input)
                agent_name = "Stock Agent"
                message = response.message['content'][0]['text']
                avatar = "📈"
            elif st.session_state.current_agent == "rag":
                response = rag_agent(user_input)
                agent_name = "Knowledge Base Agent"
                message = response.message
                avatar = "📚"
        except Exception as e:
            st.error(f"Error processing request: {str(e)}")
            agent_name = "Error"
            message = f"An error occurred: {str(e)}"
            avatar = "⚠️"
    
    # Display assistant response
    with st.chat_message("assistant", avatar=avatar):
        st.write(f"**{agent_name}**: {message}")
    
    # Add to chat history
    st.session_state.chat_history.append({
        "content": f"**{agent_name}**: {message}"
    })
