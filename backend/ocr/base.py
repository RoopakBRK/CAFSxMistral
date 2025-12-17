"""Base interface for all OCR engines."""

from abc import ABC, abstractmethod
import numpy as np
from core.models import OCRResult

class BaseOCR(ABC):
    """Abstract base class for OCR engines."""
    
    @abstractmethod
    def extract(self, image: np.ndarray, page_number: int) -> OCRResult:
        """Extract text from an image."""
        pass
    
    def get_name(self) -> str:
        """Return human-readable name of this engine"""
        return self.__class__.__name__
