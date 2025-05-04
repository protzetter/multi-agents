"""
Example of using the Stock SimpleAgent.

This script demonstrates how to use the Stock SimpleAgent to retrieve
and analyze stock information using smaller language models.
"""
import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

# Import the Stock SimpleAgent
from src.agents.simpleagents.stock_agent import StockSimpleAgent

def main():
    """Run the Stock SimpleAgent example."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Stock SimpleAgent Example')
    parser.add_argument('--provider', type=str, default='openai',
                        help='Model provider (openai, anthropic, huggingface, bedrock, local)')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo',
                        help='Model name')
    parser.add_argument('--interactive', action='store_true',
                        help='Run in interactive mode')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    args = parser.parse_args()
    
    # Set up logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Initialize the Stock SimpleAgent
    print(f"Initializing Stock SimpleAgent with {args.provider}/{args.model}...")
    agent = StockSimpleAgent(
        model_provider=args.provider,
        model_name=args.model
    )
    
    print("\nStock SimpleAgent Example")
    print("======================")
    
    if args.interactive:
        # Interactive mode
        print("\nEnter your questions about stocks or the market (type 'exit' to quit):")
        while True:
            user_input = input("\n> ")
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
            
            print("\nProcessing...")
            response = agent.process_message(user_input)
            print(f"\nAgent: {response}")
    else:
        # Demo mode with predefined examples
        examples = [
            "What's the current price of AAPL?",
            "How has MSFT performed over the last month?",
            "Compare AMZN, GOOGL, and META",
            "What are the latest news about TSLA?",
            "Give me a summary of the current market conditions"
        ]
        
        for i, example in enumerate(examples):
            print(f"\nExample {i+1}: {example}")
            print("\nProcessing...")
            response = agent.process_message(example)
            print(f"\nAgent: {response}")
            
            # Reset the agent for the next example
            if i < len(examples) - 1:
                agent.reset()
                print("\n" + "-" * 50)

if __name__ == "__main__":
    main()
