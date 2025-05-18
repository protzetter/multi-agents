from strands import Agent, tool
from strands_tools import calculator, current_time, python_repl
from strands.models import BedrockModel
from strands.models.anthropic import AnthropicModel
import json
import os
from dotenv import load_dotenv

# Add the project root to the path so we can import our modules
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../config/.env')
load_dotenv(config_path)
model= os.getenv('BEDROCK_MODEL')
region= os.getenv('BEDROCK_REGION')

# Create a BedrockModel
bedrock_model = BedrockModel(
    model_id=model,
    region_name=region,
    temperature=0.3,
)

key = os.getenv('ANTHROPIC_API_KEY')
anthropic_model = AnthropicModel(
    client_args={
        "api_key": key,
    },
    # **model_config
    max_tokens=1028,
    model_id="claude-3-7-sonnet-20250219",
    params={
        "temperature": 0.7,
    }
)

# Define custom tools for banking onboarding
@tool
def validate_customer_id(customer_id: str) -> dict:
    """
    Validate a customer ID format and check if it exists in the system.
    
    Args:
        customer_id: The customer ID to validate
        
    Returns:
        dict: Validation result with status and message
    """
    # In a real implementation, this would check against a database
    if len(customer_id) != 10 or not customer_id.isalnum():
        return {"valid": False, "message": "Invalid customer ID format. Must be 10 alphanumeric characters."}
    
    # Mock validation - in production would check against actual database
    return {"valid": True, "message": "Customer ID validated successfully"}

@tool
def check_compliance_requirements(customer_type: str, risk_level: str) -> dict:
    """
    Check compliance requirements for a customer based on type and risk level.
    
    Args:
        customer_type: Type of customer (individual, business, etc.)
        risk_level: Risk assessment level (low, medium, high)
        
    Returns:
        dict: Required compliance documents and checks
    """
    requirements = {
        "individual": {
            "low": ["government_id", "proof_of_address"],
            "medium": ["government_id", "proof_of_address", "source_of_funds"],
            "high": ["government_id", "proof_of_address", "source_of_funds", "enhanced_due_diligence"]
        },
        "business": {
            "low": ["business_registration", "tax_id", "ownership_structure"],
            "medium": ["business_registration", "tax_id", "ownership_structure", "financial_statements"],
            "high": ["business_registration", "tax_id", "ownership_structure", "financial_statements", "enhanced_due_diligence"]
        }
    }
    
    if customer_type not in requirements:
        return {"error": f"Unknown customer type: {customer_type}"}
    
    if risk_level not in requirements[customer_type]:
        return {"error": f"Unknown risk level: {risk_level}"}
    
    return {
        "required_documents": requirements[customer_type][risk_level],
        "customer_type": customer_type,
        "risk_level": risk_level
    }

@tool
def save_customer_information(customer_data: dict) -> dict:
    """
    Save customer information to the system.
    
    Args:
        customer_data: Dictionary containing customer information
        
    Returns:
        dict: Operation result with status and customer ID
    """
    # In production, this would save to a database
    # For this example, we'll just return a success message
    
    required_fields = ["name", "address", "date_of_birth", "id_type", "id_number"]
    missing_fields = [field for field in required_fields if field not in customer_data]
    
    if missing_fields:
        return {
            "success": False,
            "message": f"Missing required fields: {', '.join(missing_fields)}"
        }
    
    # Generate a mock customer ID
    import random
    import string
    customer_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    return {
        "success": True,
        "customer_id": customer_id,
        "message": "Customer information saved successfully"
    }

# Create the relationship manager agent
relationship_agent = Agent(
    model=anthropic_model,
    tools=[validate_customer_id, check_compliance_requirements, save_customer_information, current_time],
    system_prompt="""
    You are a helpful banking relationship manager assistant. Your role is to help customers open new bank accounts
    and guide them through the onboarding process. You should:
    
    1. Collect necessary customer information (name, address, date of birth, ID information)
    2. Explain account options and requirements
    3. Help customers complete required documentation
    4. Answer questions about banking services
    5. Ensure compliance with banking regulations
    
    Be professional, courteous, and thorough. Protect customer privacy and follow all banking regulations.
    Use your tools to validate information and check compliance requirements.
    """
)

# Create the regulator agent
regulator_agent = Agent(
    model= anthropic_model,
    tools=[check_compliance_requirements],
    system_prompt="""
    You are a banking compliance officer responsible for ensuring all customer onboarding processes
    follow regulatory requirements. Your role is to:
    
    1. Review customer information for compliance issues
    2. Verify that all required documentation has been collected
    3. Flag potential regulatory concerns
    4. Ensure anti-money laundering (AML) and know-your-customer (KYC) requirements are met
    
    Be thorough and strict in your compliance checks. Your primary concern is regulatory compliance,
    not customer satisfaction.
    """
)

# Create a simple orchestrator function
def orchestrate_onboarding(user_input, user_id, session_id, chat_history=None):
    """
    Orchestrate the banking onboarding process between agents.
    
    Args:
        user_input: The user's message
        user_id: Unique identifier for the user
        session_id: Unique identifier for the session
        chat_history: List of previous interactions
        
    Returns:
        dict: Response from the appropriate agent
    """
    chat_history = chat_history or []
    
    # Simple keyword-based routing
    compliance_keywords = ["compliance", "regulation", "aml", "kyc", "risk", "verify"]
    
    # Check if any compliance keywords are in the user input
    if any(keyword in user_input.lower() for keyword in compliance_keywords):
        # Route to regulator agent
        response = regulator_agent(user_input)
        return {
            "agent": "regulator",
            "response": response.message
        }
    else:
        # Default to relationship manager
        response = relationship_agent(user_input)
        return {
            "agent": "relationship_manager",
            "response": response.message
        }

# Example usage
if __name__ == "__main__":
    # Simulate a conversation
    user_id = "user123"
    session_id = "session456"
    chat_history = []
    
    print("Banking Onboarding System")
    print("------------------------")
    print("Type 'exit' to quit")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            break
            
        response = orchestrate_onboarding(user_input, user_id, session_id, chat_history)
        #print(f"\n[{response['agent']}]: {response['response']}")
        
        # Add to chat history
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": response['response']})
