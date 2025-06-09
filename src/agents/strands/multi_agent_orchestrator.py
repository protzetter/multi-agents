from strands import Agent, tool
from strands_tools import agent_graph, workflow, think
from strands.models import BedrockModel
from strands.models.anthropic import AnthropicModel
import json
import os
import sys
from pathlib import Path

# Add the project root to the path to import our modules
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Import our specialized agents
try:
    from src.agents.strands.banking_onboarding_agent import relationship_agent, regulator_agent
    from src.agents.strands.document_processing_agent import document_agent
    from src.agents.strands.stock_info_agent import stock_agent
    from src.agents.strands.rag_agent import rag_agent
    from src.agents.strands.data_catalog_agent import data_catalog_agent
except ImportError:
    print("Warning: Some agent modules could not be imported. Make sure all required files exist.")
    # Create placeholder agents if imports fail
    from strands import Agent
    relationship_agent = Agent(system_prompt="Banking relationship manager placeholder")
    regulator_agent = Agent(system_prompt="Banking regulator placeholder")
    document_agent = Agent(system_prompt="Document processing placeholder")
    stock_agent = Agent(system_prompt="Stock information placeholder")
    rag_agent = Agent(system_prompt="Knowledge base placeholder")
    data_catalog_agent = Agent(system_prompt="Data catalog placeholder")

@tool
def route_to_agent(query: str) -> dict:
    """
    Determine which specialized agent should handle a user query.
    
    Args:
        query: The user's query text
        
    Returns:
        dict: The routing decision with agent name and confidence
    """
    # Simple keyword-based routing
    banking_keywords = ["account", "bank", "onboarding", "kyc", "customer", "deposit", "withdraw"]
    document_keywords = ["document", "passport", "statement", "extract", "validate", "pdf", "image"]
    stock_keywords = ["stock", "price", "market", "invest", "share", "dividend", "chart"]
    data_catalog_keywords = ["data", "dataset", "catalog", "metadata", "attributes", "power plants", "population", "swiss", "data product"]
    
    # Count keyword matches for each agent type
    banking_score = sum(1 for keyword in banking_keywords if keyword in query.lower())
    document_score = sum(1 for keyword in document_keywords if keyword in query.lower())
    stock_score = sum(1 for keyword in stock_keywords if keyword in query.lower())
    data_catalog_score = sum(1 for keyword in data_catalog_keywords if keyword in query.lower())
    
    # Find the agent with the highest score
    scores = {
        "banking": banking_score,
        "document": document_score,
        "stock": stock_score,
        "data_catalog": data_catalog_score
    }
    
    max_score = max(scores.values())
    if max_score == 0:
        # No clear match, use general assistant
        return {
            "agent": "general",
            "confidence": 1.0,
            "reason": "No specialized agent matches the query"
        }
    
    # Get the agent with the highest score
    selected_agent = max(scores, key=scores.get)
    confidence = max_score / sum(scores.values())
    
    return {
        "agent": selected_agent,
        "confidence": confidence,
        "reason": f"Query contains keywords related to {selected_agent}"
    }

# Create the orchestrator agent
orchestrator = Agent(
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    tools=[route_to_agent, agent_graph, workflow, think],
    system_prompt="""
    You are an orchestrator agent responsible for coordinating between specialized agents.
    Your role is to:
    
    1. Analyze user queries to determine the most appropriate specialized agent
    2. Route requests to the correct agent based on the query content
    3. Coordinate multi-step workflows that may involve multiple agents
    4. Maintain context and state across agent interactions
    5. Provide a seamless experience for the user
    
    Available specialized agents:
    - Banking Agent: Handles account opening, customer onboarding, and banking services
    - Document Agent: Processes and validates documents like passports and bank statements
    - Stock Agent: Provides stock information, analysis, and visualizations
    - Data Catalog Agent: Helps discover and understand available data products and their metadata
    
    Use your tools to route queries and coordinate workflows between these agents.
    """
)

# Function to handle multi-agent orchestration
def process_with_orchestration(user_input, session_id=None):
    """
    Process a user query through the orchestrator and route to specialized agents.
    
    Args:
        user_input: The user's query
        session_id: Optional session identifier for maintaining context
        
    Returns:
        dict: Response from the appropriate agent
    """
    # First, use the orchestrator to determine which agent should handle the query
    orchestrator_response = orchestrator(f"Route this query to the appropriate agent: {user_input}")
    
    # Extract the routing decision from the orchestrator's response
    routing_info = None
    for tool_use in orchestrator_response.metadata.get("tool_uses", []):
        if tool_use.get("name") == "route_to_agent":
            routing_info = tool_use.get("output", {})
            break
    
    if not routing_info:
        # If no routing info, use the orchestrator's response directly
        return {
            "agent": "orchestrator",
            "response": orchestrator_response.message,
            "metadata": orchestrator_response.metadata
        }
    
    # Route to the appropriate agent based on the orchestrator's decision
    agent_type = routing_info.get("agent")
    
    if agent_type == "banking":
        response = relationship_agent(user_input)
        agent_name = "Banking Agent"
    elif agent_type == "document":
        response = document_agent(user_input)
        agent_name = "Document Agent"
    elif agent_type == "stock":
        response = stock_agent(user_input)
        agent_name = "Stock Agent"
    elif agent_type == "data_catalog":
        response = data_catalog_agent(user_input)
        agent_name = "Data Catalog Agent"
    else:
        # Default to orchestrator for general queries
        response = orchestrator(user_input)
        agent_name = "General Assistant"
    
    return {
        "agent": agent_name,
        "response": response.message,
        "confidence": routing_info.get("confidence", 1.0),
        "metadata": response.metadata
    }

# Example usage
if __name__ == "__main__":
    print("Multi-Agent Orchestration System")
    print("--------------------------------")
    print("Type 'exit' to quit")
    
    session_id = f"session_{os.urandom(4).hex()}"
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            break
            
        response = process_with_orchestration(user_input, session_id)
        print(f"\n[{response['agent']}]: {response['response']}")
