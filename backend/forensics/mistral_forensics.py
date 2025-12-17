"""
Mistral Forensics Analyzer
Separate module for certificate authenticity analysis
"""

import base64
import json
import os
from typing import Dict, Any
from mistralai import Mistral
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()


class MistralForensics:
    """
    Certificate Forensics using Mistral Vision AI
    
    Analyzes certificates for:
    - Visual manipulation
    - Authenticity markers
    - Quality indicators
    - Suspicious patterns
    """
    
    def __init__(self):
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment")
        
        self.client = Mistral(api_key=api_key)
        logger.info("[INFO] Mistral Forensics initialized")
    
    def analyze_certificate(self, image_path: str) -> Dict[str, Any]:
        """
        Perform forensics analysis on a certificate image.
        
        Args:
            image_path: Path to certificate image
            
        Returns:
            Dictionary with forensics report
        """
        
        # Read and encode image
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode()
        
        # Determine MIME type
        file_ext = image_path.lower().split('.')[-1]
        mime_type = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'pdf': 'application/pdf'
        }.get(file_ext, 'image/jpeg')
        
        try:
            logger.info("[INFO] Running forensics analysis...")
            
            response = self.client.chat.complete(
                model="pixtral-12b-2409",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": f"data:{mime_type};base64,{image_base64}"
                            },
                            {
                                "type": "text",
                                "text": """You are a certificate forensics expert. Analyze this certificate image for authenticity and potential manipulation.

Return ONLY a JSON object:

{
  "is_high_risk": true/false,
  "manipulation_score": 0.0 to 1.0,
  "anomalies_detected": ["Specific issues found"],
  "authenticity_indicators": ["Positive signs of authenticity"],
  "visual_quality": "excellent/good/fair/poor",
  "status": "Brief summary",
  "confidence": 0.0 to 1.0,
  "details": "Detailed forensics report"
}

FORENSICS CHECKLIST:

1. Font Analysis:
   - Are fonts consistent throughout?
   - Professional typography or amateur?
   - Any mismatched font sizes/styles?

2. Layout & Spacing:
   - Professional alignment?
   - Consistent margins and spacing?
   - Elements properly positioned?

3. Logo & Graphics:
   - Logos crisp and high-quality?
   - Official branding present?
   - Any pixelation or distortion?

4. Text Quality:
   - Sharp, clear text?
   - Any blurry or re-typed sections?
   - OCR artifacts visible?

5. Color & Contrast:
   - Uniform color palette?
   - Natural shadows and gradients?
   - Color mismatches or overlays?

6. Compression & Artifacts:
   - Signs of multiple compressions?
   - JPEG artifacts around text?
   - Unnatural edges or halos?

7. Overlays & Editing:
   - Text that looks pasted on?
   - Inconsistent backgrounds?
   - Clone stamp or copy-paste evidence?

8. Official Elements:
   - Seals, watermarks present?
   - Digital signatures visible?
   - Security features appropriate?

9. ID/URL Format:
   - Certificate IDs follow platform standards?
   - URLs formatted correctly?
   - Reference numbers consistent?

10. Overall Assessment:
    - Does it look professionally produced?
    - Matches known certificate templates?
    - Any red flags?

SCORING:
- manipulation_score: 0.0 = pristine/authentic, 1.0 = heavily manipulated
- is_high_risk: true if score > 0.5 OR critical anomalies
- confidence: How certain you are about the analysis

Be thorough and specific. List actual observations, not generic statements."""
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            
            # Parse JSON
            try:
                forensics = json.loads(result_text)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    forensics = json.loads(json_match.group())
                else:
                    forensics = self._default_forensics()
            
            # Ensure all required fields exist
            forensics = self._normalize_forensics(forensics)
            
            logger.info(f"[INFO] Forensics complete: Risk={forensics['is_high_risk']}, Score={forensics['manipulation_score']}")
            
            return {
                "success": True,
                "forensics": forensics
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Forensics analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "forensics": self._default_forensics()
            }
    
    def _default_forensics(self) -> Dict[str, Any]:
        """Default forensics response when analysis fails"""
        return {
            "is_high_risk": False,
            "manipulation_score": 0.0,
            "anomalies_detected": [],
            "authenticity_indicators": [],
            "visual_quality": "unknown",
            "status": "Analysis unavailable",
            "confidence": 0.0,
            "details": "Forensics analysis could not be performed"
        }
    
    def _normalize_forensics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all required fields exist with defaults"""
        defaults = self._default_forensics()
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        return data
