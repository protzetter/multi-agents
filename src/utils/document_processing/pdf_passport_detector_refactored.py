"""
Passport detection and information extraction using AWS Bedrock Nova model.
This module provides functionality to detect passports in documents and extract relevant information.
"""
import os
import json
import base64
import io
from typing import Optional, Dict, Any, Union, BinaryIO
import boto3
import fitz  # PyMuPDF
from PIL import Image

# Configuration variables
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
NOVA_MODEL_ID = os.environ.get('NOVA_MODEL_ID', 'amazon.nova-lite-v1:0')
IMAGE_DPI = 300
IMAGE_QUALITY = 75
MAX_IMAGE_SIZE = (1024, 1024)
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'static')

def convert_document_to_image(file_obj: BinaryIO, file_name: Optional[str] = None) -> tuple:
    """
    Convert a document (PDF or image) to image bytes and determine media type.
    
    Args:
        file_obj: A file-like object containing the document
        file_name: Optional name of the file to help determine type
        
    Returns:
        tuple: (image_bytes, media_type)
    """
    # Reset file pointer
    file_obj.seek(0)
    
    # Check if it's a PDF
    is_pdf = False
    if file_name and file_name.lower().endswith('.pdf'):
        is_pdf = True
    elif hasattr(file_obj, 'name') and file_obj.name.lower().endswith('.pdf'):
        is_pdf = True
    
    if is_pdf:
        # Convert PDF to image
        pdf_bytes = file_obj.read()
        
        # Use PyMuPDF to convert PDF to image
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        if len(pdf_document) == 0:
            return None, None
            
        # Get the first page
        page = pdf_document[0]
        
        # Render page to an image
        pix = page.get_pixmap(matrix=fitz.Matrix(IMAGE_DPI/72, IMAGE_DPI/72))
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Resize if needed
        if img.size[0] > MAX_IMAGE_SIZE[0] or img.size[1] > MAX_IMAGE_SIZE[1]:
            img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=IMAGE_QUALITY)
        img_bytes = img_byte_arr.getvalue()
        
        # Close the PDF document
        pdf_document.close()
        
        return img_bytes, "image/jpeg"
    else:
        # For non-PDF files, assume it's an image
        file_obj.seek(0)
        img_bytes = file_obj.read()
        
        # Determine media type based on file extension
        media_type = "image/jpeg"  # Default
        if file_name:
            if file_name.lower().endswith(('.jpg', '.jpeg')):
                media_type = "image/jpeg"
            elif file_name.lower().endswith('.png'):
                media_type = "image/png"
        elif hasattr(file_obj, 'name'):
            if file_obj.name.lower().endswith(('.jpg', '.jpeg')):
                media_type = "image/jpeg"
            elif file_obj.name.lower().endswith('.png'):
                media_type = "image/png"
                
        return img_bytes, media_type

def get_bedrock_client():
    """
    Create and return a Bedrock runtime client.
    
    Returns:
        boto3.client: Bedrock runtime client
    """
    return boto3.client('bedrock-runtime', region_name=AWS_REGION)

