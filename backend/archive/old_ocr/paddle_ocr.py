"""PaddleOCR wrapper - compatible with PaddleOCR 3.3.2"""
from paddleocr import PaddleOCR
import numpy as np
from typing import List, Tuple
from .base import BaseOCR
from .exceptions import OCRInitializationError, OCRExtractionError
from core.models import OCRResult, OCREngine

class PaddleOCRWrapper(BaseOCR):
    def __init__(self):
        try:
            # Use new parameter name (use_angle_cls is deprecated)
            self.engine = PaddleOCR(lang='en')
            print("✅ PaddleOCR initialized (v3.3.2)")
        except Exception as e:
            raise OCRInitializationError(f"Failed: {e}")
    
    def extract(self, image: np.ndarray, page_number: int) -> OCRResult:
        if image is None or image.size == 0:
            raise OCRExtractionError("Invalid image")
        
        try:
            # Don't pass cls parameter (deprecated)
            result = self.engine.ocr(image)
            lines, confidences = self._parse_332_format(result)
            
            print(f"   📊 PaddleOCR detected {len(lines)} lines")
            
            return OCRResult(
                engine=OCREngine.PADDLE,
                raw_lines=lines,
                confidence=sum(confidences)/len(confidences) if confidences else 0.0,
                page_number=page_number
            )
        except Exception as e:
            raise OCRExtractionError(f"Failed: {e}")
    
    def _parse_332_format(self, result) -> Tuple[List[str], List[float]]:
        """Parse PaddleOCR 3.3.2 format (dict-like OCRResult object)."""
        lines = []
        confidences = []
        
        if not result or len(result) == 0:
            return lines, confidences
        
        # result[0] is an OCRResult object (acts like a dict)
        ocr_result = result[0]
        
        # Access as dictionary
        try:
            # rec_text contains the recognized text
            if 'rec_texts' in ocr_result:
                texts = ocr_result['rec_texts']
                scores = ocr_result.get('rec_scores', [])
                
                if isinstance(texts, list):
                    for i, text in enumerate(texts):
                        text = str(text).strip()
                        if text:
                            lines.append(text)
                            conf = float(scores[i]) if i < len(scores) else 0.0
                            confidences.append(conf)
        except Exception as e:
            print(f"   ⚠️  Parse error: {e}")
        
        return lines, confidences
