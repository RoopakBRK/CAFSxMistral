"""Test full extraction - see everything Mistral finds"""

import cv2
import os
import json
from ocr.factory import OCRFactory
from reasoning.mistral_agent import MistralReasoning


def test_full_extraction():
    """Extract ALL data from certificate."""
    
    print("="*60)
    print("FULL EXTRACTION TEST")
    print("="*60)
    
    # Load image
    cert_file = 'sample_cert.jpg'
    if not os.path.exists(cert_file):
        print("❌ sample_cert.jpg not found!")
        return
    
    image = cv2.imread(cert_file)
    
    # Run OCR
    print("\n1. Running OCR...")
    easy = OCRFactory.create_easy_ocr()
    ocr_result = easy.extract(image, page_number=0)
    
    print(f"   ✅ Extracted {len(ocr_result.raw_lines)} lines")
    
    # Show raw text
    print("\n2. Raw OCR Text:")
    print("-"*60)
    for i, line in enumerate(ocr_result.raw_lines, 1):
        print(f"   {i:2d}. {line}")
    
    # Extract everything with Mistral
    print("\n3. Mistral Analysis:")
    print("-"*60)
    mistral = MistralReasoning()
    
    full_data = mistral.extract_everything(ocr_result)
    
    # Pretty print ALL extracted data
    print("\n4. ALL EXTRACTED DATA:")
    print("="*60)
    print(json.dumps(full_data, indent=2, ensure_ascii=False))
    
    # Highlight key findings
    print("\n5. KEY FINDINGS:")
    print("-"*60)
    
    if 'student_name' in full_data and full_data['student_name']:
        print(f"   ✅ Student Name: {full_data['student_name']}")
    else:
        print(f"   ⚠️  Student Name: Not found")
    
    if 'issuer' in full_data:
        print(f"   ✅ Issuer: {full_data['issuer']}")
    
    if 'course_name' in full_data:
        print(f"   ✅ Course: {full_data['course_name']}")
    
    if 'certificate_ids' in full_data:
        print(f"   ✅ IDs: {full_data['certificate_ids']}")
    
    if 'urls' in full_data:
        print(f"   ✅ URLs: {full_data['urls']}")
    
    # List ALL fields found
    print(f"\n   📊 Total fields extracted: {len([k for k in full_data.keys() if not k.startswith('_')])}")
    print(f"   📋 Fields: {[k for k in full_data.keys() if not k.startswith('_')]}")
    
    print("\n" + "="*60)
    print("✅ EXTRACTION COMPLETE!")
    print("="*60)
    
    return full_data


if __name__ == "__main__":
    data = test_full_extraction()
