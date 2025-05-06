"""
Example of using the banking onboarding API agent.
"""
import os
import sys
import asyncio
import uuid
from dotenv import load_dotenv

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

# Import necessary components
from multi_agent_orchestrator.orchestrator import MultiAgentOrchestrator
from multi_agent_orchestrator.classifiers import BedrockClassifier, BedrockClassifierOptions
from src.agents.bedrock.banking_onboarding_api import create_relationship_agent, create_regulator_agent

async def main():
    """Run the banking onboarding API example."""
    # Initialize user session
    user_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    chat_history = []
    
    # Set up the model
    model = 'amazon.nova-lite-v1:0'
    
    # Create a classifier for the orchestrator
    classifier = BedrockClassifierOptions(
        model_id=model,
        inference_config={
            'maxTokens': 500,
            'temperature': 0.7,
            'topP': 0.9
        }
    )
    
    # Create the orchestrator
    orchestrator = MultiAgentOrchestrator(classifier=BedrockClassifier(classifier))
    
    # Create agents
    relationship_agent = create_relationship_agent(model=model)
    regulator_agent = create_regulator_agent(model=model)
    
    # Add agents to orchestrator
    orchestrator.add_agent(relationship_agent)
    orchestrator.set_default_agent("Relationship Agent")
    
    print("Starting banking onboarding conversation...")
    print("Type 'quit' to exit.")
    
    # Start with an initial message
    initial_message = "I'd like to open a new bank account"
    print(f"\nYou: {initial_message}")
    
    # Process the initial request
    response = await orchestrator.route_request(initial_message, user_id, session_id, chat_history)
    
    # Print the response
    print(f"\nAgent ({response.metadata.agent_name}): {response.output.content[0]['text']}")
    
    # Add response to chat history
    chat_history.append(response.output)
    
    # Continue the conversation until complete
    while "TERMINATE" not in response.output.content[0]['text']:
        # Get next user input
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            print("Exiting the program. Goodbye!")
            break
        
        # Get next response
        response = await orchestrator.route_request(user_input, user_id, session_id, chat_history)
        print(f"\nAgent ({response.metadata.agent_name}): {response.output.content[0]['text']}")
        
        # Add response to chat history
        chat_history.append(response.output)
    
    # Once complete, have the regulator agent review the information
    if "TERMINATE" in response.output.content[0]['text']:
        print("\nSwitching to Regulator Agent for review...")
        regulator_response = await regulator_agent.process_request(
            "Please review the customer information", 
            user_id, 
            session_id, 
            chat_history
        )
        print(f"\nRegulator Agent: {regulator_response.content[0]['text']}")

if __name__ == "__main__":
    asyncio.run(main())
