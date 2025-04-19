import asyncio
import sys
import os
import uuid
from dotenv import load_dotenv
import logging
import PyPDF2
import io
from chainlit.input_widget import Select, Switch
import chainlit as cl

# Add the project root to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from typing import List
import chainlit as cl

# Load environment variables from the config directory
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../config/.env'))

key = os.getenv('ANTHROPIC_API_KEY')
if not key:
    logger.error("ANTHROPIC_API_KEY not found in environment variables")
    raise ValueError("ANTHROPIC_API_KEY is not set")


from multi_agent_orchestrator.classifiers import AnthropicClassifier, AnthropicClassifierOptions
from multi_agent_orchestrator.orchestrator import MultiAgentOrchestrator
from multi_agent_orchestrator.agents import AnthropicAgent, AnthropicAgentOptions, AgentResponse

from typing import List, Tuple, Optional, Collection
from multi_agent_orchestrator.types import ConversationMessage


# Import ChromaDB retriever from the new location
from src.utils.db.chroma_retriever import ChromaDBRetriever, ChromaDBRetrieverOptions
options = ChromaDBRetrieverOptions(
        persist_directory= './chromadb',
        collection_name='ubs-research',
        n_results= 5,
        similarity_threshold= 0.3
)

def create_relationship_agent(model:str,key:str):
    return AnthropicAgent(AnthropicAgentOptions(
        name="Relationship Agent",
        description="""You are a banking onboarding agent and you need to get the required information from a customer that wants to open an account.
You need to get first name, last name, address, birth date, nationality, residence permit.
Once you have all the information required you need to ask the regulator agent to review the information for completeness.
Ask until you have all customer information. Once you have the information please reply TERMINATE""",
        model_id=model,
        streaming=False,
        api_key=key
    ))


def create_regulator_agent(model:str, key:str):
    return AnthropicAgent(AnthropicAgentOptions(
        name="Regulator Agent",
        description="You are a banking regulator agent and you need to ensure that the relationship agent has gathered all required information from the customer"
                    "Check the context and make sure you have the required information. Once you are sure you have the infomation needed you can proceed to next steps",
        model_id=model,
        streaming=False,
        api_key=key
    ))


def create_investment_agent(model:str, key:str):
    return AnthropicAgent(AnthropicAgentOptions(
        name="Investment research agent",
        description="My investment reserach  agent is responsible for giving information about investment research, providing latest research on equities, bonds and other investment assets."
                    "Answer the question based only on the context provided.",
        streaming=False,
        model_id=model,
        api_key=key,
        retriever=ChromaDBRetriever(options)
    ))

async def handle_request(_orchestrator: MultiAgentOrchestrator, _user_input: str, _user_id: str, _session_id: str, chat_history: List[ConversationMessage]):
    try:
        print(chat_history)
        response: AgentResponse = await _orchestrator.route_request(_user_input, _user_id, _session_id,chat_history)
        return response
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

#Initialize the classifier
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

from multi_agent_orchestrator.storage import InMemoryChatStorage


#memory_storage = InMemoryChatStorage()
#Initialize the orchestrator
orchestrator = MultiAgentOrchestrator(classifier=custom_anthropic_classifier) #, storage=memory_storage)

from multi_agent_orchestrator.agents import ChainAgent, ChainAgentOptions
# create the chain agent
rel_agent = create_relationship_agent("claude-3-5-sonnet-latest", key)
reg_agent = create_regulator_agent("claude-3-5-sonnet-latest", key)
investment_agent= create_investment_agent("claude-3-5-sonnet-latest", key)

#Add agents to the orchestrator
orchestrator.add_agent(rel_agent)
orchestrator.add_agent(investment_agent)

orchestrator.set_default_agent("Relationship Agent")


import chainlit as cl

@cl.on_chat_start
async def main():
    print("A new chat session has started!")
    cl.user_session.set("user_id", str(uuid.uuid4()))
    cl.user_session.set("session_id", str(uuid.uuid4()))
    cl.user_session.set("chat_history", [])

    await cl.Message(
            content="Welcome to the interactive Multi-Agent system. Type 'quit' to exit.",
        ).send()

@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...
    user_id = cl.user_session.get("user_id")
    session_id = cl.user_session.get("session_id")
    chat_history = cl.user_session.get("chat_history")
    user_input=message.content
    if user_input.lower() == 'quit':
            print("Exiting the program. Goodbye!")
            sys.exit()
 #   chat_history.append({"role": "user", "content": user_input})
 #   chat_history.append({"role": "assistant", "content": response.output})
#    chat_history.append(response.output)
#    cl.user_session.set("chat_history", chat_history)
    #check if response includes the word TERMINATE
    if 'TERMINATE' in response.output.content[0]['text']:
        print('terminating')
        response = await reg_agent.process_request(user_input, user_id, session_id, chat_history)
        print(response.content)
        await cl.Message(
            content=response.content[0]['text'],
        ).send()
    else:
        await cl.Message(
            content=response.output.content[0]['text'],
        ).send()



    



