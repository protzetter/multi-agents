from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.models.anthropic import AnthropicModel
import os, sys
from dotenv import load_dotenv

# Add the project root to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Import the data catalog tools
from tools.data_catalog_tool import (
    search_data_catalog,
    get_data_product_attributes,
    list_data_products,
    get_data_product_location
)
from tools.excel_tools_strands import read_csv_file

# Load environment variables
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../config/.env')
load_dotenv(config_path)

region = os.environ.get('BEDROCK_REGION', 'us-east-1')        
# Get model ID from environment variables or use default
bedrock_model_id = os.environ.get('BEDROCK_MODEL', 'amazon.nova-pro-v1:0')
anthropic_model_id = os.environ.get('ANTHROPIC_MODEL', 'claude-3-7-sonnet-20250219')
print('model: %s', anthropic_model_id)

# inb case you have access to the Claude API
key = os.getenv('ANTHROPIC_API_KEY')
anthropic_model = AnthropicModel(
    client_args={
        "api_key": key,
    },
    # **model_config
    max_tokens=1028,
    model_id=anthropic_model_id,
    params={
        "temperature": 0.7,
    }
)
model=anthropic_model
# Create a BedrockModel
# bedrock_model = BedrockModel(
#     model_id=bedrock_model_id,
#     region_name=region,
#     temperature=0.3,
# )
# model=bedrock_model
# Create the Data Catalog agent
data_catalog_agent = Agent(
    model=model,
    tools=[
        search_data_catalog,
        get_data_product_attributes,
        list_data_products,
        get_data_product_location,
        read_csv_file
    ],
    system_prompt="""
    You are a Data Catalog Assistant specialized in helping users discover, understand, and access data products.
    Your role is to:
    
    1. Help users discover available data products through search and browsing
    2. Provide detailed information about data product metadata, attributes, and structure
    3. Guide users to the right datasets for their analytical needs
    4. Explain data product characteristics, formats, and access patterns
    5. Assist with data governance and understanding data lineage
    
    Use your tools to search the data catalog, retrieve metadata, and provide comprehensive information about data products.
    Present information in a clear, organized manner and help users make informed decisions about data usage.
    
    When helping users with data discovery:
    - Listen carefully to their requirements and use cases
    - Search for relevant data products using appropriate keywords
    - Explain data product attributes and their business meaning
    - Provide information about data freshness, update frequency, and reliability
    - Guide users to the storage location and access methods
    - Highlight data quality considerations and potential limitations
    - Suggest related or complementary datasets when appropriate
   
  
    Always provide accurate, helpful guidance and be transparent about data availability and limitations.
    When users ask about data products, use the appropriate tools to retrieve the most current and detailed information.
    """
)

def orchestrate_data_catalog_query(user_query: str) -> str:
    """
    Process a user query about data catalog and return the agent's response.
    
    Args:
        user_query: The user's question or request about data products
        
    Returns:
        String response from the data catalog agent
    """
    try:
        response = data_catalog_agent(user_query)
        return response.message
    except Exception as e:
        return f"Error processing query: {str(e)}"

# Example usage
if __name__ == "__main__":
    print("Data Catalog Agent")
    print("------------------------")
    print("Ask me about available data products, their attributes, locations, or search for specific datasets.")
    print("Example queries:")
    print("- 'What data products do we have?'")
    print("- 'Tell me about the power plants dataset'")
    print("- 'Search for population data'")
    print("- 'What attributes are in the swiss_population dataset?'")
    print("Type 'exit' to quit")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            break
            
        response = data_catalog_agent(user_input)
#        print(f"\nData Catalog Assistant: {response.message}")
