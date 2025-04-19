"""
Example of using the banking onboarding agent.
"""
import os
import sys
from dotenv import load_dotenv

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

# Import the agent classes
from src.agents.claude.banking_onboarding import create_relationship_agent, create_regulator_agent, create_investment_agent
from multi_agent_orchestrator.orchestrator import MultiAgentOrchestrator
from multi_agent_orchestrator.classifiers import AnthropicClassifier, AnthropicClassifierOptions

def main():
    """Run the banking onboarding example."""
    # Get API key
    key = os.getenv('ANTHROPIC_API_KEY')
    if not key:
        print("Error: ANTHROPIC_API_KEY not found in environment variables")
        return
        
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
    
    # Initialize the orchestrator
    orchestrator = MultiAgentOrchestrator(classifier=custom_anthropic_classifier)
    
    # Create and add agents
    rel_agent = create_relationship_agent("claude-3-5-sonnet-latest", key)
    reg_agent = create_regulator_agent("claude-3-5-sonnet-latest", key)
    investment_agent = create_investment_agent("claude-3-5-sonnet-latest", key)
    
    orchestrator.add_agent(rel_agent)
    orchestrator.add_agent(reg_agent)
    orchestrator.add_agent(investment_agent)
    
    orchestrator.set_default_agent("Relationship Agent")
    
    # Run a simple conversation
    user_id = "example_user"
    session_id = "example_session"
    
    print("Starting banking onboarding conversation...")
    print("Type 'quit' to exit.")
    
    chat_history = []
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            print("Exiting the program. Goodbye!")
            break
            
        # Process the request
        import asyncio
        response = asyncio.run(orchestrator.route_request(user_input, user_id, session_id, chat_history))
        
        # Print the response
        print(f"\nAgent: {response.output.content[0]['text']}")
        
        # Check if we need to switch to regulator agent
        if 'TERMINATE' in response.output.content[0]['text']:
            print("\nSwitching to Regulator Agent...")
            reg_response = asyncio.run(reg_agent.process_request(user_input, user_id, session_id, chat_history))
            print(f"\nRegulator Agent: {reg_response.content[0]['text']}")

if __name__ == "__main__":
    main()
