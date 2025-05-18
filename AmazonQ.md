# Strands SDK Integration for Multi-Agent Systems

This document outlines the implementation of Strands SDK in the multi-agent systems project.

## Overview

The Strands SDK provides a powerful framework for building AI agents with access to tools, models, and orchestration capabilities. This implementation demonstrates how to use Strands to create a multi-agent system for banking onboarding, document processing, stock information analysis, and knowledge retrieval.

## Implementation Details

The implementation includes:

1. **Banking Onboarding Agents**
   - Relationship manager agent for customer interactions
   - Regulator agent for compliance checks
   - Tools for customer validation and compliance requirements

2. **Document Processing Agent**
   - Tools for extracting information from passports and bank statements
   - Document validation capabilities
   - Integration with image and file processing

3. **Stock Information Agent**
   - Stock data retrieval and comparison
   - Chart generation capabilities
   - Financial analysis tools

4. **RAG-Enhanced Knowledge Agent**
   - Knowledge base search functionality
   - Information retrieval and synthesis
   - Banking and finance domain knowledge

5. **Multi-Agent Orchestrator**
   - Query routing based on content analysis
   - Coordination between specialized agents
   - Workflow management

6. **Streamlit UI**
   - Interactive chat interface
   - Agent selection and visualization
   - Response metadata inspection

## Directory Structure

```
multi-agents/
├── src/
│   ├── agents/
│   │   └── strands/
│   │       ├── __init__.py
│   │       ├── banking_onboarding_agent.py
│   │       ├── document_processing_agent.py
│   │       ├── stock_info_agent.py
│   │       ├── rag_agent.py
│   │       ├── multi_agent_orchestrator.py
│   │       └── requirements.txt
│   └── ui/
│       ├── streamlit_strands_app.py
│       └── README_strands_app.md
├── docs/
│   └── strands_getting_started.md
└── run_strands_app.py
```

## Getting Started

See the [Getting Started Guide](docs/strands_getting_started.md) for installation and usage instructions.

## Key Features

- **Tool-based Agent Architecture**: Agents use specialized tools to perform tasks
- **Model Flexibility**: Support for various LLM providers including Bedrock, Anthropic, and more
- **Multi-Agent Orchestration**: Intelligent routing of queries to specialized agents
- **Interactive UI**: Streamlit-based interface for easy interaction
- **Extensibility**: Easy to add new tools and agents

## Future Enhancements

- Integration with ChromaDB for vector storage
- Connection to real financial data APIs
- Enhanced document processing with OCR
- Agent memory and persistent state
- Multi-step workflows with agent collaboration
