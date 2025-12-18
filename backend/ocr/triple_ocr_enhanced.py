"""
Enhanced Triple OCR with PaddleOCR Fallback
Uses SimplePaddleOCR wrapper for correct v3.3.2 format handling
"""

import logging
from typing import Dict, Any, List
from ocr.easy_ocr_simple import SimpleEasyOCR
from ocr.mistral_ocr_enhanced import EnhancedMistralOCR
from ocr.tesseract_ocr import TesseractOCR
from ocr.paddle_ocr_simple import SimplePaddleOCR
from mistralai import Mistral
import os
import re

logger = logging.getLogger(__name__)


class TripleOCREnhanced:
    """Runs 3 OCR engines, with PaddleOCR fallback when verification fails"""
    
    def __init__(self):
        self.easy_ocr = SimpleEasyOCR()
        self.mistral_ocr = EnhancedMistralOCR()
        self.tesseract_ocr = TesseractOCR()
        
        # Initialize PaddleOCR lazily
        self.paddle_ocr = None
        
        # Mistral client for structuring
        api_key = os.getenv("MISTRAL_API_KEY")
        self.mistral_client = Mistral(api_key=api_key) if api_key else None
        
        logger.info("[INFO] Enhanced Triple OCR initialized (+ PaddleOCR fallback)")
    
    def _init_paddle_ocr(self):
        """Lazy load PaddleOCR"""
        if self.paddle_ocr is None:
            try:
                self.paddle_ocr = SimplePaddleOCR()
                logger.info("[INFO] PaddleOCR fallback ready")
            except Exception as e:
                logger.error(f"[ERROR] PaddleOCR init failed: {e}")
                self.paddle_ocr = False
    
    def _extract_and_validate_urls(self, structured_data: Dict[str, Any]) -> List[str]:
        """Extract and validate URLs"""
        urls = structured_data.get('urls', [])
        
        if isinstance(urls, dict):
            urls = list(urls.values())
        
        valid_urls = []
        url_pattern = r'https?://(?:[a-zA-Z0-9]|[-._~:/?#\[\]@!$&\'()*+,;=])+'
        
        for url in urls:
            if not url:
                continue
            
            if re.match(url_pattern, str(url), re.IGNORECASE):
                if any(tld in str(url).lower() for tld in ['.com', '.org', '.edu', '.net', '.gov', '.io']):
                    valid_urls.append(url)
        
        return valid_urls
    
    def _has_valid_verification_url(self, results: List[Dict[str, Any]]) -> bool:
        """Check if any result has valid URLs"""
        for result in results:
            if not result.get('success'):
                continue
            
            structured = result.get('structured_data', {})
            valid_urls = self._extract_and_validate_urls(structured)
            
            if valid_urls:
                logger.info(f"[INFO] {result['engine']} found {len(valid_urls)} valid URL(s)")
                return True
        
        logger.warning("[WARNING] No valid URLs in any OCR result")
        return False
    
    def _structure_raw_text(self, raw_text: str, engine_name: str) -> Dict[str, Any]:
        """Use Mistral to structure raw text"""
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
  "certificate_ids": ["All IDs - carefully: 7 not Z, 0 not O, J not missing"],
  "urls": ["All URLs - for Coursera use full format: https://www.coursera.org/account/accomplishments/verify/{{ID}}"],
  "instructor": "Instructor",
  "duration": "Duration"
}}

CRITICAL:
- Read IDs character-by-character: 7≠Z, 0≠O, 1≠I, J≠missing
- For Coursera, use FULL URL: https://www.coursera.org/account/accomplishments/verify/{{ID}}
- Fix spaces in URLs

Return ONLY JSON."""
                }],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"[ERROR] Structuring failed: {e}")
            return {}
    
    def _run_paddle_fallback(self, image_path: str) -> Dict[str, Any]:
        """Run PaddleOCR as fallback"""
        self._init_paddle_ocr()
        
        if not self.paddle_ocr or self.paddle_ocr is False:
            return {
                "engine": "paddleocr",
                "success": False,
                "error": "PaddleOCR not available",
                "structured_data": {},
                "confidence": 0.0
            }
        
        logger.info("[FALLBACK] Running PaddleOCR...")
        
        try:
            paddle_result = self.paddle_ocr.extract_text(image_path)
            
            if not paddle_result.get("success"):
                logger.error(f"[FALLBACK FAILED] {paddle_result.get('error')}")
                return {
                    "engine": "paddleocr",
                    "success": False,
                    "error": paddle_result.get("error"),
                    "structured_data": {},
                    "confidence": 0.0,
                    "is_fallback": True
                }
            
            raw_text = paddle_result.get("raw_text", "")
            logger.info(f"[FALLBACK] PaddleOCR extracted: {len(raw_text)} chars")
            logger.info(f"[FALLBACK] Preview: {raw_text[:200]}")
            
            # Structure the text
            structured = self._structure_raw_text(raw_text, "PaddleOCR")
            
            if structured:
                logger.info(f"[FALLBACK] Structured: {structured.get('student_name')}, {structured.get('issuer')}")
                urls = self._extract_and_validate_urls(structured)
                if urls:
                    logger.info(f"[FALLBACK SUCCESS] ✅ PaddleOCR found {len(urls)} URL(s): {urls}")
                else:
                    logger.warning("[FALLBACK] ⚠️ PaddleOCR extracted data but no valid URLs")
            
            return {
                "engine": "paddleocr",
                "success": True,
                "structured_data": structured,
                "confidence": paddle_result.get("confidence", 0.0),
                "raw_text_preview": raw_text[:300],
                "total_lines": paddle_result.get("total_lines", 0),
                "is_fallback": True
            }
            
        except Exception as e:
            logger.error(f"[FALLBACK ERROR] {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "engine": "paddleocr",
                "success": False,
                "error": str(e),
                "structured_data": {},
                "confidence": 0.0,
                "is_fallback": True
            }
    
    async def extract_all(self, image_path: str) -> List[Dict[str, Any]]:
        """Extract with all engines + PaddleOCR fallback if needed"""
        
        results = []
        
        # === ENGINE 1: EasyOCR ===
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
                "error": easy_result.get("error"),
                "structured_data": {},
                "confidence": 0.0
            })
        
        # === ENGINE 2: Mistral ===
        logger.info("[OCR 2/3] Running Mistral OCR...")
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
            logger.warning("[WARNING] Mistral failed")
            results.append({
                "engine": "mistral",
                "success": False,
                "error": mistral_result.get("error"),
                "structured_data": {},
                "confidence": 0.0
            })
        
        # === ENGINE 3: Tesseract ===
        logger.info("[OCR 3/3] Running Tesseract...")
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
                "error": tesseract_result.get("error"),
                "structured_data": {},
                "confidence": 0.0
            })
        
        successful = sum(1 for r in results if r['success'])
        logger.info(f"[TRIPLE OCR] {successful}/3 engines succeeded")
        
        # === PADDLEOCR FALLBACK ===
        if not self._has_valid_verification_url(results):
            logger.warning("="*80)
            logger.warning("[CRITICAL] NO VALID URLS - ACTIVATING PADDLEOCR FALLBACK")
            logger.warning("="*80)
            
            paddle_result = self._run_paddle_fallback(image_path)
            results.append(paddle_result)
            
            if paddle_result['success']:
                successful += 1
        else:
            logger.info("[INFO] Valid URLs found - PaddleOCR not needed")
        
        logger.info(f"[FINAL] {successful}/{len(results)} total engines succeeded")
        
        return results
