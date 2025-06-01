# Stock Agent MCP Server

This directory contains an MCP (Model Context Protocol) server implementation that exposes the Strands stock agent functionality through a standardized interface.

## Overview

The Stock Agent MCP Server provides tools for:

1. Getting stock information for specific symbols
2. Comparing multiple stocks
3. Getting market summaries
4. Generating chart code for stock visualization
5. Searching for stocks by name or ticker
6. Asking the stock agent questions about stocks and financial analysis

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure you have the necessary environment variables set in your `config/.env` file:

```
ANTHROPIC_API_KEY=your_api_key
OPENAI_API_KEY=your_api_key
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_aws_region
BEDROCK_MODEL_ID=your_preferred_model_id
```

## Running the Server

To run the MCP server:

```bash
python run_stock_mcp_server.py
```

For debug logging:

```bash
python run_stock_mcp_server.py --debug
```

And ask questions like:
- "What's the current price of AAPL stock?"
- "Compare AAPL, MSFT, and GOOGL"
- "Show me a market summary"
- "Generate a chart for TSLA over the last 30 days"

## Available Tools

The server exposes the following tools:

- `ask_stock_agent`: Ask the stock agent questions about stocks and markets

## Architecture

The MCP server is built on top of the Strands SDK stock agent implementation. It uses:

- MCP for standardized tool interfaces
- Strands SDK for agent functionality
- Yahoo Finance API for stock data retrieval
- Bedrock or Anthropic models for analysis and responses


