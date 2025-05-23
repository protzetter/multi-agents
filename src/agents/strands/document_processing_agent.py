from strands import Agent, tool
from strands_tools import file_read, image_reader
from strands.models import BedrockModel
from strands.models.anthropic import AnthropicModel
import os
from dotenv import load_dotenv


# Add the project root to the path so we can import our modules
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../config/.env')
load_dotenv(config_path)
region = os.environ.get('BEDROCK_REGION', 'us-east-1')        
# Get model ID from environment variables or use default
model= os.environ.get('BEDROCK_MODEL', 'amazon.nova-pro-v1:0')
print('model:%s',model)

# Create a BedrockModel
bedrock_model = BedrockModel(
    model_id=model,
    region_name=region,
    temperature=0.3,
)


@tool
def extract_passport_info(image_path: str) -> dict:
    """
    Extract information from a passport image from a pdf file
    
    Args:
        image_path: Path to the passport image file
        
    Returns:
        dict: Extracted passport information
    """
    # In a real implementation, this would use OCR and image processing
    # For this example, we'll return mock data
    
    if not os.path.exists(image_path):
        return {"error": f"File not found: {image_path}"}
    
    # Mock passport data extraction
    return {
        "document_type": "passport",
        "issuing_country": "United States",
        "passport_number": "123456789",
        "surname": "SMITH",
        "given_names": "JOHN JAMES",
        "nationality": "USA",
        "date_of_birth": "1990-01-01",
        "gender": "M",
        "date_of_issue": "2018-01-01",
        "date_of_expiry": "2028-01-01",
        "mrz_line1": "P<USASMITH<<JOHN<JAMES<<<<<<<<<<<<<<<<<<<<<",
        "mrz_line2": "1234567897USA9001014M2801011<<<<<<<<<<<<<<06"
    }

@tool
def validate_passport(passport_data: dict) -> dict:
    """
    Validate passport data for authenticity and expiration.
    
    Args:
        passport_data: Dictionary containing passport information
        
    Returns:
        dict: Validation results
    """
    # Check for required fields
    required_fields = ["passport_number", "date_of_expiry", "surname", "given_names"]
    missing_fields = [field for field in required_fields if field not in passport_data]
    
    if missing_fields:
        return {
            "is_valid": False,
            "reason": f"Missing required fields: {', '.join(missing_fields)}"
        }
    
    # Check expiration date
    from datetime import datetime
    try:
        expiry_date = datetime.strptime(passport_data["date_of_expiry"], "%Y-%m-%d")
        today = datetime.now()
        
        if expiry_date < today:
            return {
                "is_valid": False,
                "reason": "Passport has expired",
                "expiry_date": passport_data["date_of_expiry"]
            }
    except ValueError:
        return {
            "is_valid": False,
            "reason": "Invalid expiry date format"
        }
    
    # In a real implementation, additional validation would be performed
    # such as MRZ checksum validation, security feature detection, etc.
    
    return {
        "is_valid": True,
        "name": f"{passport_data['given_names']} {passport_data['surname']}",
        "passport_number": passport_data["passport_number"],
        "expiry_date": passport_data["date_of_expiry"]
    }

@tool
def extract_bank_statement_info(pdf_path: str) -> dict:
    """
    Extract information from a bank statement PDF.
    
    Args:
        pdf_path: Path to the bank statement PDF file
        
    Returns:
        dict: Extracted bank statement information
    """
    # In a real implementation, this would use PDF parsing
    # For this example, we'll return mock data
    
    if not os.path.exists(pdf_path):
        return {"error": f"File not found: {pdf_path}"}
    
    # Mock bank statement data extraction
    return {
        "document_type": "bank_statement",
        "bank_name": "Example Bank",
        "account_holder": "John Smith",
        "account_number": "XXXX-XXXX-1234",
        "statement_period": "01/04/2025 - 30/04/2025",
        "opening_balance": 5000.00,
        "closing_balance": 5432.10,
        "total_deposits": 2500.00,
        "total_withdrawals": 2067.90,
        "transactions": [
            {"date": "2025-04-02", "description": "SALARY", "amount": 2500.00, "type": "credit"},
            {"date": "2025-04-05", "description": "GROCERY STORE", "amount": -120.50, "type": "debit"},
            {"date": "2025-04-12", "description": "RESTAURANT", "amount": -85.40, "type": "debit"},
            {"date": "2025-04-18", "description": "UTILITY BILL", "amount": -150.00, "type": "debit"},
            {"date": "2025-04-25", "description": "ONLINE SHOPPING", "amount": -212.00, "type": "debit"}
        ]
    }

# Create the document processing agent
document_agent = Agent(
    model=bedrock_model,
    tools=[extract_passport_info, validate_passport, extract_bank_statement_info, file_read, image_reader],
    system_prompt="""
    You are a document processing assistant specialized in banking and identity documents.
    Your role is to:
    
    1. Extract information from various document types (passports, bank statements, etc.)
    2. Validate document authenticity and expiration
    3. Organize and summarize document information
    4. Flag potential issues or discrepancies
    
    Use your tools to process documents and provide clear, structured information to users.
    Be thorough and accurate in your document analysis.
    """
)

# Example usage
if __name__ == "__main__":
    print("Document Processing System")
    print("------------------------")
    print("Type 'exit' to quit")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            break
            
        response = document_agent(user_input)
        print(f"\nAssistant: {response.message['content'][0]['text']}")
