# Multi-Agent Systems

This repository contains implementations and experiments with multi-agent AI systems using various frameworks and models.

## Project Overview

This project explores different approaches to multi-agent systems, particularly focused on:
- Banking onboarding processes
- Document processing and validation
- Retrieval-augmented generation (RAG)
- Agent orchestration and communication

## Technologies Used

- **LLM Frameworks**: AutoGen, Claude API, AWS Bedrock
- **Vector Databases**: ChromaDB
- **UI**: Streamlit, Chainlit
- **Document Processing**: PDF analysis tools

## Getting Started

### Prerequisites

- Python 3.8+
- Required Python packages (see `requirements.txt`)
- API keys for Claude and/or AWS Bedrock

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
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
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
│   │   └── claude/      # Claude API-based agents
│   ├── ui/              # User interface implementations
│   └── utils/           # Utility functions
│       ├── db/          # Database utilities
│       └── document_processing/ # Document processing utilities
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Specify your license here]
