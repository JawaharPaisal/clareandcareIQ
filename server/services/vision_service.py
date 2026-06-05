#!/usr/bin/env python3
"""
Medical Vision Service - LOCAL FIRST
Prioritizes local models (Qwen2-VL, LLaVA-Med) with Gemini as RARE fallback only
"""

import os
import torch
from PIL import Image
import io
from typing import Dict, Optional, Union
import re

class MedicalVisionService:
    """Service for analyzing medical images - LOCAL MODELS FIRST"""
    
    def __init__(self):
        self.qwen_model = None
        self.qwen_processor = None
        self.llava_model = None
        self.llava_tokenizer = None
        self.llava_image_processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"🔧 Medical Vision Service Initialization (LOCAL FIRST):")
        print(f"   Device: {self.device}")
        
        # Model paths
        self.qwen_path = os.path.join(os.path.dirname(__file__), '..', 'Qwen2-VL-7B-Instruct')
        self.llava_path = os.path.join(os.path.dirname(__file__), '..', 'llava-med-v1.5-mistral-7b')
        
        # Check availability
        self.qwen_available = os.path.exists(self.qwen_path)
        self.llava_available = os.path.exists(self.llava_path)
        
        if self.qwen_available:
            print(f"   ✅ Qwen2-VL model found (PRIMARY)")
        else:
            print(f"   ❌ Qwen2-VL model not found")
        
        if self.llava_available:
            print(f"   ✅ LLaVA-Med model found (SECONDARY)")
        else:
            print(f"   ❌ LLaVA-Med model not found")
        
        # Import Gemini Vision as RARE fallback only
        try:
            from services.gemini_vision_service import gemini_vision
            self.gemini_vision = gemini_vision if gemini_vision.available else None
            if self.gemini_vision:
                print(f"   ℹ️ Gemini Vision available (RARE FALLBACK only)")
        except:
            self.gemini_vision = None
    
    def _load_qwen_vl(self):
        """Load Qwen2-VL model - PRIMARY for all documents"""
        if self.qwen_model is None and self.qwen_available:
            try:
                print("   🚀 Loading Qwen2-VL model (PRIMARY)...")
                from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
                from qwen_vl_utils import process_vision_info
                
                # Store process_vision_info for later use
                self.process_vision_info = process_vision_info
                
                # Load model with proper settings
                self.qwen_model = Qwen2VLForConditionalGeneration.from_pretrained(
                    self.qwen_path,
                    torch_dtype="auto",  # Let model decide
                    device_map="auto" if self.device == "cuda" else "cpu",
                    trust_remote_code=True,
                    low_cpu_mem_usage=True
                )
                
                # Load processor
                self.qwen_processor = AutoProcessor.from_pretrained(
                    self.qwen_path,
                    trust_remote_code=True,
                    min_pixels=256*28*28,  # Qwen2-VL config
                    max_pixels=1280*28*28
                )
                
                print("   ✅ Qwen2-VL loaded successfully! (PRIMARY MODEL READY)")
                return True
                
            except Exception as e:
                print(f"   ❌ Qwen2-VL loading failed: {e}")
                self.qwen_available = False
                return False
        return self.qwen_model is not None
    
    def _load_llava_med(self):
        """Load LLaVA-Med model - SECONDARY for medical images"""
        if self.llava_model is None and self.llava_available:
            try:
                print("   🚀 Loading LLaVA-Med model (SECONDARY)...")
                from transformers import LlavaNextForConditionalGeneration, LlavaNextProcessor
                
                # Load processor
                self.llava_processor = LlavaNextProcessor.from_pretrained(
                    self.llava_path,
                    trust_remote_code=True
                )
                
                # Load model
                self.llava_model = LlavaNextForConditionalGeneration.from_pretrained(
                    self.llava_path,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else "cpu",
                    trust_remote_code=True,
                    low_cpu_mem_usage=True
                )
                
                print("   ✅ LLaVA-Med loaded successfully! (SECONDARY MODEL READY)")
                return True
                
            except Exception as e:
                print(f"   ❌ LLaVA-Med loading failed: {e}")
                print(f"   💡 LLaVA-Med requires specific configuration. Using Qwen2-VL instead.")
                self.llava_available = False
                return False
        return self.llava_model is not None
    
    def analyze_medical_image(
        self, 
        image_data: Union[bytes, Image.Image], 
        document_type: str = "general",
        specific_questions: Optional[list] = None
    ) -> Dict:
        """
        Analyze medical image - LOCAL MODELS FIRST, Gemini as RARE fallback
        
        Args:
            image_data: Image bytes or PIL Image object
            document_type: Type of document
            specific_questions: Optional questions
            
        Returns:
            Dict with analysis results
        """
        try:
            # Convert to PIL Image
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                image = image_data
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            print(f"   🖼️ Analyzing {document_type} (size: {image.size})")
            
            # ====== PRIORITY 1: Qwen2-VL (LOCAL - PRIMARY) ======
            if self.qwen_available:
                print(f"   🥇 Trying PRIMARY: Qwen2-VL (local)...")
                result = self._analyze_with_qwen(image, document_type, specific_questions)
                if result['success']:
                    print(f"   ✅ SUCCESS with Qwen2-VL (local)!")
                    return result
                print("   ⚠️ Qwen2-VL failed, trying secondary...")
            
            # ====== PRIORITY 2: LLaVA-Med (LOCAL - SECONDARY) ======
            if self.llava_available:
                print(f"   🥈 Trying SECONDARY: LLaVA-Med (local)...")
                result = self._analyze_with_llava(image, document_type, specific_questions)
                if result['success']:
                    print(f"   ✅ SUCCESS with LLaVA-Med (local)!")
                    return result
                print("   ⚠️ LLaVA-Med failed, trying fallback...")
            
            # ====== PRIORITY 3: Gemini Vision (CLOUD - RARE FALLBACK ONLY) ======
            if self.gemini_vision:
                print(f"   ⚠️ LOCAL MODELS FAILED - Using Gemini Vision (rare fallback)...")
                result = self.gemini_vision.analyze_medical_image(image, document_type, specific_questions)
                if result['success']:
                    print(f"   ✅ SUCCESS with Gemini Vision (cloud fallback)")
                    return result
            
            # All failed
            return {
                "success": False,
                "model": "none",
                "analysis": "All vision analysis methods failed",
                "extracted_text": "[Vision analysis unavailable]",
                "error": "No working vision services"
            }
            
        except Exception as e:
            print(f"   ❌ Vision analysis error: {e}")
            return {
                "success": False,
                "model": "error",
                "analysis": f"Error: {str(e)}",
                "extracted_text": "",
                "error": str(e)
            }
    
    def _analyze_with_qwen(self, image: Image.Image, document_type: str, questions: Optional[list]) -> Dict:
        """Analyze with Qwen2-VL - PRIMARY METHOD"""
        try:
            if not self._load_qwen_vl():
                return {"success": False, "error": "Qwen2-VL not loaded"}
            
            print("      🤖 Running Qwen2-VL analysis...")
            
            # Create comprehensive prompt
            prompt = self._create_vision_prompt(document_type, questions)
            
            # Qwen2-VL message format
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # Apply chat template
            text = self.qwen_processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Process vision info
            image_inputs, video_inputs = self.process_vision_info(messages)
            
            # Prepare inputs
            inputs = self.qwen_processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt"
            )
            inputs = inputs.to(self.device)
            
            # Generate
            print("      ⏳ Generating analysis...")
            with torch.no_grad():
                generated_ids = self.qwen_model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9
                )
            
            # Decode
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            output_text = self.qwen_processor.batch_decode(
                generated_ids_trimmed,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]
            
            # Extract structured info
            extracted_info = self._extract_structured_info(output_text, document_type)
            
            print(f"      ✅ Qwen2-VL complete: {len(output_text)} chars")
            
            return {
                "success": True,
                "model": "qwen2-vl-7b-instruct-LOCAL",
                "analysis": output_text,
                "extracted_text": output_text,
                "structured_data": extracted_info,
                "document_type": document_type
            }
            
        except Exception as e:
            print(f"      ❌ Qwen2-VL error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def _analyze_with_llava(self, image: Image.Image, document_type: str, questions: Optional[list]) -> Dict:
        """Analyze with LLaVA-Med - SECONDARY METHOD"""
        try:
            if not self._load_llava_med():
                return {"success": False, "error": "LLaVA-Med not loaded"}
            
            print("      🤖 Running LLaVA-Med analysis...")
            
            # Create prompt
            prompt = self._create_vision_prompt(document_type, questions)
            
            # LLaVA conversation format
            conversation = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # Process with LLaVA processor
            inputs = self.llava_processor(
                text=self.llava_processor.apply_chat_template(conversation, add_generation_prompt=True),
                images=image,
                return_tensors="pt"
            ).to(self.device)
            
            # Generate
            print("      ⏳ Generating analysis...")
            with torch.no_grad():
                outputs = self.llava_model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.7,
                    do_sample=True
                )
            
            # Decode
            response = self.llava_processor.decode(outputs[0], skip_special_tokens=True)
            
            # Extract structured info
            extracted_info = self._extract_structured_info(response, document_type)
            
            print(f"      ✅ LLaVA-Med complete: {len(response)} chars")
            
            return {
                "success": True,
                "model": "llava-med-v1.5-mistral-7b-LOCAL",
                "analysis": response,
                "extracted_text": response,
                "structured_data": extracted_info,
                "document_type": document_type
            }
            
        except Exception as e:
            print(f"      ❌ LLaVA-Med error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def _create_vision_prompt(self, document_type: str, questions: Optional[list] = None) -> str:
        """Create comprehensive prompts for medical document analysis"""
        
        base_prompts = {
            "prescription": """Carefully read and extract ALL information from this prescription:

EXTRACT COMPLETELY:
1. ALL medication names with EXACT dosages (e.g., "Metformin 500mg")
2. ALL instructions (frequency like "twice daily", timing like "with food")
3. Patient name if visible
4. Doctor name and signature
5. Prescription date
6. Hospital/clinic name
7. Any special warnings or notes

READ EVERY WORD - even if partially visible or handwritten.

Format as:
MEDICATIONS:
- [Name] [Dosage] - [Instructions]

PATIENT: [name]
DOCTOR: [name]  
DATE: [date]
HOSPITAL: [name]

COMPLETE TEXT: [Every single word visible]""",
            
            "lab_report": """Read this laboratory/blood test report COMPLETELY and extract EVERYTHING:

EXTRACT ALL:
1. Patient name, age, ID
2. Lab name and location
3. Test dates (collection and reporting)
4. EVERY test with:
   - Exact test name
   - Result value
   - Unit (mg/dL, %, mmHg, etc.)
   - Reference range if shown
   - Flag if HIGH/LOW/ABNORMAL
5. **BLOOD TYPE if present** (format as A+, O+, B-, AB+, etc.)
6. Doctor/technician name

BE THOROUGH - read every line, every number.

Format as:
PATIENT: [full name]
AGE: [age]
LAB: [lab name]
TEST DATE: [date]

**BLOOD TYPE: [A/B/AB/O with +/-]** (if blood grouping test)

TEST RESULTS:
- [Test]: [Value] [Unit] (Ref: [range]) [Status]

FINDINGS: [Any abnormalities]

COMPLETE TEXT: [All visible text]""",
            
            "general": """Extract EVERY word and number from this medical document:

READ COMPLETELY:
1. Every word visible (even if unclear)
2. All numbers and dates
3. Patient information
4. Medical terms and conditions
5. Medications or test results
6. Doctor/hospital information
7. Any diagnoses or findings

Be extremely thorough - extract everything."""
        }
        
        prompt = base_prompts.get(document_type, base_prompts["general"])
        
        if questions:
            prompt += "\n\nADDITIONAL QUESTIONS:\n"
            for i, q in enumerate(questions, 1):
                prompt += f"{i}. {q}\n"
        
        return prompt
    
    def _extract_structured_info(self, response: str, document_type: str) -> Dict:
        """Extract structured data from analysis"""
        
        result = {
            "text": response,
            "document_type": document_type,
            "extracted_fields": {}
        }
        
        # Extract blood type (IMPORTANT!)
        blood_type = self._extract_blood_type(response)
        if blood_type:
            result["extracted_fields"]["blood_type"] = blood_type
            print(f"      🩸 Extracted blood type: {blood_type}")
        
        # Extract medications
        medications = self._extract_medications(response)
        if medications:
            result["extracted_fields"]["medications"] = medications
            print(f"      💊 Extracted {len(medications)} medications")
        
        # Extract lab values
        lab_values = self._extract_lab_values(response)
        if lab_values:
            result["extracted_fields"]["lab_values"] = lab_values
            print(f"      🔬 Extracted {len(lab_values)} lab values")
        
        # Extract conditions
        conditions = self._extract_conditions(response)
        if conditions:
            result["extracted_fields"]["conditions"] = conditions
            print(f"      🏥 Extracted conditions: {conditions}")
        
        return result
    
    def _extract_blood_type(self, text: str) -> Optional[str]:
        """Extract blood type - ENHANCED for your blood test"""
        patterns = [
            r'BLOOD\s+TYPE:\s*(A|B|AB|O)\s*(POSITIVE|NEGATIVE|\+|\-)',
            r'ABO\s+Group:\s*(A|B|AB|O)',
            r'Rh\s+Type:\s*(POSITIVE|NEGATIVE|\+|\-)',
            r'\b(A|B|AB|O)\s+(POSITIVE|NEGATIVE)\b',
            r'Blood\s+Group:\s*(A|B|AB|O)',
        ]
        
        text_upper = text.upper()
        
        # Try each pattern
        for pattern in patterns:
            match = re.search(pattern, text_upper)
            if match:
                group = match.group(1)
                if len(match.groups()) > 1:
                    rh = match.group(2)
                    symbol = "+" if "POS" in rh or "+" in rh else "-"
                    return f"{group}{symbol}"
                else:
                    # Look for Rh separately
                    if "POSITIVE" in text_upper or "RH POSITIVE" in text_upper or "+ " in text:
                        return f"{group}+"
                    elif "NEGATIVE" in text_upper or "RH NEGATIVE" in text_upper:
                        return f"{group}-"
                    return f"{group}"
        
        return None
    
    def _extract_medications(self, text: str) -> list:
        """Extract medications with dosages"""
        medications = []
        
        # Patterns for medications
        patterns = [
            r'([A-Z][a-z]+(?:ol|in|am|ide|ine|ate|pril|statin|mycin))\s+(\d+\s*mg)',
            r'([A-Z][a-z]{3,})\s+(\d+\s*mg)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for name, dose in matches:
                medications.append(f"{name} {dose}")
        
        return list(set(medications))
    
    def _extract_lab_values(self, text: str) -> list:
        """Extract lab test values"""
        lab_values = []
        
        # Look for test: value patterns
        pattern = r'([A-Za-z\s]{3,30}):\s*(\d+\.?\d*)\s*([a-zA-Z/%]*)'
        matches = re.findall(pattern, text)
        
        for test, value, unit in matches:
            test_clean = test.strip()
            if len(test_clean) > 2:
                try:
                    lab_values.append({
                        "test": test_clean,
                        "value": float(value),
                        "unit": unit.strip() if unit else ""
                    })
                except:
                    pass
        
        return lab_values
    
    def _extract_conditions(self, text: str) -> list:
        """Extract medical conditions"""
        conditions = []
        keywords = [
            'diabetes', 'hypertension', 'high blood pressure', 'cholesterol',
            'asthma', 'arthritis', 'fracture', 'infection', 'pneumonia',
            'cancer', 'tumor', 'anemia', 'thyroid'
        ]
        
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                conditions.append(keyword.title())
        
        return list(set(conditions))


# Global instance
vision_service = MedicalVisionService()
