"""Custom exceptions for OCR operations."""

class OCRException(Exception):
    """Base exception for all OCR-related errors"""
    pass

class OCRInitializationError(OCRException):
    """Raised when OCR engine fails to initialize"""
    pass

class OCRExtractionError(OCRException):
    """Raised when text extraction fails"""
    pass

class ImageLoadError(OCRException):
    """Raised when image cannot be loaded or is invalid"""
    pass
