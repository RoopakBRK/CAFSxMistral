"""
Complete Verification Pipeline
Uses: Mistral OCR + Mistral Forensics + Verification
"""

import asyncio
from typing import Dict, Any
from ocr.mistral_ocr import MistralOCR
from forensics.mistral_forensics import MistralForensics
from verification.service import get_verification_service
import logging

logger = logging.getLogger(__name__)


class CompleteCertificateVerifier:
    """End-to-end verification with OCR + Forensics"""
    
    def __init__(self):
        self.ocr = MistralOCR()
        self.forensics = MistralForensics()
        self.verifier = get_verification_service()
        
        logger.info("[INFO] Pipeline initialized: OCR + Forensics + Verification")
    
    async def verify_certificate(self, image_path: str) -> Dict[str, Any]:
        """Complete verification with forensics"""
        
        # Step 1: OCR + Extraction
        logger.info("[1/3] Running OCR...")
        ocr_result = self.ocr.extract_certificate_data(image_path)
        
        if not ocr_result["success"]:
            return {
                'success': False,
                'error': ocr_result.get("error", "OCR failed"),
                'stage': 'ocr'
            }
        
        structured_data = ocr_result["structured_data"]
        
        # Step 2: Forensics Analysis
        logger.info("[2/3] Running forensics analysis...")
        forensics_result = self.forensics.analyze_certificate(image_path)
        
        if not forensics_result["success"]:
            logger.warning("[WARNING] Forensics failed, continuing anyway")
        
        forensics_data = forensics_result.get("forensics", {})
        
        # Step 3: Web Verification
        logger.info("[3/3] Verifying with issuer...")
        
        try:
            extraction_result = self.verifier.verify_from_evidence(structured_data)
            verification_result = await self.verifier.verify(extraction_result)
        except Exception as e:
            logger.error(f"[ERROR] Verification failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'stage': 'verification',
                'extracted_data': structured_data,
                'forensics': forensics_data
            }
        
        logger.info(f"[INFO] Complete: Verified={verification_result.is_verified}, Risk={forensics_data.get('is_high_risk')}")
        
        return {
            'success': True,
            'ocr': {
                'engine': 'mistral-vision',
                'confidence': round(ocr_result["confidence"] * 100, 2)
            },
            'extracted_data': {
                'student_name': structured_data.get('student_name'),
                'issuer': structured_data.get('issuer'),
                'course_name': structured_data.get('course_name'),
                'completion_date': structured_data.get('completion_date'),
                'certificate_ids': structured_data.get('certificate_ids', []),
                'urls': structured_data.get('urls', []),
                'instructor': structured_data.get('instructor'),
                'duration': structured_data.get('duration')
            },
            'forensics': forensics_data,
            'verification': {
                'is_verified': verification_result.is_verified,
                'trusted_domain': verification_result.trusted_domain,
                'confidence_score': round(verification_result.confidence_score * 100, 2),
                'method': verification_result.method,
                'message': verification_result.message,
                'verification_url': verification_result.verification_url
            }
        }
