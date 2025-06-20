from mcp import stdio_client, StdioServerParameters
from mcp.client.sse import sse_client
from strands import Agent
from strands.tools.mcp import MCPClient
from strands.models import BedrockModel
from strands.models.anthropic import AnthropicModel
import os, dotenv
# Add the project root to the path so we can import our modules
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../config/.env')
dotenv.load_dotenv(config_path)

region = os.environ.get('BEDROCK_REGION', 'us-east-1')        
# Get model ID from environment variables or use default
model= os.environ.get('BEDROCK_MODEL', 'us.amazon.nova-pro-v1:0')
ant_model=os.environ.get('ANTHROPIC_MODEL', 'claude-3-7-sonnet-20250219')                      
print('model:%s',model)
print('ant_model:%s', ant_model)
bedrock_model=BedrockModel(
    region_name=region,
    max_tokens=1028,
    model_id=model,
    params={
        "temperature": 0.7,
    }
)
key = os.getenv('ANTHROPIC_API_KEY')
anthropic_model = AnthropicModel(
    client_args={
        "api_key": key,
    },
    # **model_config
    max_tokens=1028,
    model_id=ant_model,
    params={
        "temperature": 0.7,
    }
)
# Use both servers together
def main():
    # Connect to multiple MCP servers
    sse_mcp_client = MCPClient(lambda: sse_client("http://127.0.0.1:8000/sse"))
    with sse_mcp_client:
        tools = sse_mcp_client.list_tools_sync()
        for t in tools:
            print(t.tool_name)

        # Create an agent with all tools
        agent = Agent(model=anthropic_model, tools=tools)
        # Run the agent
        agent('can you give me a stock market overview ?',streaming=False)

if __name__ == "__main__":
    main()