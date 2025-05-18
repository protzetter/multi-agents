import streamlit as st
import boto3
import asyncio
import uuid
from dotenv import load_dotenv
import os
import logging
import sys
from typing import List

# Add the project root to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Import document processing utilities
from src.utils.document_processing.pdf_passport_detector_refactored import is_passport_with_nova, extract_passport_info

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(os.path.join(os.path.dirname(__file__), '../../config/.env'))

key = os.getenv('ANTHROPIC_API_KEY')


def create_bedrock_agent_client():
    return boto3.client('bedrock-agent-runtime', region_name='us-east-1')

def create_bedrock_agent():
    try:
        return {
            'agent_id': 'your-agent-id',  # Replace with your Bedrock agent ID
            'agent_alias_id': 'your-agent-alias-id'  # Replace with your agent alias ID
        }
    except Exception as e:
        logger.error(f"Error creating Bedrock agent: {str(e)}")
        return None


from agent_squad.classifiers import AnthropicClassifier, AnthropicClassifierOptions
from agent_squad.orchestrator import AgentSquad
from agent_squad.agents import BedrockLLMAgent,BedrockLLMAgentOptions,AnthropicAgent, AnthropicAgentOptions, AgentResponse
from typing import List, Tuple, Optional, Collection
from agent_squad.types import ConversationMessage

# ChromaDB retriever setup
from src.utils.db.chroma_retriever import ChromaDBRetriever, ChromaDBRetrieverOptions
options = ChromaDBRetrieverOptions(
    persist_directory='/Users/patrickrotzetter/Library/CloudStorage/OneDrive-Personal/Documents/dev/multi-agents/chromadb',
    collection_name='ubs-research',
    n_results=5,
    similarity_threshold=0.3
)

def create_relationship_agent(model: str, key: str):
    try:
        return AnthropicAgent(AnthropicAgentOptions(
            name="Relationship Agent",
            description="You are a banking onboarding agent and you need to get the required information from a customer that wants to open an account"
                        " You need to get first name, last name, address, birth date, nationality, residence permit."
                        "Once you have all the information required you need to ask the regulator agent to review the information for completeness"
                        "Ask until you have all customer information. Once you have the information please reply TERMINATE",
            model_id=model,
            streaming=False,
            api_key=key
        ))
    except Exception as e:
        logger.error(f"Error creating relationship agent: {str(e)}")
        return None

# create function to create a relationship agent woth a bedrock agent
def create_relationship_agent_bedrock(model: str):
    try:
        return BedrockLLMAgent(BedrockLLMAgentOptions(
            name="Relationship Agent",
            description="You are a banking onboarding agent and you need to get the required information from a customer that wants to open an account"
                        " You need to get first name, last name, address, birth date, nationality, residence permit."
                        "Once you have all the information required you need to ask the regulator agent to review the information for completeness"
                        "Ask until you have all customer information. Once you have the information please reply TERMINATE",
            model_id=model,
            region='us-east-1',
            streaming=False
        ))
    except Exception as e:
        logger.error(f"Error creating relationship agent: {str(e)}")
        return None

def create_regulator_agent(model: str, key: str):
    try:
        return AnthropicAgent(AnthropicAgentOptions(
            name="Regulator Agent",
            description="You are a banking regulator agent and you need to ensure that the relationship agent has gathered all required information from the customer"
                        "Check the context and make sure you have the required information. Once you are sure you have the infomation needed you can proceed to next steps",
            model_id=model,
            streaming=False,
            api_key=key
        ))
    except Exception as e:
        logger.error(f"Error creating regulator agent: {str(e)}")
        return None

def create_investment_agent(model: str, key: str):
    try:
        return AnthropicAgent(AnthropicAgentOptions(
            name="Investment research agent",
            description="My investment research agent is responsible for giving information about investment research, providing latest research on equities, bonds and other investment assets."
                        "Answer the question based only on the context provided.",
            streaming=False,
            model_id=model,
            api_key=key,
            retriever=ChromaDBRetriever(options)
        ))
    except Exception as e:
        logger.error(f"Error creating investment agent: {str(e)}")
        logger.exception("Full traceback:") # import traceback
        return None

async def handle_request(_orchestrator: AgentSquad, _user_input: str, _user_id: str, _session_id: str, chat_history: List[ConversationMessage]):
    response: AgentResponse = await _orchestrator.route_request(_user_input, _user_id, _session_id, chat_history)
    return response

