"""
Complete Verification Pipeline
Tries ALL 3 OCR results - if ANY verifies, certificate is verified
"""

import asyncio
from typing import Dict, Any, List
from ocr.triple_ocr import TripleOCR
from forensics.mistral_forensics import MistralForensics
from verification.service import get_verification_service
import logging

logger = logging.getLogger(__name__)


class CompleteCertificateVerifier:
    """Verification with triple OCR - tries all 3 independently"""
    
    def __init__(self):
        self.ocr = TripleOCR()
        self.forensics = MistralForensics()
        self.verifier = get_verification_service()
        
        logger.info("[INFO] Pipeline: Triple OCR (EasyOCR + Mistral + Tesseract)")
    
    async def verify_certificate(self, image_path: str) -> Dict[str, Any]:
        """
        Complete verification with ALL 3 OCR engines
        If ANY result verifies, certificate is verified
        """
        
        # Step 1: Run ALL 3 OCR engines
        logger.info("[1/3] Running ALL 3 OCR engines in parallel...")
        ocr_results = await self.ocr.extract_all(image_path)
        
        # Check if at least one succeeded
        successful_results = [r for r in ocr_results if r.get("success")]
        
        if not successful_results:
            return {
                'success': False,
                'error': 'All 3 OCR engines failed',
                'stage': 'ocr',
                'ocr_results': ocr_results
            }
        
        logger.info(f"[INFO] {len(successful_results)}/3 OCR engines succeeded")
        
        # Step 2: Forensics
        logger.info("[2/3] Running forensics...")
        forensics_result = self.forensics.analyze_certificate(image_path)
        forensics_data = forensics_result.get("forensics", {})
        
        # Step 3: Try verification with EACH OCR result
        logger.info("[3/3] Verifying with EACH OCR result...")
        
        verification_attempts = []
        
        for idx, ocr_result in enumerate(successful_results):
            engine = ocr_result["engine"]
            structured_data = ocr_result.get("structured_data", {})
            
            logger.info(f"[VERIFY {idx+1}/{len(successful_results)}] Trying {engine.upper()}...")
            logger.info(f"  - Name: {structured_data.get('student_name')}")
            logger.info(f"  - IDs: {structured_data.get('certificate_ids')}")
            logger.info(f"  - URLs: {structured_data.get('urls')}")
            
            try:
                # Convert to verification format
                extraction_result = self.verifier.verify_from_evidence(structured_data)
                
                # Attempt verification
                verification_result = await self.verifier.verify(extraction_result)
                
                verification_attempts.append({
                    "engine": engine,
                    "extracted_data": structured_data,
                    "verification": {
                        "is_verified": verification_result.is_verified,
                        "trusted_domain": verification_result.trusted_domain,
                        "confidence_score": round(verification_result.confidence_score * 100, 2),
                        "method": verification_result.method,
                        "message": verification_result.message,
                        "verification_url": verification_result.verification_url
                    },
                    "ocr_confidence": round(ocr_result["confidence"] * 100, 2)
                })
                
                status = "✅ VERIFIED" if verification_result.is_verified else "❌ UNVERIFIED"
                logger.info(f"  - Result: {status} (Confidence: {verification_result.confidence_score:.2%})")
                
            except Exception as e:
                logger.error(f"[ERROR] {engine.upper()} verification failed: {e}")
                verification_attempts.append({
                    "engine": engine,
                    "extracted_data": structured_data,
                    "error": str(e),
                    "verification": {
                        "is_verified": False,
                        "message": f"Verification error: {str(e)}"
                    }
                })
        
        # Determine final verdict: VERIFIED if ANY attempt succeeded
        verified_attempts = [a for a in verification_attempts if a.get("verification", {}).get("is_verified")]
        
        is_verified = len(verified_attempts) > 0
        
        # Pick best result
        if verified_attempts:
            best_attempt = max(verified_attempts, key=lambda x: x.get("verification", {}).get("confidence_score", 0))
            final_verdict = "VERIFIED"
            final_message = f"✅ Verified via {best_attempt['engine'].upper()}: {best_attempt['verification']['message']}"
        else:
            best_attempt = max(verification_attempts, key=lambda x: x.get("verification", {}).get("confidence_score", 0))
            final_verdict = "UNVERIFIED"
            final_message = f"❌ Could not verify with any OCR result. Best: {best_attempt['engine'].upper()} ({best_attempt.get('verification', {}).get('confidence_score', 0)}%)"
        
        logger.info(f"[FINAL] {final_verdict}: {len(verified_attempts)}/{len(verification_attempts)} engines verified")
        
        return {
            'success': True,
            'final_verdict': final_verdict,
            'is_verified': is_verified,
            'verification_attempts': verification_attempts,
            'best_result': best_attempt,
            'ocr_results': ocr_results,
            'forensics': forensics_data,
            'summary': {
                'total_ocr_engines': 3,
                'successful_ocr': len(successful_results),
                'verification_attempts': len(verification_attempts),
                'verified_count': len(verified_attempts),
                'final_message': final_message
            }
        }
