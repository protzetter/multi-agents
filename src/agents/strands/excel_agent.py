from strands import Agent
from strands.models.bedrock import BedrockModel
import os,sys
from dotenv import load_dotenv

# Add the project root to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Import the Stock SimpleAgent
from src.tools.excel_tools_strands import read_csv_file

# Add the project root to the path so we can import our modules
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../config/.env')
load_dotenv(config_path)

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



# Create the Excel analysis agent
excel_agent = Agent(
    model=bedrock_model,
    tools=[read_csv_file],
    system_prompt="""
    You are an Excel data analysis assistant specialized in interpreting and visualizing spreadsheet data.
    Your role is to:
    
    1. Read and interpret Excel files, understanding their structure and content
    2. Analyze data to identify patterns, trends, and insights
    3. Generate visualizations to help users understand their data
    4. Answer questions about the data using natural language queries
    5. Provide clear explanations of your findings in business-friendly language
    
    Use your tools to read Excel files, analyze data, create visualizations, and respond to queries.
    Present information in a clear, organized manner and explain statistical concepts when needed.
    
    When analyzing Excel data:
    - Identify the key columns and their data types
    - Look for patterns, correlations, and outliers
    - Suggest appropriate visualizations based on the data structure
    - Provide context for numerical findings (is a value high/low compared to industry standards?)
    - Highlight potential data quality issues (missing values, inconsistent formats)
    
    Always provide accurate, helpful analysis and be transparent about any limitations in the data.
    """
)

# Example usage
if __name__ == "__main__":
    print("Excel Agent")
    print("------------------------")
    print("Type 'exit' to quit")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            break
            
        response = excel_agent(user_input)
        print(f"\nAssistant: {response.message['content'][0]['text']}")