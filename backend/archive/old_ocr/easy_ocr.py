"""EasyOCR wrapper."""

import easyocr
import numpy as np
from typing import List, Tuple

from .base import BaseOCR
from .exceptions import OCRInitializationError, OCRExtractionError
from core.models import OCRResult, OCREngine


class EasyOCRWrapper(BaseOCR):
    """Wrapper around EasyOCR."""
    
    def __init__(self, languages: List[str] = None, gpu: bool = False):
        """Initialize EasyOCR."""
        if languages is None:
            languages = ['en']
        
        try:
            self.engine = easyocr.Reader(languages, gpu=gpu)
            print(f"✅ EasyOCR initialized (GPU: {gpu}, Languages: {languages})")
        except Exception as e:
            raise OCRInitializationError(f"Failed to initialize EasyOCR: {e}")
    
    def extract(self, image: np.ndarray, page_number: int) -> OCRResult:
        """Extract text from image using EasyOCR."""
        if image is None or image.size == 0:
            raise OCRExtractionError("Invalid image: empty or None")
        
        try:
            result = self.engine.readtext(image)
            lines, confidences = self._parse_easy_output(result)
            avg_confidence = self._calculate_average_confidence(confidences)
            
            return OCRResult(
                engine=OCREngine.EASY,
                raw_lines=lines,
                confidence=avg_confidence,
                page_number=page_number
            )
        except Exception as e:
            raise OCRExtractionError(f"EasyOCR extraction failed: {e}")
    
    def _parse_easy_output(self, result: List) -> Tuple[List[str], List[float]]:
        """Parse EasyOCR's output format."""
        lines = []
        confidences = []
        
        for detection in result:
            bbox = detection[0]
            text = detection[1]
            confidence = detection[2]
            
            lines.append(text)
            confidences.append(float(confidence))
        
        return lines, confidences
    
    def _calculate_average_confidence(self, confidences: List[float]) -> float:
        """Calculate average confidence score."""
        if not confidences:
            return 0.0
        return sum(confidences) / len(confidences)
