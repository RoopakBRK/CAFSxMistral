"""Test OCR wrappers - show FULL output"""

import cv2
import numpy as np
import os
from ocr.factory import OCRFactory


def load_image(file_path):
    """Load image from file."""
    if not os.path.exists(file_path):
        return None
    
    if file_path.endswith('.pdf'):
        try:
            from pdf2image import convert_from_path
            print(f"📄 Converting PDF to image...")
            pages = convert_from_path(file_path, first_page=1, last_page=1)
            img = np.array(pages[0])
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            return img
        except Exception as e:
            print(f"❌ Failed to load PDF: {e}")
            return None
    else:
        return cv2.imread(file_path)


def test_with_real_certificate():
    """Test with your actual certificate - FULL OUTPUT."""
    print("\n🎓 Testing with REAL certificate...\n")
    
    cert_files = [
        'sample_cert.pdf',
        'sample_cert.jpg', 
        'sample_cert.png',
        'certificate.pdf',
        'certificate.jpg',
        'certificate.png'
    ]
    
    image = None
    used_file = None
    
    for cert_file in cert_files:
        if os.path.exists(cert_file):
            print(f"📁 Found: {cert_file}")
            image = load_image(cert_file)
            if image is not None:
                used_file = cert_file
                break
    
    if image is None:
        print("❌ No certificate found!")
        return
    
    print(f"✅ Loaded: {used_file}")
    print(f"   Size: {image.shape[1]}x{image.shape[0]} pixels\n")
    
    # Test PaddleOCR
    print("="*60)
    print("🔍 PADDLEOCR RESULTS")
    print("="*60)
    paddle = OCRFactory.create_paddle_ocr()
    paddle_result = paddle.extract(image, page_number=0)
    
    print(f"\nConfidence: {paddle_result.confidence:.2%}")
    print(f"Total lines: {len(paddle_result.raw_lines)}\n")
    print("📄 ALL EXTRACTED TEXT:")
    for i, line in enumerate(paddle_result.raw_lines, 1):
        print(f"   {i:2d}. {line}")
    
    # Test EasyOCR
    print("\n" + "="*60)
    print("🔍 EASYOCR RESULTS")
    print("="*60)
    easy = OCRFactory.create_easy_ocr()
    easy_result = easy.extract(image, page_number=0)
    
    print(f"\nConfidence: {easy_result.confidence:.2%}")
    print(f"Total lines: {len(easy_result.raw_lines)}\n")
    print("📄 ALL EXTRACTED TEXT:")
    for i, line in enumerate(easy_result.raw_lines, 1):
        print(f"   {i:2d}. {line}")
    
    # Side-by-side comparison
    print("\n" + "="*60)
    print("📊 COMPARISON")
    print("="*60)
    print(f"\nPaddleOCR: {len(paddle_result.raw_lines)} lines ({paddle_result.confidence:.2%} confidence)")
    print(f"EasyOCR:   {len(easy_result.raw_lines)} lines ({easy_result.confidence:.2%} confidence)")
    
    # Find unique lines
    paddle_set = set(paddle_result.raw_lines)
    easy_set = set(easy_result.raw_lines)
    
    only_paddle = paddle_set - easy_set
    only_easy = easy_set - paddle_set
    
    if only_paddle:
        print(f"\n📌 Only in PaddleOCR ({len(only_paddle)} unique):")
        for line in list(only_paddle)[:5]:
            print(f"   - {line}")
    
    if only_easy:
        print(f"\n📌 Only in EasyOCR ({len(only_easy)} unique):")
        for line in list(only_easy)[:5]:
            print(f"   - {line}")
    
    print("\n" + "="*60)
    print("✅ BOTH ENGINES WORKING!")
    print("="*60)
    
    return paddle_result, easy_result


if __name__ == "__main__":
    paddle_result, easy_result = test_with_real_certificate()
