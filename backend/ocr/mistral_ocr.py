"""
Mistral OCR with Smart PDF Handling
PDFs are processed at HIGH QUALITY to preserve text clarity
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
    """Mistral OCR with high-quality PDF conversion"""
    
    def __init__(self):
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found")
        
        self.client = Mistral(api_key=api_key)
        logger.info("[INFO] Mistral OCR initialized")
    
    def _convert_pdf_to_image(self, pdf_path: str) -> str:
        """
        Convert PDF to HIGH QUALITY image
        Uses 300 DPI to preserve text clarity
        """
        try:
            from pdf2image import convert_from_path
            import tempfile
            
            logger.info("[INFO] Converting PDF to high-quality image (300 DPI)...")
            
            # Convert at 300 DPI (print quality) - NOT 72 DPI (screen quality)
            images = convert_from_path(
                pdf_path, 
                dpi=300,  # HIGH QUALITY - preserves fine details
                first_page=1, 
                last_page=1,
                fmt='png'  # PNG for lossless compression
            )
            
            if not images:
                raise ValueError("PDF conversion failed")
            
            # Save as PNG (lossless)
            temp_image = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            images[0].save(temp_image.name, 'PNG', quality=100)
            temp_image.close()
            
            logger.info(f"[INFO] PDF converted to high-quality PNG: {temp_image.name}")
            return temp_image.name
            
        except ImportError:
            raise ImportError("pdf2image not installed. Run: pip install pdf2image")
        except Exception as e:
            raise Exception(f"PDF conversion failed: {e}")
    
    def extract_certificate_data(self, image_path: str) -> Dict[str, Any]:
        """
        Extract certificate data with smart format handling
        
        PDFs: Converted at 300 DPI for maximum quality
        Images: Used directly
        """
        
        file_ext = image_path.lower().split('.')[-1]
        temp_image_path = None
        original_was_pdf = False
        
        # Convert PDF to high-quality image
        if file_ext == 'pdf':
            original_was_pdf = True
            try:
                temp_image_path = self._convert_pdf_to_image(image_path)
                image_path = temp_image_path
                file_ext = 'png'
            except Exception as e:
                logger.error(f"[ERROR] PDF conversion failed: {e}")
                return {
                    "success": False,
                    "error": f"PDF conversion failed: {str(e)}",
                    "structured_data": {},
                    "confidence": 0.0
                }
        
        # Read and encode image
        try:
            with open(image_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode()
        finally:
            # Clean up temp file
            if temp_image_path and os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
        
        mime_type = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png'
        }.get(file_ext, 'image/jpeg')
        
        try:
            logger.info(f"[INFO] Running Mistral OCR (source: {'PDF' if original_was_pdf else 'Image'})...")
            
            response = self.client.chat.complete(
                model="pixtral-12b-2409",
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
                                "text": """Extract ALL information from this certificate image. Pay EXTRA attention to:
- URLs (carefully read each character, underlined text can be tricky)
- Certificate IDs (numbers/letters can look similar: 0/O, 1/I, 7/Z, 5/S)
- Dates (format as YYYY-MM-DD)

Return JSON:
{
  "student_name": "Full name of recipient",
  "issuer": "Organization (Udemy, Coursera, edX, LinkedIn, Google, IBM, Microsoft, etc.)",
  "course_name": "Full course/program name",
  "completion_date": "YYYY-MM-DD format",
  "certificate_ids": ["All IDs/reference numbers/serial numbers found"],
  "urls": ["All URLs - fix broken ones like 'ude . my' to 'https://ude.my', 'coursera . org' to 'https://coursera.org'"],
  "instructor": "Instructor/teacher name",
  "duration": "Course duration (e.g., '44.5 hours', '6 weeks')"
}

CRITICAL: 
- Read URLs character-by-character carefully
- Common OCR mistakes: 7↔Z, 0↔O, 1↔I↔l, 5↔S, 8↔B
- If you see underlined text, be extra careful
- Fix broken URLs by removing spaces: "ude . my" → "https://ude.my"

Return ONLY valid JSON."""
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            
            try:
                structured_data = json.loads(result_text)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                structured_data = json.loads(json_match.group()) if json_match else {}
            
            logger.info(f"[INFO] OCR complete: {structured_data.get('student_name')}, {structured_data.get('issuer')}")
            logger.info(f"[INFO] IDs extracted: {structured_data.get('certificate_ids')}")
            logger.info(f"[INFO] URLs extracted: {structured_data.get('urls')}")
            
            return {
                "success": True,
                "structured_data": structured_data,
                "confidence": 0.95,
                "source_format": "PDF" if original_was_pdf else "Image"
            }
            
        except Exception as e:
            logger.error(f"[ERROR] OCR failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "structured_data": {},
                "confidence": 0.0
            }
