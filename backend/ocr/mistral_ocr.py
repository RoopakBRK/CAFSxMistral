"""
Mistral OCR Wrapper - Updated for correct API format
"""

import base64
import json
import os
from typing import Dict, Any
from mistralai import Mistral
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()


class MistralOCR:
    """Mistral OCR - OCR and structured extraction in one API call"""
    
    def __init__(self):
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment")
        
        self.client = Mistral(api_key=api_key)
        logger.info("[INFO] Mistral OCR initialized")
    
    def extract_certificate_data(self, image_path: str) -> Dict[str, Any]:
        """
        Extract structured certificate data using Mistral OCR.
        
        Uses Mistral's Vision API for image analysis + structured extraction.
        """
        
        # Read and encode document
        with open(image_path, "rb") as f:
            file_content = f.read()
            image_base64 = base64.b64encode(file_content).decode()
        
        # Determine file type
        file_ext = image_path.lower().split('.')[-1]
        if file_ext in ['jpg', 'jpeg']:
            mime_type = "image/jpeg"
        elif file_ext == 'png':
            mime_type = "image/png"
        elif file_ext == 'pdf':
            mime_type = "application/pdf"
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        try:
            logger.info(f"[INFO] Calling Mistral Vision API...")
            
            # Use Mistral Chat with Vision + JSON mode for structured extraction
            response = self.client.chat.complete(
                model="pixtral-12b-2409",  # Mistral's vision model
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": f"data:{mime_type};base64,{image_base64}"
                            },
                            {
                                "type": "text",
                                "text": """Extract ALL information from this certificate image.

Return a JSON object with these fields:
{
  "student_name": "Full name of certificate recipient",
  "issuer": "Organization that issued it (Udemy, Coursera, edX, etc.)",
  "course_name": "Course or program name",
  "completion_date": "Date in YYYY-MM-DD format",
  "certificate_ids": ["All IDs, reference numbers, serial numbers found"],
  "urls": ["All URLs found - fix broken ones like 'ude . my' to 'https://ude.my'"],
  "instructor": "Instructor name if shown",
  "duration": "Course duration if shown"
}

Rules:
1. Extract ALL text you see
2. Fix broken URLs (add https://, remove spaces)
3. Normalize dates to YYYY-MM-DD
4. Return ONLY the JSON object, no explanations"""
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            # Extract response
            result_text = response.choices[0].message.content
            
            # Parse JSON
            try:
                structured_data = json.loads(result_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, extract it from markdown
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    structured_data = json.loads(json_match.group())
                else:
                    structured_data = {}
            
            logger.info(f"[INFO] Mistral Vision API completed")
            logger.info(f"[INFO] Extracted: {structured_data.get('student_name')}, {structured_data.get('issuer')}")
            
            return {
                "success": True,
                "raw_text": result_text,
                "structured_data": structured_data,
                "confidence": 0.95
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Mistral Vision API failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "raw_text": "",
                "structured_data": {},
                "confidence": 0.0
            }
