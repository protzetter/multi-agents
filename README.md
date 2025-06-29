# Multi-Agent Systems

This repository contains implementations and experiments with multi-agent AI systems using various frameworks and models.
![artifical intelligence agents coordinating between each other with a dark sky with stars in thebackground(1)](https://github.com/user-attachments/assets/48b063e7-7d69-4880-b59f-52fd13e85d3a)

## Project Overview

This project explores different approaches to multi-agent systems, particularly focused on:
- Banking onboarding processes
- Document processing and validation
- Retrieval-augmented generation (RAG)
- Agent orchestration and communication
- Stock information analysis and visualization
- Simple Language Model Agents (SimpleAgents)

## Technologies Used

- **LLM Frameworks**: Strands SDK, AutoGen, Claude API, AWS Bedrock, OpenAI
- **Vector Databases**: ChromaDB
- **UI**: Streamlit, Chainlit
- **Document Processing**: PDF analysis tools
- **Financial Data**: Yahoo Finance API
- **LLM Providers**: AWS Bedrock, OpenAI, Anthropic, HuggingFace

## Getting Started

### Prerequisites

- Python 3.8+
- Required Python packages (see `requirements.txt`)
- API keys for Claude, OpenAI, and/or AWS Bedrock

### Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install as a package:
   ```bash
   pip install -e .
   ```
   
3. Set up environment variables in `config/.env` file:
   ```
   ANTHROPIC_API_KEY=your_api_key
   OPENAI_API_KEY=your_api_key
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=your_aws_region
   BEDROCK_MODEL_ID=your_preferred_model_id
   HF_API_TOKEN=your_huggingface_token
   ```

## Project Structure

```
multi-agents/
├── config/              # Configuration files
├── data/                # Input data files
├── docs/                # Documentation
├── examples/            # Example usage scripts
├── notebooks/           # Jupyter notebooks for experiments
├── src/                 # Source code
│   ├── agents/          # Agent implementations
│   │   ├── autogen/     # AutoGen-based agents
│   │   ├── bedrock/     # AWS Bedrock-based agents
│   │   ├── claude/      # Claude API-based agents
│   │   ├── simpleagents/  # Simple Language Model Agents
│   │   └── strands/     # Strands SDK-based agents
│   │       ├── electricity_agent.py    # European electricity market agent
│   │       └── stock_info_agent.py     # Stock market agent
│   ├── tools/           # Strands tools for agents
│   │   ├── entsoe_tool.py              # ENTSOE API tools
│   │   ├── electricity_agent_tool.py   # Electricity agent wrapper tools
│   │   └── stock_info_tool.py          # Stock info tools
│   ├── ui/              # User interface implementations
│   │   └── streamlit_strands_stock_app.py  # Stock analysis UI
│   └── utils/           # Utility functions
│       ├── db/          # Database utilities
│       ├── document_processing/ # Document processing utilities
│       └── finance/     # Financial data utilities
└── tests/               # Test files
```

## Usage Examples

### Strands SDK Multi-Agent System

The Strands SDK implementation provides a powerful framework for building AI agents with access to tools, models, and orchestration capabilities.

```bash
# Run the Strands multi-agent Streamlit app
python run_strands_app.py
```

Or run individual agents:

```python
from src.agents.strands.banking_onboarding_agent import orchestrate_onboarding
from src.agents.strands.document_processing_agent import document_agent
from src.agents.strands.stock_info_agent import stock_agent
from src.agents.strands.electricity_agent import ask_electricity_agent
from src.agents.strands.rag_agent import rag_agent
from src.agents.strands.multi_agent_orchestrator import process_with_orchestration

# Use the orchestrator to route queries to specialized agents
response = process_with_orchestration("What's the current price of AAPL stock?")
print(f"[{response['agent']}]: {response['response']}")

# Or use a specific agent directly
response = stock_agent("Compare AAPL, MSFT, and GOOGL")
print(response.message)

```

For more details, see the [Strands Getting Started Guide](docs/strands_getting_started.md).


### Banking Onboarding Agent

```python
from src.agents.bedrock.banking_onboarding_api import relationship_agent, regulator_agent, orchestrator

# Initialize user session
user_id = "user123"
session_id = "session456"
chat_history = []

# Start the onboarding process
user_input = "I'd like to open a new bank account"
response = await orchestrator.route_request(user_input, user_id, session_id, chat_history)

# Process the response
print(f"Agent: {response.metadata.agent_name}")
print(f"Response: {response.output.content[0]['text']}")

# Continue the conversation until complete
while "TERMINATE" not in response.output.content[0]['text']:
    # Get next user input
    user_input = input("Your response: ")
    
    # Add previous response to chat history
    chat_history.append(response.output)
    
    # Get next response
    response = await orchestrator.route_request(user_input, user_id, session_id, chat_history)
    print(f"Response: {response.output.content[0]['text']}")

# Once complete, have the regulator agent review the information
if "TERMINATE" in response.output.content[0]['text']:
    regulator_response = await regulator_agent.process_request(
        "Please review the customer information", 
        user_id, 
        session_id, 
        chat_history
    )
    print(f"Regulator: {regulator_response.content[0]['text']}")
```

### Document Validation

```python
from src.utils.document_processing.pdf_passport_detector_refactored import PassportDetector

# Initialize the passport detector
detector = PassportDetector()

# Validate the passport
result = detector.validate_passport("path/to/passport.pdf")

# Check the results
if result['is_valid']:
    print(f"Valid passport detected for {result['name']}")
else:
    print("Invalid passport or no passport detected")
```

### Stock Information Agent

```python
from src.agents.bedrock.stock_info_agent import StockInfoAgent

# Initialize the agent
agent = StockInfoAgent(model_id="amazon.nova-pro-v1:0")

# Get stock summary
summary = agent.get_stock_summary("AAPL")
print(f"Current price: {summary['stock_info']['current_price']}")
print(summary['natural_language_summary'])

# Compare stocks
comparison = agent.compare_stocks(["AAPL", "MSFT", "GOOGL"])
print(comparison['analysis'])
```

### Stock SimpleAgent (Simple Language Model Agent)

```python
from src.agents.simpleagents.stock_agent import StockSimpleAgent

# Initialize the agent with a smaller model
agent = StockSimpleAgent(model_provider="openai", model_name="gpt-3.5-turbo")

# Get stock analysis
analysis = agent.get_stock_analysis("AAPL")
print(analysis)

# Compare stocks
comparison = agent.compare_stock_analysis(["AAPL", "MSFT", "GOOGL"])
print(comparison)

# Interactive mode
while True:
    query = input("Ask about stocks (or 'exit' to quit): ")
    if query.lower() == "exit":
        break
    response = agent.process_message(query)
    print(response)
```

### Running the UI Applications

```bash
# Run the Strands multi-agent app
python run_strands_app.py

# Run the full-featured stock app
python run_stock_app.py

# Run the lightweight SimpleAgent app
python run_simpleagent_app.py
```

Or directly with Streamlit:

```bash
# Strands multi-agent app
streamlit run src/ui/streamlit_strands_app.py

# Full-featured stock app with electricity integration
streamlit run src/ui/streamlit_strands_stock_app.py

# Lightweight SimpleAgent app
streamlit run src/ui/streamlit_simpleagent_app.py
```

## Key Features

### 🏦 Banking & Finance
- **Banking Onboarding**: Automated customer onboarding with document validation
- **Stock Market Analysis**: Real-time stock data, comparison, and visualization
- **Financial Document Processing**: PDF passport detection and validation

### ⚡ Energy Markets
- **European Electricity Markets**: Real-time analysis of 17 European countries
- **Load Forecasting**: Electricity consumption analysis and predictions
- **Price Analysis**: Day-ahead market price tracking and volatility analysis
- **Cross-Border Flows**: Inter-country electricity trade analysis
- **Renewable Integration**: Wind and solar generation forecasting
- **Market Insights**: Comprehensive electricity market intelligence

### 🤖 Multi-Agent Orchestration
- **Intelligent Routing**: Automatic query routing to specialized agents
- **Agent Coordination**: Seamless communication between different agent types
- **Tool Integration**: Extensive tool ecosystem for data access and analysis
- **Streaming Responses**: Real-time response generation and display

### 📊 Data Integration
- **Yahoo Finance**: Stock market data and financial information
- **ENTSOE API**: European electricity market transparency data
- **Document Processing**: PDF analysis and validation
- **Vector Databases**: ChromaDB for RAG implementations

## Agent Capabilities

### Stock Information Agent
- Real-time stock prices and historical data
- Multi-stock comparison and analysis
- Market overview and trends
- Financial ratio analysis
- Stock chart generation
- News integration

### Document Processing Agent
- PDF document validation
- Passport detection and verification
- Text extraction and analysis
- Document classification

### Banking Onboarding Agent
- Customer information collection
- Document verification workflow
- Regulatory compliance checking
- Multi-step process orchestration

## API Integrations & Data Sources

### Financial Data
- **Yahoo Finance API**: Real-time and historical stock data
  - Stock prices, market cap, P/E ratios
  - Historical price data and charts
  - Company news and financial metrics
  - Market indices and sector information

### LLM Providers
- **AWS Bedrock**: Amazon's managed AI service
  - Nova Pro, Claude, and other foundation models
  - Streaming responses and caching
- **Anthropic Claude**: Direct API integration
- **OpenAI**: GPT models for various tasks
- **HuggingFace**: Open-source model integration

## Tools Ecosystem

### Strands Tools (22 total)

#### Stock Market Tools (6 tools)
- `analyze_with_stock_agent()` - Main stock agent interface
- `get_stock_price()` - Real-time stock prices
- `compare_multiple_stocks()` - Multi-stock comparison
- `get_market_overview()` - Market indices and trends
- `search_stocks_by_name()` - Stock search functionality
- `get_stock_agent_capabilities()` - Agent capabilities info

#### Document & Data Tools (7 tools)
- `search_data_catalog()` - Data product search
- `get_data_product_attributes()` - Product metadata
- `list_data_products()` - Available products
- `get_data_product_location()` - Data locations
- `read_excel_file()` - Excel file processing
- `read_csv_file()` - CSV file processing
- `analyze_with_excel_agent()` - Excel analysis agent

## Environment Variables

Required environment variables for full functionality:

```bash
# LLM API Keys
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
HF_API_TOKEN=your_huggingface_token

# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
BEDROCK_REGION=us-east-1
BEDROCK_MODEL=us.amazon.nova-pro-v1:0


# Model Configuration
ANTHROPIC_MODEL=claude-3-7-sonnet-20250219
```

## Performance & Scalability

### Real-time Data Processing
- **Stock Data**: Sub-second response times for market data
- **Streaming Responses**: Progressive response generation for better UX

### Caching & Optimization
- **Bedrock Caching**: Prompt caching for improved performance
- **Data Caching**: Intelligent caching of API responses
- **Error Handling**: Robust error recovery and fallback mechanisms

### Supported Scale
- **Stock Markets**: Global stock exchanges via Yahoo Finance
- **Concurrent Users**: Multi-user support with session management
- **Data Points**: Handles thousands of data points per request

## Quick Start Examples

### 1. Stock Market Analysis
```python
# Get stock information
from src.agents.strands.stock_info_agent import ask_stock_agent

response = ask_stock_agent("Compare Apple, Microsoft, and Google stocks")
print(response)
```

### 3. Multi-Agent Orchestration
```python
# Let the orchestrator route your query
from src.agents.strands.multi_agent_orchestrator import process_with_orchestration

response = process_with_orchestration("Compare electricity prices in Europe with stock market volatility")
print(f"[{response['agent']}]: {response['response']}")
```

### 4. Direct Tool Usage
```python
# Use tools directly
from src.tools.stock_info_tool import get_stock_price

# Get Apple stock price
stock_data = get_stock_price('AAPL')
print(f"AAPL: ${stock_data['current_price']}")
```

## Troubleshooting

### Common Issues

#### AWS Credentials
```bash
# Error: "Unable to locate credentials"
# Solution: Configure AWS credentials
aws configure
# or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

#### Missing Dependencies
```bash
# Error: "ModuleNotFoundError"
# Solution: Install all dependencies
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install development dependencies: `pip install -r requirements-dev.txt`
4. Make your changes
5. Run tests: `python -m pytest tests/`
6. Submit a pull request

## License

[Specify your license here]

---

## 📊 Data Sources & Credits

- **Stock Data**: [Yahoo Finance](https://finance.yahoo.com/)
- **LLM Models**: AWS Bedrock, Anthropic Claude, OpenAI GPT
- **Framework**: [Strands SDK](https://strands.ai/)

## 🔗 Related Projects

- [Strands SDK Documentation](https://docs.strands.ai/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)

---

*Last updated: June 2025*
