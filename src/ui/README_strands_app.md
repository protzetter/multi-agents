# Multi-Agent System with Strands

This Streamlit application demonstrates a multi-agent system built using the Strands SDK. The system includes several specialized agents:

## Available Agents

1. **Orchestrator Agent** - Automatically routes queries to the most appropriate specialized agent
2. **Banking Onboarding Agent** - Handles banking account opening and compliance processes
3. **Document Processing Agent** - Validates and extracts information from documents
4. **Stock Information Agent** - Provides stock data, analysis, and visualizations
5. **Knowledge Base Agent** - Retrieves information from a banking and finance knowledge base

## Usage Instructions

1. Select an agent from the sidebar
2. Type your query in the chat input box
3. The agent will process your query and provide a response
4. You can view the agent's metadata by expanding the "View Agent Metadata" section

## Example Queries

- **Banking Agent**: "I'd like to open a new checking account" or "What documents do I need for KYC?"
- **Document Agent**: "Can you validate this passport?" or "Extract information from my bank statement"
- **Stock Agent**: "What's the current price of AAPL?" or "Compare MSFT, GOOGL, and AAPL"
- **Knowledge Base Agent**: "What are the AML requirements?" or "Explain the fee structure for checking accounts"
- **Orchestrator**: Any query - it will route to the appropriate specialized agent

## Implementation Details

This application is built using:
- Strands SDK for agent creation and orchestration
- Streamlit for the user interface
- Custom tools for each specialized agent
