"""
Dual OCR System - Independent Results
Returns both EasyOCR and Mistral OCR results separately
"""

import logging
from typing import Dict, Any, List
from ocr.easy_ocr_simple import SimpleEasyOCR
from ocr.mistral_ocr_enhanced import EnhancedMistralOCR
from mistralai import Mistral
import os

logger = logging.getLogger(__name__)


class DualOCR:
    """Runs both OCR engines, returns both results independently"""
    
    def __init__(self):
        self.easy_ocr = SimpleEasyOCR()
        self.mistral_ocr = EnhancedMistralOCR()
        
        # Mistral client for structuring EasyOCR results
        api_key = os.getenv("MISTRAL_API_KEY")
        self.mistral_client = Mistral(api_key=api_key) if api_key else None
        
        logger.info("[INFO] Dual OCR initialized")
    
    def _structure_easy_ocr(self, raw_text: str) -> Dict[str, Any]:
        """Use Mistral to structure EasyOCR's raw text"""
        if not self.mistral_client or not raw_text:
            return {}
        
        try:
            import json
            response = self.mistral_client.chat.complete(
                model="mistral-large-latest",
                messages=[{
                    "role": "user",
                    "content": f"""Extract structured data from this certificate text:

{raw_text}

Return JSON:
{{
  "student_name": "Full name",
  "issuer": "Organization",
  "course_name": "Course name",
  "completion_date": "YYYY-MM-DD",
  "certificate_ids": ["All IDs"],
  "urls": ["All URLs - fix spaces like 'ude . my' to 'https://ude.my'"],
  "instructor": "Instructor",
  "duration": "Duration"
}}

Return ONLY JSON."""
                }],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"[ERROR] EasyOCR structuring failed: {e}")
            return {}
    
    async def extract_both(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Extract with both engines, return list of results
        
        Returns:
            [
                {
                    "engine": "easyocr",
                    "success": True,
                    "structured_data": {...},
                    "confidence": 0.85
                },
                {
                    "engine": "mistral",
                    "success": True,
                    "structured_data": {...},
                    "confidence": 0.95
                }
            ]
        """
        
        results = []
        
        # ===== EasyOCR =====
        logger.info("[OCR 1/2] Running EasyOCR...")
        easy_result = self.easy_ocr.extract_text(image_path)
        
        if easy_result.get("success"):
            raw_text = easy_result.get("raw_text", "")
            structured = self._structure_easy_ocr(raw_text)
            
            results.append({
                "engine": "easyocr",
                "success": True,
                "structured_data": structured,
                "confidence": easy_result.get("confidence", 0.0),
                "raw_text": raw_text[:500],  # First 500 chars for debugging
                "total_lines": easy_result.get("total_lines", 0)
            })
            
            logger.info(f"[INFO] EasyOCR: {structured.get('student_name')}, {structured.get('issuer')}")
        else:
            logger.warning("[WARNING] EasyOCR failed")
            results.append({
                "engine": "easyocr",
                "success": False,
                "error": easy_result.get("error", "Unknown error"),
                "structured_data": {},
                "confidence": 0.0
            })
        
        # ===== Mistral OCR =====
        logger.info("[OCR 2/2] Running Mistral OCR (2-pass)...")
        mistral_result = self.mistral_ocr.extract_certificate_data(image_path)
        
        if mistral_result.get("success"):
            structured = mistral_result.get("structured_data", {})
            
            results.append({
                "engine": "mistral",
                "success": True,
                "structured_data": structured,
                "confidence": mistral_result.get("confidence", 0.0),
                "passes_completed": mistral_result.get("passes_completed", 1)
            })
            
            logger.info(f"[INFO] Mistral: {structured.get('student_name')}, {structured.get('issuer')}")
        else:
            logger.warning("[WARNING] Mistral OCR failed")
            results.append({
                "engine": "mistral",
                "success": False,
                "error": mistral_result.get("error", "Unknown error"),
                "structured_data": {},
                "confidence": 0.0
            })
        
        logger.info(f"[DUAL OCR] Complete: {sum(1 for r in results if r['success'])}/2 engines succeeded")
        
        return results
