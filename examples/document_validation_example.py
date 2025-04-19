"""
Example of using the document validation utilities.
"""
import os
import sys
from dotenv import load_dotenv

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

# Import the document processing utilities
from src.utils.document_processing.pdf_passport_detector_refactored import PassportDetector

def main():
    """Run the document validation example."""
    # Initialize the passport detector
    detector = PassportDetector()
    
    # Path to a sample passport PDF
    pdf_path = input("Enter the path to a PDF file to analyze (or press Enter to exit): ")
    
    if not pdf_path:
        print("No file provided. Exiting.")
        return
        
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return
    
    print(f"Analyzing file: {pdf_path}")
    
    # Open the file
    with open(pdf_path, 'rb') as file:
        # Validate the passport
        result = detector.validate_passport(file)
    
        # Print the results
        if result.get('is_passport', False):
            print("\n✅ Valid passport detected!")
            print(f"Passport number: {result.get('passport_number', 'Not found')}")
            print(f"Name: {result.get('given_names', '')} {result.get('surname', '')}")
            print(f"Nationality: {result.get('nationality', 'Not found')}")
            print(f"Date of birth: {result.get('date_of_birth', 'Not found')}")
            print(f"Expiry date: {result.get('date_of_expiry', 'Not found')}")
        else:
            print("\n❌ Invalid passport or no passport detected")
            if 'error' in result:
                print(f"Reason: {result['error']}")

if __name__ == "__main__":
    main()
