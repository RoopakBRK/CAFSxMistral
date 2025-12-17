"""
Pre-load OCR models at server startup
Models stay in memory for fast requests
"""
import logging
from ocr.factory import OCRFactory

logger = logging.getLogger(__name__)

# Global model instances (loaded once, reused for all requests)
_paddle_ocr = None
_easy_ocr = None
_models_loaded = False


def load_ocr_models():
    """
    Load OCR models once at startup.
    This takes 5-7 minutes but only happens ONCE.
    """
    global _paddle_ocr, _easy_ocr, _models_loaded
    
    if _models_loaded:
        logger.info("[STARTUP] Models already loaded, skipping")
        return
    
    logger.info("[STARTUP] ========================================")
    logger.info("[STARTUP] Loading OCR models (one-time setup)")
    logger.info("[STARTUP] This takes 5-7 minutes on first start")
    logger.info("[STARTUP] ========================================")
    
    # Load EasyOCR (fast - 10 seconds)
    logger.info("[STARTUP] Loading EasyOCR...")
    try:
        _easy_ocr = OCRFactory.create_easy_ocr()
        logger.info("[STARTUP] ✅ EasyOCR ready")
    except Exception as e:
        logger.error(f"[STARTUP] ❌ EasyOCR failed: {e}")
    
    # Load PaddleOCR (slow - 5 minutes)
    logger.info("[STARTUP] Loading PaddleOCR (this will take ~5 minutes)...")
    try:
        _paddle_ocr = OCRFactory.create_paddle_ocr()
        logger.info("[STARTUP] ✅ PaddleOCR ready")
    except Exception as e:
        logger.error(f"[STARTUP] ❌ PaddleOCR failed: {e}")
    
    _models_loaded = True
    logger.info("[STARTUP] ========================================")
    logger.info("[STARTUP] ✅ All OCR models loaded and ready!")
    logger.info("[STARTUP] ========================================")


def get_ocr_models():
    """
    Get pre-loaded OCR models.
    If not loaded yet, load them now.
    """
    global _paddle_ocr, _easy_ocr, _models_loaded
    
    if not _models_loaded:
        load_ocr_models()
    
    return _paddle_ocr, _easy_ocr
