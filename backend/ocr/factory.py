"""Factory for creating OCR engines."""

from typing import Dict
from .base import BaseOCR
from .paddle_ocr import PaddleOCRWrapper
from .easy_ocr import EasyOCRWrapper


class OCRFactory:
    """Factory for creating OCR engine instances."""
    
    @staticmethod
    def create_paddle_ocr(use_gpu: bool = False) -> BaseOCR:
        """Create PaddleOCR instance."""
        return PaddleOCRWrapper()
    
    @staticmethod
    def create_easy_ocr(use_gpu: bool = False) -> BaseOCR:
        """Create EasyOCR instance."""
        return EasyOCRWrapper(languages=['en'], gpu=use_gpu)
    
    @staticmethod
    def create_all(use_gpu: bool = False) -> Dict[str, BaseOCR]:
        """Create all available OCR engines."""
        return {
            'paddle': OCRFactory.create_paddle_ocr(use_gpu),
            'easy': OCRFactory.create_easy_ocr(use_gpu)
        }
