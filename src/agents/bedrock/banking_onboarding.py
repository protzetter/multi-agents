
from agent_squad.orchestrator import AgentSquad
from agent_squad.agents import BedrockLLMAgent,BedrockLLMAgentOptions, AgentResponse, AgentCallbacks
from agent_squad.agents import ChainAgent, ChainAgentOptions
from agent_squad.types import ConversationMessage
from typing import List
import uuid
import asyncio
import os
import chainlit as cl
from agent_squad.classifiers import BedrockClassifier, BedrockClassifierOptions

from dotenv import load_dotenv
# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../config/.env'))

model= os.getenv('BEDROCK_MODEL')
print(model)
reg=os.getenv('AWS_REGION')
custom_bedrock_classifier = BedrockClassifier(BedrockClassifierOptions(
    model_id=model,
    region=reg,
    inference_config={
        'maxTokens': 500,
        'temperature': 0.7,
        'topP': 0.9
    }
))

orchestrator = AgentSquad(classifier=custom_bedrock_classifier)


class BedrockLLMAgentCallbacks(AgentCallbacks):
    def on_llm_new_token(self, token: str) -> None:
        # handle response streaming here
        print(token, end='', flush=True)



from agent_squad.agents import BedrockLLMAgent, BedrockLLMAgentOptions
from agent_squad.retrievers import AmazonKnowledgeBasesRetriever, AmazonKnowledgeBasesRetrieverOptions


def create_relationship_agent(model:str,region:str):
    return BedrockLLMAgent(BedrockLLMAgentOptions(
        name="Relationship Agent",
        description="You are a banking onboarding agent and you need to get the required information from a customer that wants to open an account"
                    " You need to get his first name, hist last name, his address, his birth date, his nationality, his residence permit."
                    "Once you have all the information required you need to ask the regulator agent to review the information for completeness"
                    "Ask until you have all customer information. Once you have the information please reply TERMINATE",
        model_id=model,
        region=region,
        streaming=False
    ))

def create_assesment_agent(model:str,region:str):
    return BedrockLLMAgent(BedrockLLMAgentOptions(
        name="Relationship Agent",
        description="You are a banking onboarding agent and you need to get the required information from a customer that wants to open an account"
                    "You are receiving questions that you need to ask. Do not say thank you, but use the quesions to ask the customer information"
                    "Ask until you have all customer information. Once you have the information please reply TERMINATE",
        model_id=model,
        region=region,
        streaming=False
    ))



def create_regulator_agent(model:str, region:str):
    return BedrockLLMAgent(BedrockLLMAgentOptions(
        name="Regulator Agent",
        region=region,
        description="You are a banking regulator agent and you need to ensure that the relationship agent has gathered all required information from the customer"
                    "Check the context and make sure you have the required information. Once you are sure you have the infomation needed you can proceed to next steps",
        model_id=model,
        streaming=False
    ))




def create_kb_agent(model:str,region:str):
    return BedrockLLMAgent(BedrockLLMAgentOptions(
        name="My personal agent",
        description="My personal agent is responsible for giving information about banking customer complicane, onboarding, risk assessment and any question related to financial services."
                    "Answer the question based only on the context provided.",
        streaming=True,
        model_id=model,
        region=region,
        inference_config={
            "temperature": 0.1,
        },
        retriever=AmazonKnowledgeBasesRetriever(AmazonKnowledgeBasesRetrieverOptions(
            knowledge_base_id="R15U9U9KHU",
            retrievalConfiguration={
                "vectorSearchConfiguration": {
                    "numberOfResults": 5,
                    "overrideSearchType": "HYBRID",
                },
            },
        ))
    ))

import os
from dotenv import load_dotenv
# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../config/.env'))

# Get model and region from environment variables with default values
model = os.getenv('BEDROCK_MODEL', 'amazon.nova-lite-v1:0')
region = os.getenv('AWS_REGION', 'us-east-1')

# Update agent creation with model and region
# kb_agent = create_kb_agent(model=model, region=region)
regulator_agent = create_regulator_agent(model=model, region=region) 
relationship_agent=create_relationship_agent(model=model, region=region)

#Add agents to the orchestrator
orchestrator.add_agent(regulator_agent)
orchestrator.add_agent(relationship_agent)

orchestrator.set_default_agent("Relationship Agent")


async def handle_request(_orchestrator: AgentSquad, _user_input: str, _user_id: str, _session_id: str, chat_history: List[ConversationMessage]):
    response: AgentResponse = await _orchestrator.route_request(_user_input, _user_id, _session_id,chat_history)
    print("\nMetadata:")
    print(f"Selected Agent: {response.metadata.agent_name}")
    if response.streaming:
        print('Response:', response.output.content[0]['text'])
    else:
        print('Response:', response.output.content[0]['text'])
    return response




import chainlit as cl

@cl.on_chat_start
async def main():
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
    response= asyncio.run(handle_request(orchestrator, user_input, user_id, session_id, chat_history))
    chat_history.append(response.output)
    cl.user_session.set("chat_history", chat_history)
    #check if response includes the word TERMINATE
    if 'TERMINATE' in response.output.content[0]['text']:
        response = asyncio.run(regulator_agent.process_request(user_input, user_id, session_id, chat_history))
        print(response.output.content[0]['text'])
        await cl.Message(
            content=response.content[0]['text'],
        ).send()
    else:
        await cl.Message(
            content=response.output.content[0]['text'],
        ).send()



    



