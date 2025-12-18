"""API Routes with Triple OCR Verification"""

from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os
import logging

from pipeline.complete_verifier import CompleteCertificateVerifier

router = APIRouter()
logger = logging.getLogger(__name__)

_verifier = None

def get_verifier():
    global _verifier
    if _verifier is None:
        _verifier = CompleteCertificateVerifier()
    return _verifier

@router.post("/verify")
async def verify_certificate(file: UploadFile = File(...)):
    """Verify with ALL 3 OCR engines (EasyOCR + Mistral + Tesseract)"""
    
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(400, f"Invalid file type: {file.content_type}")
    
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        verifier = get_verifier()
        result = await verifier.verify_certificate(tmp_path)
        
        best_result = result.get('best_result', {})
        
        return {
            "success": True,
            "filename": file.filename,
            "data": {
                "ocr": {
                    "engines_used": ["easyocr", "mistral", "tesseract"],
                    "all_results": result.get('ocr_results', [])
                },
                "extracted_data": best_result.get('extracted_data', {}),
                "forensics": result.get('forensics', {}),
                "verification": best_result.get('verification', {}),
                "all_verification_attempts": result.get('verification_attempts', []),
                "summary": result.get('summary', {})
            }
        }
    
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        raise HTTPException(500, f"Verification failed: {str(e)}")
    
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

@router.get("/health")
async def health():
    return {"status": "healthy", "ocr": "triple"}
