from multi_agent_orchestrator.orchestrator import MultiAgentOrchestrator
from multi_agent_orchestrator.agents import BedrockLLMAgent,BedrockLLMAgentOptions, AgentResponse, AgentCallbacks
from multi_agent_orchestrator.agents import ChainAgent, ChainAgentOptions
from multi_agent_orchestrator.types import ConversationMessage, ParticipantRole
from typing import Optional, List, Dict, Any
import uuid
import asyncio
import chainlit as cl
import sys

# temporary_model_until_fixed='us.anthropic.claude-3-5-sonnet-20241022-v2:0'
# custom_bedrock_classifier = BedrockClassifier(BedrockClassifierOptions(
#     model_id=temporary_model_until_fixed,
#     inference_config={
#         'maxTokens': 500,
#         'temperature': 0.7,
#         'topP': 0.9
#     }
# ))

import os
from dotenv import load_dotenv
load_dotenv()

key= os.getenv('ANTHROPIC_API_KEY')

# Create an orchestrator instance
from multi_agent_orchestrator.classifiers import BedrockClassifier, BedrockClassifierOptions

# Initialize the classifier
classifier = BedrockClassifierOptions(
    model_id='amazon.nova-lite-v1:0',
    inference_config={
        'maxTokens': 500,
        'temperature': 0.7,
        'topP': 0.9
    }
)

# Create the orchestrator
orchestrator = MultiAgentOrchestrator(classifier=BedrockClassifier(classifier))

class BedrockLLMAgentCallbacks(AgentCallbacks):
    def on_llm_new_token(self, token: str) -> None:
        # handle response streaming here
        print(token, end='', flush=True)



from multi_agent_orchestrator.agents import BedrockLLMAgent, BedrockLLMAgentOptions
from multi_agent_orchestrator.retrievers import AmazonKnowledgeBasesRetriever, AmazonKnowledgeBasesRetrieverOptions


def create_relationship_agent(model:str):
    return BedrockLLMAgent(BedrockLLMAgentOptions(
        name="Relationship Agent",
        description="You are a banking onboarding agent and you need to get the required information from a customer that wants to open an account"
                    " You need to get his first name, hist last name, his address, his birth date, his nationality, his residence permit."
                    "Once you have all the information required you need to ask the regulator agent to review the information for completeness"
                    "Ask until you have all customer information. Please confirm with the customer that the information is complete and accurate"
                    "Once you have the information please reply TERMINATE",
        model_id=model,
        streaming=False
    ))

def create_assesment_agent(model:str):
    return BedrockLLMAgent(BedrockLLMAgentOptions(
        name="Relationship Agent",
        description="You are a banking onboarding agent and you need to get the required information from a customer that wants to open an account"
                    "You are receiving questions that you need to ask. Do not say thank you, but use the quesions to ask the customer information"
                    "Ask until you have all customer information. Once you have the information please reply TERMINATE",
        model_id=model,
        streaming=False
    ))



def create_regulator_agent(model:str):
    return BedrockLLMAgent(BedrockLLMAgentOptions(
        name="Regulator Agent",
        description="You are a banking regulator agent and you need to ensure that the relationship agent has gathered all required information from the customer"
                    "Check the context and make sure you have the required information. Once you are sure you have the infomation needed you can proceed to next steps",
        model_id=model,
        streaming=False
    ))




def create_kb_agent():
    return BedrockLLMAgent(BedrockLLMAgentOptions(
        name="My personal agent",
        description="My personal agent is responsible for giving information about banking customer complicane, onboarding, risk assessment and any question related to financial services."
                    "Answer the question based only on the context provided.",
        streaming=True,
        model_id="amazon.nova-micro-v1:0",
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

kb_agent= create_kb_agent()
model='amazon.nova-lite-v1:0'
regulator_agent=create_regulator_agent(model=model)
relationship_agent=create_relationship_agent(model=model)
assesment_agent=create_assesment_agent(model=model)

onboarding_agent = ChainAgent(ChainAgentOptions(
    name='BasicChainAgent',
    description='A simple chain of multiple agents',
    agents=[kb_agent, assesment_agent]
))

orchestrator.add_agent(onboarding_agent)



async def handle_request(_orchestrator: MultiAgentOrchestrator, _user_input: str, _user_id: str, _session_id: str, chat_history: List[ConversationMessage]):
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
 #   chat_history.append({"role": "user", "content": user_input})
 #   chat_history.append({"role": "assistant", "content": response.output})
    chat_history.append(response.output)
    cl.user_session.set("chat_history", chat_history)
    #check if response includes the word TERMINATE
    if 'TERMINATE' in response.output.content[0]['text']:
        print("TERMINATE")
        response = asyncio.run(regulator_agent.process_request(user_input, user_id, session_id, chat_history))
        print(response.output.content[0]['text'])
        await cl.Message(
            content=response.content[0]['text'],
        ).send()
    else:
        await cl.Message(
            content=response.output.content[0]['text'],
        ).send()
