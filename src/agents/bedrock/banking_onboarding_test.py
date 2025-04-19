import uuid
import asyncio
from typing import Optional, List, Dict, Any
import json
import sys
from multi_agent_orchestrator.orchestrator import MultiAgentOrchestrator, OrchestratorConfig
from multi_agent_orchestrator.agents import BedrockLLMAgent,BedrockLLMAgentOptions, AgentResponse, AgentCallbacks
from multi_agent_orchestrator.agents import ChainAgent, ChainAgentOptions
from multi_agent_orchestrator.types import ConversationMessage, ParticipantRole

# orchestrator = MultiAgentOrchestrator(options=OrchestratorConfig(
#   LOG_AGENT_CHAT=True,
#   LOG_CLASSIFIER_CHAT=True,
#   LOG_CLASSIFIER_RAW_OUTPUT=True,
#   LOG_CLASSIFIER_OUTPUT=True,
#   LOG_EXECUTION_TIMES=True,
#   MAX_RETRIES=3,
#   USE_DEFAULT_AGENT_IF_NONE_IDENTIFIED=True,
#   MAX_MESSAGE_PAIRS_PER_AGENT=10
# ))

from multi_agent_orchestrator.orchestrator import MultiAgentOrchestrator
from multi_agent_orchestrator.classifiers import BedrockClassifier, BedrockClassifierOptions

temporary_model_until_fixed='us.anthropic.claude-3-5-sonnet-20241022-v2:0'
custom_bedrock_classifier = BedrockClassifier(BedrockClassifierOptions(
    model_id=temporary_model_until_fixed,
    inference_config={
        'maxTokens': 500,
        'temperature': 0.7,
        'topP': 0.9
    }
))


orchestrator = MultiAgentOrchestrator()

#orchestrator = MultiAgentOrchestrator(classifier=custom_bedrock_classifier)

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
                    "Ask until you have all customer information. Once you have the information please reply TERMINATE",
        model_id=model,
        streaming=False
    ))

def create_assesment_agent(model:str):
    return BedrockLLMAgent(BedrockLLMAgentOptions(
        name="Relationship Agent",
        description="You are a banking onboarding agent and you need to get the required information from a customer that wants to open an account"
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
model='amazon.nova-pro-v1:0'
regulator_agent=create_regulator_agent(model=model)
relationship_agent=create_relationship_agent(model=model)
assesment_agent=create_assesment_agent(model=model)

onboarding_agent = ChainAgent(ChainAgentOptions(
    name='BasicChainAgent',
    description='A simple chain of multiple agents',
    agents=[kb_agent, assesment_agent]
))

orchestrator.add_agent(onboarding_agent)

async def handle_request(_orchestrator: MultiAgentOrchestrator, _user_input: str, _user_id: str, _session_id: str):
    response: AgentResponse = await _orchestrator.route_request(_user_input, _user_id, _session_id)
    # Print metadata
    print("\nMetadata:")
    print(f"Selected Agent: {response.metadata.agent_name}")
    if response.streaming:
        print('Response:', response.output.content[0]['text'])
    else:
        print('Response:', response.output.content[0]['text'])

if __name__ == "__main__":
    USER_ID = "user123"
    SESSION_ID = str(uuid.uuid4())
    print("Welcome to the interactive Multi-Agent system. Type 'quit' to exit.")
    while True:
        # Get user input
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'quit':
            print("Exiting the program. Goodbye!")
            sys.exit()
        # Run the async function
        asyncio.run(handle_request(orchestrator, user_input, USER_ID, SESSION_ID))

