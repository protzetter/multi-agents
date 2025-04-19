import asyncio
import sys
import os
from dotenv import load_dotenv
import uuid
load_dotenv()

key= os.getenv('ANTHROPIC_API_KEY')
AWS_DEFAULT_REGION='us-east-1'

from multi_agent_orchestrator.classifiers import AnthropicClassifier, AnthropicClassifierOptions
from multi_agent_orchestrator.orchestrator import MultiAgentOrchestrator

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

orchestrator = MultiAgentOrchestrator(classifier=custom_anthropic_classifier)

from multi_agent_orchestrator.agents import AnthropicAgent, AnthropicAgentOptions

Cathy = AnthropicAgent(AnthropicAgentOptions(
    name="Cathy",
    description="Your name is Cathy and you are a stand-up comedian.",
    model_id="claude-3-haiku-20240307",
    streaming=False,
    api_key=key
))

Cathy.set_system_prompt("Your name is Cathy and you are a stand-up comedian. "
    "Start the next joke from the punchline of the previous joke.")
Joe = AnthropicAgent(AnthropicAgentOptions(
    name="Joe",
    description="Your name is Joe and you are a stand-up comedian.",
    model_id="claude-3-haiku-20240307",
    streaming=False,
    api_key=key
))
Joe.set_system_prompt("Start the next joke from the punchline of the previous joke.")

from multi_agent_orchestrator.orchestrator import MultiAgentOrchestrator
from multi_agent_orchestrator.classifiers import AnthropicClassifier, AnthropicClassifierOptions

async def handle_request(_orchestrator: MultiAgentOrchestrator, _user_input: str, _user_id: str, _session_id: str):
    response: AgentResponse = await _orchestrator.route_request(_user_input, _user_id, _session_id)
    print("\nMetadata:")
    print(f"Selected Agent: {response.metadata.agent_name}")
    if response.streaming:
        print('Response:', response.output.content[0]['text'])
    else:
        print('Response:', response.output.content[0]['text'])


if __name__ == "__main__":

    anthropic_classifier = AnthropicClassifier(AnthropicClassifierOptions(
        api_key=key
    ))
    orchestrator = MultiAgentOrchestrator(classifier=anthropic_classifier)

    orchestrator.add_agent(Joe)
    orchestrator.add_agent(Cathy)

    print(orchestrator.get_all_agents())

    orchestrator.set_default_agent('Joe')

    USER_ID = "user123"
    SESSION_ID = str(uuid.uuid4())
    print("Welcome to the interactive Multi-Agent system. Type 'quit' to exit.")
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'quit':
            print("Exiting the program. Goodbye!")
            sys.exit()
        asyncio.run(handle_request(orchestrator, user_input, USER_ID, SESSION_ID))
    