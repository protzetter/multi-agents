#Lets import the modules needed for this exercise
import boto3
import json
from typing import Optional
import fitz
import base64
from PIL import Image
import io
import requests
import os
import PyPDF2

#Function to convert PDF files to a list of base64-encoded PNG images
def pdf_to_base64_pngs(file, quality=75, max_size=(1024, 1024)):
    base64_encoded_pngs = []
    doc = PyPDF2.PdfReader(file)        
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        with io.BytesIO() as image_data:
            image.save(image_data, format='PNG', optimize=True, quality=quality)
            base64_encoded = base64.b64encode(image_data.getvalue()).decode('utf-8')
            base64_encoded_pngs.append(base64_encoded)
    return base64_encoded_pngs


import boto3
import base64
import json
import io
import fitz  # PyMuPDF
from PIL import Image

import boto3
import base64
import json
import io
import fitz  # PyMuPDF
from PIL import Image

def extract_passport_info(uploaded_file):
    """
    Use Amazon Nova with the Converse API to extract information from a passport.
    
    Args:
        uploaded_file: A file-like object (can be Streamlit UploadedFile or file path)
        
    Returns:
        dict: Dictionary containing extracted passport information or None if not a passport
    """
    try:
        # Create Bedrock runtime client
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Convert PDF to image if needed
        if hasattr(uploaded_file, 'name') and uploaded_file.name.lower().endswith('.pdf'):
            # Reset file pointer and read content
            uploaded_file.seek(0)
            pdf_bytes = uploaded_file.read()
            
            # Use PyMuPDF (fitz) to convert PDF to image
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            if len(pdf_document) == 0:
                return None
                
            # Get the first page
            page = pdf_document[0]
            
            # Render page to an image (300 DPI)
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Convert to base64
            base64_image = base64.b64encode(img_byte_arr).decode('utf-8')
            media_type = "image/jpeg"
            
            # Close the PDF document
            pdf_document.close()
        else:
            # For non-PDF files, assume it's an image
            uploaded_file.seek(0)
            bytes_data = uploaded_file.read()
            
            # Determine media type based on file extension
            if hasattr(uploaded_file, 'name'):
                if uploaded_file.name.lower().endswith('.jpg') or uploaded_file.name.lower().endswith('.jpeg'):
                    media_type = "image/jpeg"
                elif uploaded_file.name.lower().endswith('.png'):
                    media_type = "image/png"
                else:
                    # Default to JPEG if unknown
                    media_type = "image/jpeg"
            else:
                # Default to JPEG if no filename
                media_type = "image/jpeg"
                
            base64_image = base64.b64encode(bytes_data).decode('utf-8')
        
        # Specify which Nova model to use
        model_id = "amazon.nova-lite-v1:0"
        
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
                            "format": "jpeg",
                            "source": {
                                "bytes": img_byte_arr
                            }
                        }
                    }
                ]
            }
        ]
        
        # Use the Converse API
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig={
                "maxTokens": 1024,  # Increased token limit for more detailed response
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
            
            # convert json to dictionary
            model_response = json.loads(response["body"].read())
            return model_response

        
    except Exception as e:
        print(f"Error extracting passport information: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"is_passport": False, "error": str(e)}
    



def is_passport_with_nova(uploaded_file):
    """
    Use Amazon Nova with the Converse API to determine if a document is a passport.
    
    Args:
        uploaded_file: A file-like object (can be Streamlit UploadedFile or file path)
        
    Returns:
        bool: True if the document appears to be a passport, False otherwise
    """
    try:
        # Create Bedrock runtime client
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Convert PDF to image if needed
        if hasattr(uploaded_file, 'name') and uploaded_file.name.lower().endswith('.pdf'):
            # Reset file pointer and read content
            uploaded_file.seek(0)
            pdf_bytes = uploaded_file.read()
            
            # Use PyMuPDF (fitz) to convert PDF to image
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            if len(pdf_document) == 0:
                return False
                
            # Get the first page
            page = pdf_document[0]
            
            # Render page to an image (300 DPI)
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Convert to base64
            base64_image = base64.b64encode(img_byte_arr).decode('utf-8')
            media_type = "image/jpeg"
            print("PDF converted to image for analysis.")
            
            # Close the PDF document
            pdf_document.close()
        else:
            # For non-PDF files, assume it's an image
            uploaded_file.seek(0)
            bytes_data = uploaded_file.read()
            
            # Determine media type based on file extension
            if hasattr(uploaded_file, 'name'):
                if uploaded_file.name.lower().endswith('.jpg') or uploaded_file.name.lower().endswith('.jpeg'):
                    media_type = "image/jpeg"
                elif uploaded_file.name.lower().endswith('.png'):
                    media_type = "image/png"
                else:
                    # Default to JPEG if unknown
                    media_type = "image/jpeg"
            else:
                # Default to JPEG if no filename
                media_type = "image/jpeg"
                
            base64_image = base64.b64encode(bytes_data).decode('utf-8')
        
        # Specify which Nova model to use
        model_id = "amazon.nova-lite-v1:0"
        
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
                            "format": "jpeg",
                            "source": {
                                "bytes": img_byte_arr
                            }
                        }
                    }
                ]
            }
        ]
        
        # Use the Converse API
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig={
                "maxTokens": 512,
                "temperature": 0.0,
                "topP": 0.9
            }
        )
        
        # Parse the response from the Converse API
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
