"""
Triple OCR System
Runs EasyOCR + Mistral + Tesseract in parallel
"""

import logging
from typing import Dict, Any, List
from ocr.easy_ocr_simple import SimpleEasyOCR
from ocr.mistral_ocr_enhanced import EnhancedMistralOCR
from ocr.tesseract_ocr import TesseractOCR
from mistralai import Mistral
import os

logger = logging.getLogger(__name__)


class TripleOCR:
    """Runs 3 OCR engines, returns all results independently"""
    
    def __init__(self):
        self.easy_ocr = SimpleEasyOCR()
        self.mistral_ocr = EnhancedMistralOCR()
        self.tesseract_ocr = TesseractOCR()
        
        # Mistral client for structuring raw text
        api_key = os.getenv("MISTRAL_API_KEY")
        self.mistral_client = Mistral(api_key=api_key) if api_key else None
        
        logger.info("[INFO] Triple OCR initialized (EasyOCR + Mistral + Tesseract)")
    
    def _structure_raw_text(self, raw_text: str, engine_name: str) -> Dict[str, Any]:
        """Use Mistral to structure raw OCR text"""
        if not self.mistral_client or not raw_text:
            return {}
        
        try:
            import json
            response = self.mistral_client.chat.complete(
                model="mistral-large-latest",
                messages=[{
                    "role": "user",
                    "content": f"""Extract structured data from this certificate text (from {engine_name}):

{raw_text}

Return JSON:
{{
  "student_name": "Full name",
  "issuer": "Organization",
  "course_name": "Course name",
  "completion_date": "YYYY-MM-DD",
  "certificate_ids": ["All IDs - be careful: 7 not Z, 0 not O"],
  "urls": ["All URLs - fix spaces like 'ude . my' to 'https://ude.my'"],
  "instructor": "Instructor",
  "duration": "Duration"
}}

CRITICAL: Read certificate IDs and URLs character-by-character carefully.
Common OCR mistakes: 7↔Z, 0↔O, 1↔I, 5↔S, 8↔B

Return ONLY JSON."""
                }],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"[ERROR] Structuring {engine_name} failed: {e}")
            return {}
    
    async def extract_all(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Extract with all 3 engines, return list of results
        
        Returns:
            [
                {"engine": "easyocr", "success": True, "structured_data": {...}},
                {"engine": "mistral", "success": True, "structured_data": {...}},
                {"engine": "tesseract", "success": True, "structured_data": {...}}
            ]
        """
        
        results = []
        
        # ===== ENGINE 1: EasyOCR =====
        logger.info("[OCR 1/3] Running EasyOCR...")
        easy_result = self.easy_ocr.extract_text(image_path)
        
        if easy_result.get("success"):
            raw_text = easy_result.get("raw_text", "")
            structured = self._structure_raw_text(raw_text, "EasyOCR")
            
            results.append({
                "engine": "easyocr",
                "success": True,
                "structured_data": structured,
                "confidence": easy_result.get("confidence", 0.0),
                "raw_text_preview": raw_text[:300],
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
        
        # ===== ENGINE 2: Mistral (2-pass) =====
        logger.info("[OCR 2/3] Running Mistral OCR (2-pass zoom)...")
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
        
        # ===== ENGINE 3: Tesseract =====
        logger.info("[OCR 3/3] Running Tesseract OCR...")
        tesseract_result = self.tesseract_ocr.extract_text(image_path)
        
        if tesseract_result.get("success"):
            raw_text = tesseract_result.get("raw_text", "")
            structured = self._structure_raw_text(raw_text, "Tesseract")
            
            results.append({
                "engine": "tesseract",
                "success": True,
                "structured_data": structured,
                "confidence": tesseract_result.get("confidence", 0.0),
                "raw_text_preview": raw_text[:300],
                "total_words": tesseract_result.get("total_words", 0)
            })
            
            logger.info(f"[INFO] Tesseract: {structured.get('student_name')}, {structured.get('issuer')}")
        else:
            logger.warning("[WARNING] Tesseract failed")
            results.append({
                "engine": "tesseract",
                "success": False,
                "error": tesseract_result.get("error", "Unknown error"),
                "structured_data": {},
                "confidence": 0.0
            })
        
        successful = sum(1 for r in results if r['success'])
        logger.info(f"[TRIPLE OCR] Complete: {successful}/3 engines succeeded")
        
        return results
