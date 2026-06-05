#!/usr/bin/env python3
"""
OCR Fallback Service
Uses Tesseract OCR as a reliable fallback when vision models fail
"""

import os
from PIL import Image
import io
from typing import Union
import re

# Try to import pytesseract
try:
    import pytesseract
    OCR_AVAILABLE = True
    print("✅ Tesseract OCR available")
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️ Tesseract OCR not available - install with: pip install pytesseract")

class OCRFallbackService:
    """Reliable OCR fallback using Tesseract"""
    
    def __init__(self):
        self.ocr_available = OCR_AVAILABLE
        
        # Try to find Tesseract executable on Windows
        if self.ocr_available and os.name == 'nt':
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    print(f"   ✅ Tesseract found at: {path}")
                    break
    
    def extract_text_from_image(self, image_data: Union[bytes, Image.Image]) -> str:
        """Extract text from image using OCR"""
        if not self.ocr_available:
            return "[OCR not available - install Tesseract and pytesseract]"
        
        try:
            # Convert bytes to PIL Image if needed
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                image = image_data
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text with Tesseract
            text = pytesseract.image_to_string(image)
            
            return text.strip()
            
        except Exception as e:
            return f"[OCR error: {str(e)}]"
    
    def analyze_medical_document(self, image_data: Union[bytes, Image.Image], document_type: str = "general") -> dict:
        """Analyze medical document with OCR and basic parsing"""
        
        # Extract text
        extracted_text = self.extract_text_from_image(image_data)
        
        if not extracted_text or extracted_text.startswith("["):
            return {
                "success": False,
                "error": "OCR extraction failed",
                "extracted_text": extracted_text
            }
        
        # Parse based on document type
        analysis = self._analyze_text(extracted_text, document_type)
        
        return {
            "success": True,
            "model": "tesseract-ocr-fallback",
            "analysis": analysis,
            "extracted_text": extracted_text,
            "structured_data": self._extract_structured_data(extracted_text, document_type),
            "document_type": document_type
        }
    
    def _analyze_text(self, text: str, document_type: str) -> str:
        """Generate simple analysis from extracted text"""
        
        if document_type == "prescription":
            return f"Prescription document with {len(text.split())} words extracted. Contains medication information."
        elif document_type == "lab_report":
            # Count numbers (likely test values)
            numbers = re.findall(r'\d+\.?\d*', text)
            return f"Laboratory report with {len(numbers)} numerical values extracted. Contains test results."
        else:
            return f"Medical document with {len(text)} characters extracted via OCR."
    
    def _extract_structured_data(self, text: str, document_type: str) -> dict:
        """Extract structured data from OCR text"""
        
        result = {"extracted_fields": {}}
        
        # Extract blood type
        blood_pattern = r'\b(A|B|AB|O)\s*(positive|negative|\+|\-)\b'
        blood_match = re.search(blood_pattern, text, re.IGNORECASE)
        if blood_match:
            blood_group = blood_match.group(1).upper()
            rh = blood_match.group(2).lower()
            blood_type = f"{blood_group}+" if 'pos' in rh or '+' in rh else f"{blood_group}-"
            result["extracted_fields"]["blood_type"] = blood_type
        
        # Extract medications
        med_pattern = r'([A-Z][a-z]+(?:ol|in|am|ide|ine|ate))\s+(\d+\s*mg)'
        medications = re.findall(med_pattern, text)
        if medications:
            result["extracted_fields"]["medications"] = [f"{m[0]} {m[1]}" for m in medications]
        
        # Extract lab values with units
        lab_pattern = r'([A-Za-z\s]{3,20}):\s*(\d+\.?\d*)\s*([a-zA-Z/%]+)'
        lab_values = re.findall(lab_pattern, text)
        if lab_values:
            result["extracted_fields"]["lab_values"] = [
                {"test": l[0].strip(), "value": l[1], "unit": l[2]} 
                for l in lab_values
            ]
        
        return result


# Global instance
ocr_fallback = OCRFallbackService()


