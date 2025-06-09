"""
Data Catalog Tool Example

This example demonstrates how to use the data catalog tool with Strands agents
to search and retrieve metadata about available data products.
"""

from strands.models.bedrock import BedrockModel
import os,sys
from dotenv import load_dotenv
# Add the project root to the path so we can import our modules
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config/.env')
load_dotenv(config_path)


# Add the src directory to the path so we can import our tools
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from strands import Agent
from tools.data_catalog_tool import (
    search_data_catalog,
    get_data_product_attributes,
    list_data_products,
    get_data_product_location
)


def main():
    """Main function to demonstrate the data catalog tool usage."""
    
    print("=== Data Catalog Tool Example ===\n")

    region = os.environ.get('BEDROCK_REGION', 'us-east-1')        
    # Get model ID from environment variables or use default
    model= os.environ.get('BEDROCK_MODEL', 'amazon.nova-pro-v1:0')
    print('model:%s',model)
    # Create a BedrockModel
    bedrock_model = BedrockModel(
        model_id=model,
        region_name=region,
        temperature=0.3,
    )
   
    # Create an agent with data catalog tools
    agent = Agent(
        model=bedrock_model,
        tools=[
            search_data_catalog,
            get_data_product_attributes,
            list_data_products,
            get_data_product_location
        ],
        system_prompt="""You are a data catalog assistant. Help users discover and understand 
        available data products. When users ask about data, use the catalog tools to provide 
        accurate information about datasets, their attributes, locations, and metadata."""
    )
    
    # Example queries to demonstrate the agent's capabilities
    example_queries = [
        "What data products do we have available?",
        "Tell me about the Swiss power plants dataset",
        "What attributes are available in the population data?",
        "Where is the power plants data stored and in what format?",
        "Search for any data products related to energy",
        "Show me details about the swiss_population data product"
    ]
    
    print("Running example queries...\n")
    
    for i, query in enumerate(example_queries, 1):
        print(f"Query {i}: {query}")
        print("-" * 50)
        
        try:
            response = agent(query)
#            print(f"Response: {response.message.content[0].text}\n")
        except Exception as e:
            print(f"Error: {e}\n")
    
    # Interactive mode
    print("=" * 60)
    print("Interactive Mode - Ask questions about the data catalog!")
    print("Type 'quit' to exit")
    print("=" * 60)
    
    while True:
        user_query = input("\nYour question: ").strip()
        
        if user_query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not user_query:
            continue
            
        try:
            response = agent(user_query)
#            print(f"\nAgent: {response.message.content[0].text}")
        except Exception as e:
            print(f"Error: {e}")


def direct_tool_usage_example():
    """Example of using the tools directly without an agent."""
    
    print("\n=== Direct Tool Usage Examples ===\n")
    
    # List all data products
    print("1. Listing all data products:")
    result = list_data_products()
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    for product_id, info in result['products'].items():
        print(f"  - {product_id}: {info['name']} ({info['format']}, {info['record_count']} records)")
    
    print("\n" + "="*50 + "\n")
    
    # Search for specific data
    print("2. Searching for 'power' related data:")
    result = search_data_catalog(query="power")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    for product_id, metadata in result['matching_products'].items():
        print(f"  - {product_id}: {metadata['name']}")
    
    print("\n" + "="*50 + "\n")
    
    # Get specific data product details
    print("3. Getting details for swiss_power_plants:")
    result = search_data_catalog(data_product_id="swiss_power_plants")
    if result['status'] == 'success':
        metadata = result['metadata']
        print(f"Name: {metadata['name']}")
        print(f"Description: {metadata['description']}")
        print(f"Format: {metadata['format']}")
        print(f"Location: {metadata['location']}")
        print(f"Attributes: {len(metadata['attributes'])} total")
    
    print("\n" + "="*50 + "\n")
    
    # Get attributes for a data product
    print("4. Getting attributes for swiss_population:")
    result = get_data_product_attributes("swiss_population")
    if result['status'] == 'success':
        print(f"Data Product: {result['data_product_name']}")
        print(f"Total Attributes: {result['attribute_count']}")
        print("Attributes:")
        for attr in result['attributes']:
            print(f"  - {attr}")
    
    print("\n" + "="*50 + "\n")
    
    # Get location information
    print("5. Getting location info for swiss_population:")
    result = get_data_product_location("swiss_population")
    if result['status'] == 'success':
        print(f"Data Product: {result['data_product_name']}")
        print(f"Location: {result['location']}")
        print(f"Format: {result['format']}")
        print(f"Data Owner: {result['data_owner']}")
        print(f"Last Updated: {result['last_updated']}")
        print(f"Update Frequency: {result['update_frequency']}")
        print(f"Record Count: {result['record_count']:,}")


if __name__ == "__main__":
    print("Choose an example to run:")
    print("1. Agent-based example (interactive)")
    print("2. Direct tool usage example")
    print("3. Both")
    
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    
    if choice == "1":
        main()
    elif choice == "2":
        direct_tool_usage_example()
    elif choice == "3":
        direct_tool_usage_example()
        main()
    else:
        print("Invalid choice. Running direct tool usage example...")
        direct_tool_usage_example()