# Initialize the classifier
custom_anthropic_classifier = AnthropicClassifier(AnthropicClassifierOptions(
    api_key=key,
    model_id='claude-3-5-sonnet-latest',
    inference_config={
        'max_tokens': 500,
        'temperature': 0.7,
        'top_p': 0.9,
        'stop_sequences': ['']
    }
))

# initialize a custom bedrock classifier using amazon nova lite
from agent_squad.classifiers import BedrockClassifier, BedrockClassifierOptions
custom_bedrock_classifier = BedrockClassifier(BedrockClassifierOptions(
    region='us-east-1',
 #   model_id='amazon.nova-pro-v1:0',
    model_id='mistral.mistral-small-2402-v1:0',
    inference_config={
        'max_tokens': 500,
        'temperature': 0.7,
        'top_p': 0.9,
    }
))




async def handle_request(_orchestrator: AgentSquad, _user_input: str, _user_id: str, _session_id: str, chat_history: List[ConversationMessage]):
    try:
        print(chat_history)
        response: AgentResponse = await _orchestrator.route_request(_user_input, _user_id, _session_id,chat_history)
        return response
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

# Streamlit UI
st.set_page_config(page_title="Multi-Agent Banking System", layout="wide")


st.header("Multi Agent Banking System",divider="orange")

def main():
    # Initialize session state if not exists
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    # Initialize the orchestrator
    if st.session_state.get("orchestrator") is None:
        st.session_state.orchestrator = AgentSquad(classifier=custom_anthropic_classifier)
        # add agents to the orchestrator
#        st.session_state.orchestrator.add_agent(create_relationship_agent("claude-3-5-sonnet-latest", key))
        st.session_state.orchestrator.add_agent(create_relationship_agent_bedrock("amazon.nova-lite-v1:0"))
#        st.session_state.orchestrator.add_agent(create_regulator_agent("claude-3-5-sonnet-latest", key))
        st.session_state.orchestrator.add_agent(create_investment_agent(model="claude-3-5-sonnet-latest", key=key))
        st.session_state.orchestrator.set_default_agent("Relationship Agent")
    # Chat interface
    st.write("Welcome to the interactive Multi Agent system. Type your message below.")
    
    # Add a sidebar with additional options
    with st.sidebar:
        st.title("Settings")
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
        # Dropdown menu to select the type of file to upload
        # Options: csv, txt, pdf, or all file types
        # Default selection is "all" (index=3)
        st.header("File Settings", divider="orange")
        file_type = st.selectbox(
                "Select file type",
                ["csv", "txt", "pdf","all"], 
                index=3)
        st.header("File Upload", divider="orange")
        st.write("Upload a file to the system.")
        uploaded_file = st.file_uploader("Upload a file", type=['pdf'] if file_type != 'all' else None)
        #check file type
        if uploaded_file is not None:
            # Get file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()
    
            # Check file type
            if file_extension == 'pdf':
                file_type = 'pdf'
            else:
                file_type = 'unknown'                    # Read the file content
            if file_type == 'pdf':
                st.session_state.is_passport_pdf = extract_passport_info(uploaded_file)
                if(st.session_state.is_passport_pdf['is_passport'] is True):
                    with st.chat_message("assistant"):
                        st.write("The uploaded document is a passport.")
                else:
                    with st.chat_message("assistant"):
                        st.write("The uploaded document is not a passport.")
            else:
                # write error message to streamlit
                st.error("Unsupported file type. Please upload a PDF file.")

    #  Display chat messages from history on app rerun
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


    # User input
    user_input = st.chat_input("Type your message here...")

    if user_input:
    # Display user message
        with st.chat_message("user"):
            st.write(user_input)
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = asyncio.run(handle_request(
                    st.session_state.orchestrator,
                    user_input,
                    st.session_state.user_id,
                    st.session_state.session_id,
                    ''
                ))
                if 'TERMINATE' in response.output.content[0]['text']:
                    regulator_response = asyncio.run(st.session.state.orchestrator.agents['Regulator Agent'].process_request(
                        user_input,
                        st.session_state.user_id,
                        st.session_state.session_id,
                        st.session_state.chat_history
                    ))
                    st.write(regulator_response.content[0]['text'])
                    st.session_state.chat_history.append({"role": "assistant", "content": regulator_response.content[0]['text']})
                else:
                    st.write(response.output.content[0]['text'])
                    st.session_state.chat_history.append({"role": "assistant", "content": response.output.content[0]['text']})


if __name__ == "__main__":
    main()

