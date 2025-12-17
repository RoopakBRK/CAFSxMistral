"""API Routes with Mistral OCR"""

from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os
import logging

from pipeline.complete_verifier import CompleteCertificateVerifier

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize verifier with Mistral OCR
_verifier = None

def get_verifier():
    global _verifier
    if _verifier is None:
        _verifier = CompleteCertificateVerifier()  # Uses Mistral OCR
    return _verifier

@router.post("/verify")
async def verify_certificate(file: UploadFile = File(...)):
    """Verify certificate using Mistral OCR"""
    
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(400, f"Invalid file type: {file.content_type}")
    
    tmp_path = None
    try:
        # Save temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Run verification with Mistral OCR
        verifier = get_verifier()
        result = await verifier.verify_certificate(tmp_path)
        
        return {
            "success": True,
            "filename": file.filename,
            "data": result
        }
    
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        raise HTTPException(500, f"Verification failed: {str(e)}")
    
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

@router.get("/health")
async def health():
    return {"status": "healthy"}
