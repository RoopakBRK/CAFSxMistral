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
    """Verify certificate using OCR + verification pipeline"""

    allowed_types = ["image/jpeg", "image/jpg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file.content_type}")

    tmp_path = None

    try:
        # -------------------------
        # Save uploaded file
        # -------------------------
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(file.filename)[1]
        ) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # -------------------------
        # Run verification
        # -------------------------
        verifier = get_verifier()
        result = await verifier.verify_certificate(tmp_path)

        best_result = result.get("best_result", {})

        response = {
            "success": True,
            "filename": file.filename,
            "data": {
                "ocr": {
                    "engines_used": ["easyocr", "mistral", "tesseract"],
                    "all_results": result.get("ocr_results", []),
                },
                "extracted_data": best_result.get("extracted_data", {}),
                "forensics": result.get("forensics", {}),
                "verification": best_result.get("verification", {}),
                "all_verification_attempts": result.get("verification_attempts", []),
                "summary": result.get("summary", {}),
            },
        }

        return response

    except Exception as e:
        logger.exception("Verification failed")
        raise HTTPException(
            status_code=500,
            detail=f"Verification failed: {str(e)}"
        )

    finally:
        # -------------------------
        # Save verification history (NON-BLOCKING)
        # -------------------------
        try:
            from database.models import get_history

            history = get_history()
            history.add_verification({
                "filename": file.filename,
                "extracted_data": response["data"]["extracted_data"]
                    if "response" in locals() else {},
                "verification": response["data"]["verification"]
                    if "response" in locals() else {},
                "forensics": response["data"]["forensics"]
                    if "response" in locals() else {},
            })
            logger.info("[INFO] Verification saved to history")

        except Exception as e:
            logger.warning(f"[WARNING] Failed to save verification history: {e}")

        # -------------------------
        # Cleanup temp file
        # -------------------------
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.get("/health")
async def health():
    return {"status": "healthy", "ocr": "triple"}

# ===== HISTORY ENDPOINTS =====
from database.models import get_history

@router.get("/history")
async def get_recent_history(limit: int = 10):
    """Get recent verification history"""
    try:
        history = get_history()
        verifications = history.get_recent(limit)
        
        return {
            "success": True,
            "count": len(verifications),
            "verifications": verifications
        }
    except Exception as e:
        logger.error(f"History fetch failed: {e}")
        raise HTTPException(500, f"Failed to fetch history: {str(e)}")

@router.get("/history/stats")
async def get_verification_stats():
    """Get verification statistics"""
    try:
        history = get_history()
        stats = history.get_stats()
        
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Stats fetch failed: {e}")
        raise HTTPException(500, f"Failed to fetch stats: {str(e)}")

@router.get("/history/search")
async def search_history(q: str, limit: int = 20):
    """Search verification history"""
    try:
        history = get_history()
        results = history.search(q, limit)
        
        return {
            "success": True,
            "query": q,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"History search failed: {e}")
        raise HTTPException(500, f"Failed to search history: {str(e)}")
