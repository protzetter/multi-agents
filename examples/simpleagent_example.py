"""
Example of using the SimpleAgent base class.
"""
import os
import sys
from dotenv import load_dotenv

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

# Import the SimpleAgent class
from src.agents.simpleagents.base_agent import SimpleAgent

def main():
    """Run the SimpleAgent example."""
    # Get API keys from environment variables
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
    aws_region = os.environ.get('AWS_REGION', 'us-east-1')
    
    # Check which providers we can use
    available_providers = []
    
    # Always add Bedrock as it uses AWS credentials
    available_providers.append(("bedrock", "amazon.nova-pro-v1:0"))
    
    print("SimpleAgent Example")
    print("==================")
    
    print("\nUsing Bedrock with model amazon.nova-pro-v1:0")
    
    # Create a simple agent
    agent = SimpleAgent(
        name="ExampleAgent",
        description="A simple example agent that can answer questions",
        model_provider="bedrock",
        model_name="amazon.nova-pro-v1:0",
        temperature=0.2,
        max_tokens=512
    )
    
    print("\nAgent initialized. Type 'quit' to exit.")
    
    # Simple conversation loop
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            print("Exiting the program. Goodbye!")
            break
        
        response = agent.process_message(user_input)
        print(f"\nAgent: {response}")

if __name__ == "__main__":
    main()
