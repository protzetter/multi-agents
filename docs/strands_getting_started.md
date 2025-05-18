# Getting Started with Strands Agents

This guide will help you get started with the Strands SDK implementation in the multi-agent project.

## Prerequisites

1. Python 3.8 or higher
2. AWS account with access to Amazon Bedrock (for default models)
3. API keys for other model providers if not using Bedrock

## Installation

1. Install the required packages:
   ```bash
   pip install -r src/agents/strands/requirements.txt
   ```

2. Set up your environment variables in `config/.env`:
   ```
   # AWS credentials (for Bedrock)
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-west-2
   
   # Alternative model providers
   ANTHROPIC_API_KEY=your_anthropic_key
   OPENAI_API_KEY=your_openai_key
   ```

## Running the Examples

### Individual Agents

You can run each agent example individually:

```bash
python src/agents/strands/banking_onboarding_agent.py
python src/agents/strands/document_processing_agent.py
python src/agents/strands/stock_info_agent.py
python src/agents/strands/rag_agent.py
```

### Multi-Agent Orchestration

Run the multi-agent orchestrator:

```bash
python src/agents/strands/multi_agent_orchestrator.py
```

### Streamlit UI

Run the Streamlit UI for a visual interface:

```bash
python run_strands_app.py
```

Or directly with Streamlit:

```bash
streamlit run src/ui/streamlit_strands_app.py
```

## Customizing Agents

### Adding New Tools

Create custom tools using the `@tool` decorator:

```python
from strands import tool

@tool
def my_custom_tool(param1: str, param2: int) -> dict:
    """
    Tool description goes here.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        dict: Description of return value
    """
    # Tool implementation
    return {"result": f"Processed {param1} {param2} times"}
```

### Changing Models

You can use different models by specifying them during agent creation:

```python
from strands import Agent
from strands.models import BedrockModel, AnthropicModel

# Using Bedrock
bedrock_agent = Agent(
    model=BedrockModel(
        model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        temperature=0.5
    )
)

# Using Anthropic directly
anthropic_agent = Agent(
    model=AnthropicModel(
        client_args={"api_key": "your_api_key"},
        model_id="claude-3-7-sonnet-20250219"
    )
)
```

## Integration with Existing Project Components

The Strands agents can be integrated with other components of the multi-agent project:

1. **Vector Databases**: Connect the RAG agent to ChromaDB
2. **Document Processing**: Enhance the document agent with PDF analysis tools
3. **Financial Data**: Connect the stock agent to the Yahoo Finance API

See the integration examples in the documentation for more details.
