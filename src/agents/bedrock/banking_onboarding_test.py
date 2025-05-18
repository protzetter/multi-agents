import uuid
import asyncio

import sys
from agent_squad.orchestrator import AgentSquad
from agent_squad.agents import BedrockLLMAgent,BedrockLLMAgentOptions, AgentResponse, AgentCallbacks
from agent_squad.agents import ChainAgent, ChainAgentOptions


from agent_squad.orchestrator import AgentSquad
from agent_squad.classifiers import BedrockClassifier, BedrockClassifierOptions


from dotenv import load_dotenv
# Load environment variables
import os
# Use absolute path to load environment variables
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../config/.env')
load_dotenv(config_path)
model= os.getenv('BEDROCK_MODEL')
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

def create_assesment_agent(model:str, region:str):
    return BedrockLLMAgent(BedrockLLMAgentOptions(
        name="Relationship Agent",
        description="You are a banking onboarding agent and you need to get the required information from a customer that wants to open an account"
                    "Ask until you have all customer information. Once you have the information please reply TERMINATE",
        model_id=model,
        region=region,
        streaming=False
    ))



def create_regulator_agent(model:str,region:str):
    return BedrockLLMAgent(BedrockLLMAgentOptions(
        name="Regulator Agent",
        description="You are a banking regulator agent and you need to ensure that the relationship agent has gathered all required information from the customer"
                    "Check the context and make sure you have the required information. Once you are sure you have the infomation needed you can proceed to next steps",
        model_id=model,
        streaming=False
    ))


# only use if you have a Bedrock KB available

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


# kb_agent= create_kb_agent() #only use if you have a Bedrock KB available

regulator_agent=create_regulator_agent(model=model,region=reg)
relationship_agent=create_relationship_agent(model=model, region=reg)
assesment_agent=create_assesment_agent(model=model,region=reg)

#onboarding_agent = ChainAgent(ChainAgentOptions(
#    name='BasicChainAgent',
#    description='A simple chain of multiple agents',
#    agents=[relationship_agent, assesment_agent]
#))

#Add agents to the orchestrator
orchestrator.add_agent(relationship_agent)
orchestrator.add_agent(regulator_agent)

orchestrator.set_default_agent("Relationship Agent")

async def handle_request(_orchestrator: AgentSquad, _user_input: str, _user_id: str, _session_id: str):
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