def is_passport_with_nova(uploaded_file) -> bool:
    """
    Use Amazon Nova with the Converse API to determine if a document is a passport.
    
    Args:
        uploaded_file: A file-like object (can be Streamlit UploadedFile or file path)
        
    Returns:
        bool: True if the document appears to be a passport, False otherwise
    """
    try:
        # Get file name if available
        file_name = None
        if hasattr(uploaded_file, 'name'):
            file_name = uploaded_file.name
            
        # Convert document to image
        img_bytes, media_type = convert_document_to_image(uploaded_file, file_name)
        if img_bytes is None:
            return False
            
        # Create Bedrock runtime client
        bedrock_runtime = get_bedrock_client()
        
        # Create the messages array for the Converse API
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "text": "Analyze this document image and determine if it's a passport. Look for passport-specific features like the word 'PASSPORT', machine-readable zone (MRZ), passport number, personal information fields, issue and expiry dates. Respond with ONLY 'YES' if it's a passport or 'NO' if it's not a passport."
                    },
                    {
                        "image": {
                            "format": media_type.split('/')[1],
                            "source": {
                                "bytes": img_bytes
                            }
                        }
                    }
                ]
            }
        ]
        
        # Use the Converse API
        response = bedrock_runtime.converse(
            modelId=NOVA_MODEL_ID,
            messages=messages,
            inferenceConfig={
                "maxTokens": 512,
                "temperature": 0.0,
                "topP": 0.9
            }
        )
        
        # Get the model's response
        model_response = response["output"]["message"]["content"][0]["text"]
                
        # Reset file pointer if it's a file-like object
        if hasattr(uploaded_file, 'seek'):
            uploaded_file.seek(0)
        
        # Check if the response indicates it's a passport
        return "YES" in model_response.upper()
        
    except Exception as e:
        print(f"Error using Amazon Nova for passport detection: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def extract_passport_info(uploaded_file) -> Dict[str, Any]:
    """
    Use Amazon Nova with the Converse API to extract information from a passport.
    
    Args:
        uploaded_file: A file-like object (can be Streamlit UploadedFile or file path)
        
    Returns:
        dict: Dictionary containing extracted passport information or error information
    """
    try:
        # Get file name if available
        file_name = None
        if hasattr(uploaded_file, 'name'):
            file_name = uploaded_file.name
            
        # Convert document to image
        img_bytes, media_type = convert_document_to_image(uploaded_file, file_name)
        if img_bytes is None:
            return {"is_passport": False, "error": "Could not process document"}
            
        # Create Bedrock runtime client
        bedrock_runtime = get_bedrock_client()
        
        # Create the messages array for the Converse API with enhanced prompt
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "text": """Analyze this document image. First, determine if it's a passport.
                        
If it's NOT a passport, respond with: {"is_passport": false}

If it IS a passport, extract the following information and return it in this JSON format:
{
  "is_passport": true,
  "passport_number": "extracted passport number",
  "surname": "extracted surname",
  "given_names": "extracted given names",
  "nationality": "extracted nationality",
  "date_of_birth": "extracted date of birth (YYYY-MM-DD format if possible)",
  "gender": "extracted gender",
  "place_of_birth": "extracted place of birth",
  "date_of_issue": "extracted date of issue (YYYY-MM-DD format if possible)",
  "date_of_expiry": "extracted date of expiry (YYYY-MM-DD format if possible)",
  "authority": "extracted issuing authority",
  "mrz_line1": "first line of the machine readable zone if visible",
  "mrz_line2": "second line of the machine readable zone if visible"
}

For any fields you cannot find, use null instead of leaving them blank.
Return ONLY the JSON with no additional text."""
                    },
                    {
                        "image": {
                            "format": media_type.split('/')[1],
                            "source": {
                                "bytes": img_bytes
                            }
                        }
                    }
                ]
            }
        ]
        
        # Use the Converse API
        response = bedrock_runtime.converse(
            modelId=NOVA_MODEL_ID,
            messages=messages,
            inferenceConfig={
                "maxTokens": 1024,
                "temperature": 0.0,
                "topP": 0.9
            }
        )
        
        # Parse the response from the Converse API
        model_response = response["output"]["message"]["content"][0]["text"]
        
        # Reset file pointer if it's a file-like object
        if hasattr(uploaded_file, 'seek'):
            uploaded_file.seek(0)
        
        # Try to parse the JSON response
        try:
            passport_data = json.loads(model_response)
            return passport_data
        except json.JSONDecodeError:
            # If the response isn't valid JSON, try to extract JSON from the text
            import re
            json_match = re.search(r'({.*})', model_response, re.DOTALL)
            if json_match:
                try:
                    passport_data = json.loads(json_match.group(1))
                    return passport_data
                except json.JSONDecodeError:
                    pass
            
            # If we still can't parse JSON, return an error
            return {
                "is_passport": False, 
                "error": "Could not parse response",
                "raw_response": model_response[:200]  # Include part of the raw response for debugging
            }
        
    except Exception as e:
        print(f"Error extracting passport information: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"is_passport": False, "error": str(e)}

class PassportDetector:
    """
    A class for detecting and extracting information from passport documents.
    
    This class provides methods to validate passports and extract information from them
    using AWS Bedrock's Nova model.
    """
    
    def __init__(self, region: str = None, model_id: str = None):
        """
        Initialize the PassportDetector.
        
        Args:
            region: AWS region to use (defaults to environment variable or 'us-east-1')
            model_id: Bedrock model ID to use (defaults to environment variable or 'amazon.nova-lite-v1:0')
        """
        self.region = region or AWS_REGION
        self.model_id = model_id or NOVA_MODEL_ID
    
    def validate_passport(self, uploaded_file) -> Dict[str, Any]:
        """
        Validate if a document is a passport and extract its information.
        
        Args:
            uploaded_file: A file-like object or path to a passport document
            
        Returns:
            dict: Dictionary containing passport information if valid, or error information
        """
        return extract_passport_info(uploaded_file)
    
    def is_passport(self, uploaded_file) -> bool:
        """
        Check if a document is a passport.
        
        Args:
            uploaded_file: A file-like object or path to a document
            
        Returns:
            bool: True if the document is a passport, False otherwise
        """
        return is_passport_with_nova(uploaded_file)
