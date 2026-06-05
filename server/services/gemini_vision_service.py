#!/usr/bin/env python3
"""
Gemini Vision Service
Reliable cloud-based vision analysis using Google Gemini Vision API
"""

import os
import google.generativeai as genai
from PIL import Image
import io
from typing import Dict, Optional, Union
import re

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class GeminiVisionService:
    """Vision analysis using Gemini Vision API - Always works!"""
    
    def __init__(self):
        self.available = False
        self.model = None
        
        print(f"🔧 Gemini Vision Service Initialization:")
        
        if not GEMINI_API_KEY:
            print("   ⚠️ GEMINI_API_KEY not set")
            return
        
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Supports vision
            self.available = True
            print("   ✅ Gemini Vision ready!")
        except Exception as e:
            print(f"   ❌ Gemini Vision setup failed: {e}")
    
    def analyze_medical_image(
        self, 
        image_data: Union[bytes, Image.Image], 
        document_type: str = "general",
        specific_questions: Optional[list] = None
    ) -> Dict:
        """
        Analyze medical image or document with Gemini Vision
        
        Args:
            image_data: Image bytes or PIL Image object
            document_type: Type of document
            specific_questions: Optional list of specific questions
            
        Returns:
            Dict with analysis results
        """
        if not self.available:
            return {
                "success": False,
                "error": "Gemini Vision not available - check API key",
                "extracted_text": ""
            }
        
        try:
            # Convert bytes to PIL Image if needed
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                image = image_data
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            print(f"   🤖 Analyzing with Gemini Vision API...")
            
            # Create comprehensive prompt
            prompt = self._create_vision_prompt(document_type, specific_questions)
            
            # Send to Gemini Vision
            response = self.model.generate_content([prompt, image])
            
            analysis_text = response.text
            
            # Extract structured information
            extracted_info = self._extract_structured_info(analysis_text, document_type)
            
            print(f"   ✅ Gemini Vision analysis complete ({len(analysis_text)} chars)")
            
            return {
                "success": True,
                "model": "gemini-2.0-flash-vision",
                "analysis": analysis_text,
                "extracted_text": analysis_text,
                "structured_data": extracted_info,
                "document_type": document_type
            }
            
        except Exception as e:
            print(f"   ❌ Gemini Vision error: {e}")
            return {
                "success": False,
                "error": str(e),
                "extracted_text": ""
            }
    
    def _create_vision_prompt(self, document_type: str, questions: Optional[list] = None) -> str:
        """Create comprehensive prompt for Gemini Vision"""
        
        base_prompts = {
            "prescription": """You are analyzing a medical prescription. Extract ALL information visible:

1. **Medications**: List every medication with exact dosage (e.g., "Metformin 500mg")
2. **Instructions**: How to take each medication (frequency, timing, with/without food)
3. **Patient Info**: Name, age, date if visible
4. **Doctor Info**: Name, signature, hospital/clinic
5. **Prescription Date**: When it was written
6. **Any warnings or special instructions**

Format your response as:
MEDICATIONS FOUND:
- [List each medication with dosage and instructions]

PATIENT: [name if visible]
DOCTOR: [name if visible]
DATE: [date if visible]

FULL TEXT EXTRACTION:
[Every word visible in the image]""",
            
            "lab_report": """You are analyzing a laboratory/blood test report. Extract EVERYTHING:

1. **Patient Information**: Name, age, ID number
2. **Lab/Hospital**: Name, location
3. **Test Date**: Collection and reported dates
4. **All Tests and Values**: Extract EVERY test with:
   - Test name
   - Result value
   - Unit (mg/dL, %, etc.)
   - Reference range if shown
   - Mark if HIGH or LOW

5. **Blood Type**: If this is a blood grouping test, extract the blood type clearly

Format your response as:
PATIENT: [name]
LAB: [lab name]
TEST DATE: [date]

TEST RESULTS:
- Test Name: Value Unit (Reference: range) [Status]

BLOOD TYPE: [if present, format as "A+", "O+", "B-", "AB+", etc.]

FINDINGS: [Any abnormal findings]

COMPLETE TEXT:
[All text visible in the document]""",
            
            "general": """Extract ALL text and information from this medical document:

1. Read every word visible
2. Extract all numbers, dates, names
3. Identify document type
4. Extract any medical information
5. Note any abnormal findings

Be extremely thorough - extract everything you can see.""",
            
            "xray": """Analyze this X-ray image in detail:
1. Identify body part/region
2. Describe all visible anatomical structures
3. Note any abnormalities, fractures, or findings
4. Assess image quality
5. Extract any text/labels on the image
6. Provide clinical interpretation""",
            
            "ct_scan": """Analyze this CT scan thoroughly:
1. Identify anatomical region and orientation
2. Describe all visible structures
3. Note any lesions, masses, or abnormalities
4. Measure any visible densities
5. Extract any measurements or text
6. Provide clinical assessment""",
        }
        
        prompt = base_prompts.get(document_type, base_prompts["general"])
        
        # Add specific questions if provided
        if questions:
            prompt += "\n\nADDITIONAL QUESTIONS:\n"
            for i, q in enumerate(questions, 1):
                prompt += f"{i}. {q}\n"
        
        return prompt
    
    def _extract_structured_info(self, response: str, document_type: str) -> Dict:
        """Extract structured information from Gemini response"""
        
        result = {
            "text": response,
            "document_type": document_type,
            "extracted_fields": {}
        }
        
        # Extract blood type
        blood_type = self._extract_blood_type(response)
        if blood_type:
            result["extracted_fields"]["blood_type"] = blood_type
            print(f"   🩸 Extracted blood type: {blood_type}")
        
        # Extract medications
        if document_type == "prescription":
            medications = self._extract_medications(response)
            if medications:
                result["extracted_fields"]["medications"] = medications
                print(f"   💊 Extracted {len(medications)} medications")
        
        # Extract lab values
        if document_type == "lab_report" or document_type == "general":
            lab_values = self._extract_lab_values(response)
            if lab_values:
                result["extracted_fields"]["lab_values"] = lab_values
                print(f"   🔬 Extracted {len(lab_values)} lab values")
            
            abnormal_values = self._extract_abnormal_flags(response)
            if abnormal_values:
                result["extracted_fields"]["abnormal_values"] = abnormal_values
        
        # Extract conditions
        conditions = self._extract_conditions(response)
        if conditions:
            result["extracted_fields"]["conditions"] = conditions
            print(f"   🏥 Extracted {len(conditions)} conditions")
        
        return result
    
    def _extract_blood_type(self, text: str) -> Optional[str]:
        """Extract blood type from text"""
        # Comprehensive patterns for blood type
        patterns = [
            r'blood\s+type:\s*(A|B|AB|O)\s*(positive|negative|\+|\-)',
            r'(A|B|AB|O)\s*(positive|negative|\+|\-)',
            r'ABO\s+Group:\s*(A|B|AB|O)',
            r'Rh\s+Type:\s*(positive|negative|\+|\-)',
        ]
        
        text_upper = text.upper()
        
        # Look for explicit blood type statements
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                blood_group = match.group(1).upper()
                if len(match.groups()) > 1:
                    rh = match.group(2).lower()
                    if 'pos' in rh or '+' in rh:
                        return f"{blood_group}+"
                    elif 'neg' in rh or '-' in rh:
                        return f"{blood_group}-"
        
        # Look for pattern like "O POSITIVE" or "AB NEGATIVE"
        simple_pattern = r'\b(A|B|AB|O)\s+(POSITIVE|NEGATIVE)\b'
        match = re.search(simple_pattern, text_upper)
        if match:
            group = match.group(1)
            rh = "+" if "POS" in match.group(2) else "-"
            return f"{group}{rh}"
        
        return None
    
    def _extract_medications(self, text: str) -> list:
        """Extract medication names from text"""
        medications = []
        
        # Look for lines with "mg" or dosage patterns
        lines = text.split('\n')
        for line in lines:
            if 'mg' in line.lower() or 'tablet' in line.lower() or 'capsule' in line.lower():
                # Extract medication name and dosage
                med_match = re.search(r'([A-Z][a-z]+(?:ol|in|am|ide|ine|ate|pril))\s+(\d+\s*mg)', line)
                if med_match:
                    medications.append(f"{med_match.group(1)} {med_match.group(2)}")
        
        return list(set(medications))
    
    def _extract_lab_values(self, text: str) -> list:
        """Extract lab test values"""
        lab_values = []
        
        # Look for patterns like "Test: value unit"
        patterns = [
            r'([A-Za-z\s]+):\s*(\d+\.?\d*)\s*([a-zA-Z/%]+)',
            r'([A-Za-z\s]+)\s+(\d+\.?\d*)\s+([a-zA-Z/%]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for test, value, unit in matches:
                test_clean = test.strip()
                if len(test_clean) > 2 and not test_clean.isupper():
                    try:
                        lab_values.append({
                            "test": test_clean,
                            "value": float(value),
                            "unit": unit.strip()
                        })
                    except:
                        pass
        
        return lab_values
    
    def _extract_abnormal_flags(self, text: str) -> list:
        """Extract abnormal value flags"""
        abnormal = []
        keywords = ['high', 'low', 'elevated', 'decreased', 'abnormal', 'out of range']
        
        lines = text.split('\n')
        for line in lines:
            if any(kw in line.lower() for kw in keywords):
                abnormal.append(line.strip())
        
        return abnormal
    
    def _extract_conditions(self, text: str) -> list:
        """Extract medical conditions mentioned"""
        conditions = []
        condition_keywords = [
            'diabetes', 'hypertension', 'high blood pressure', 'cholesterol',
            'asthma', 'arthritis', 'fracture', 'infection', 'cancer',
            'pneumonia', 'anemia', 'thyroid', 'heart disease'
        ]
        
        text_lower = text.lower()
        for condition in condition_keywords:
            if condition in text_lower:
                conditions.append(condition.title())
        
        return list(set(conditions))


# Global instance
gemini_vision = GeminiVisionService()


