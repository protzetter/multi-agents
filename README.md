# Multi-Agent Systems

This repository contains implementations and experiments with multi-agent AI systems using various frameworks and models.

## Project Overview

This project explores different approaches to multi-agent systems, particularly focused on:
- Banking onboarding processes
- Document processing and validation
- Retrieval-augmented generation (RAG)
- Agent orchestration and communication
- Stock information analysis and visualization
- Simple Language Model Agents (SimpleAgents)

## Technologies Used

- **LLM Frameworks**: AutoGen, Claude API, AWS Bedrock, OpenAI
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
│   │   └── simpleagents/  # Simple Language Model Agents
│   ├── ui/              # User interface implementations
│   └── utils/           # Utility functions
│       ├── db/          # Database utilities
│       ├── document_processing/ # Document processing utilities
│       └── finance/     # Financial data utilities
└── tests/               # Test files
```

## Usage Examples

### Banking Onboarding Agent

```python
from src.agents.claude.banking_onboarding import BankingOnboardingAgent

# Initialize the agent
agent = BankingOnboardingAgent()

# Run the onboarding process
agent.start_onboarding(
    customer_name="John Doe",
    customer_id="12345",
    product_type="checking_account"
)

# Get the results
results = agent.get_results()
print(f"Onboarding completed with status: {results['status']}")
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

### Running the Stock Information UI

```bash
# Run the full-featured Streamlit app
python run_stock_app.py

# Run the lightweight SimpleAgent app
python run_simpleagent_app.py
```

Or directly with Streamlit:

```bash
# Full-featured app
streamlit run src/ui/streamlit_stock_app.py

# Lightweight SimpleAgent app
streamlit run src/ui/streamlit_simpleagent_app.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Specify your license here]
