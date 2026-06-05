#!/usr/bin/env python3
"""
ULTRA FAST Medical Vision Service - Maximum Speed Optimization
Uses the smallest possible model settings for speed
"""

import os
import torch
from PIL import Image
import io
from typing import Dict, Optional, Union
import re
import time
import gc

class UltraFastMedicalVisionService:
    """ULTRA FAST Medical Vision Service - Maximum speed"""
    
    def __init__(self):
        self.qwen_model = None
        self.qwen_processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_loaded = False
        
        print(f"ULTRA FAST Medical Vision Service:")
        print(f"   Device: {self.device}")
        print(f"   GPU Available: {torch.cuda.is_available()}")
        
        # Model paths
        self.qwen_path = os.path.join(os.path.dirname(__file__), '..', 'Qwen2-VL-7B-Instruct')
        self.qwen_available = os.path.exists(self.qwen_path)
        
        if self.qwen_available:
            print(f"   [OK] Qwen2-VL model found")
        else:
            print(f"   [ERROR] Qwen2-VL model not found")
        
        # Import Gemini as fallback
        try:
            from services.gemini_vision_service import gemini_vision
            self.gemini_vision = gemini_vision if gemini_vision.available else None
            if self.gemini_vision:
                print(f"   [INFO] Gemini Vision available (fallback)")
        except:
            self.gemini_vision = None
    
    def _preprocess_image_ultra_fast(self, image: Image.Image, max_size: int = 256) -> Image.Image:
        """ULTRA FAST image preprocessing - very small images"""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to very small size for maximum speed
        width, height = image.size
        if max(width, height) > max_size:
            # Maintain aspect ratio
            if width > height:
                new_width = max_size
                new_height = int((height * max_size) / width)
            else:
                new_height = max_size
                new_width = int((width * max_size) / height)
            
            image = image.resize((new_width, new_height), Image.Resampling.NEAREST)  # Fastest resize
            print(f"   [RESIZE] Image: {width}x{height} -> {new_width}x{new_height}")
        
        return image
    
    def _load_qwen_ultra_fast(self):
        """Load Qwen2-VL with ULTRA FAST settings"""
        if self.model_loaded:
            return True
            
        if not self.qwen_available:
            return False
            
        try:
            print("   [LOADING] Loading Qwen2-VL (ULTRA FAST)...")
            start_time = time.time()
            
            from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
            from qwen_vl_utils import process_vision_info
            
            # Store process_vision_info
            self.process_vision_info = process_vision_info
            
            # ULTRA FAST loading settings
            load_kwargs = {
                "torch_dtype": torch.float32,  # Use float32 for CPU speed
                "device_map": "cpu",           # Force CPU for stability
                "trust_remote_code": True,
                "low_cpu_mem_usage": True,
                "use_safetensors": True,       # Faster loading
            }
            
            # Load model with minimal memory usage
            self.qwen_model = Qwen2VLForConditionalGeneration.from_pretrained(
                self.qwen_path,
                **load_kwargs
            )
            
            # Load processor with minimal settings
            self.qwen_processor = AutoProcessor.from_pretrained(
                self.qwen_path,
                trust_remote_code=True,
                min_pixels=64*28*28,    # Very small for speed
                max_pixels=256*28*28    # Very small for speed
            )
            
            load_time = time.time() - start_time
            print(f"   [OK] Qwen2-VL loaded in {load_time:.1f}s (ULTRA FAST)")
            self.model_loaded = True
            return True
            
        except Exception as e:
            print(f"   [ERROR] Qwen2-VL loading failed: {e}")
            return False
    
    def analyze_medical_image_ultra_fast(
        self, 
        image_data: Union[bytes, Image.Image], 
        document_type: str = "general",
        timeout: int = 15
    ) -> Dict:
        """ULTRA FAST medical image analysis"""
        start_time = time.time()
        
        try:
            # Convert to PIL Image
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                image = image_data
            
            # ULTRA FAST preprocessing
            image = self._preprocess_image_ultra_fast(image, max_size=256)  # Very small
            
            print(f"   [ANALYZE] Processing {document_type} (size: {image.size})")
            
            # Try Qwen2-VL first (LOCAL)
            if self.qwen_available:
                print(f"   [TRY] Qwen2-VL (LOCAL)...")
                result = self._analyze_with_qwen_ultra_fast(image, document_type, timeout)
                if result['success']:
                    elapsed = time.time() - start_time
                    print(f"   [SUCCESS] Qwen2-VL in {elapsed:.1f}s!")
                    return result
                print("   [FAIL] Qwen2-VL failed, trying fallback...")
            
            # Fallback to Gemini
            if self.gemini_vision:
                print(f"   [FALLBACK] Using Gemini Vision...")
                result = self.gemini_vision.analyze_medical_image(image, document_type)
                if result['success']:
                    elapsed = time.time() - start_time
                    print(f"   [SUCCESS] Gemini in {elapsed:.1f}s!")
                    return result
            
            # All failed
            elapsed = time.time() - start_time
            return {
                "success": False,
                "model": "none",
                "analysis": f"All methods failed after {elapsed:.1f}s",
                "extracted_text": "[Analysis failed]",
                "error": "Timeout or processing error"
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   [ERROR] Analysis error after {elapsed:.1f}s: {e}")
            return {
                "success": False,
                "model": "error",
                "analysis": f"Error: {str(e)}",
                "extracted_text": "",
                "error": str(e)
            }
    
    def _analyze_with_qwen_ultra_fast(self, image: Image.Image, document_type: str, timeout: int) -> Dict:
        """ULTRA FAST Qwen2-VL analysis"""
        try:
            if not self._load_qwen_ultra_fast():
                return {"success": False, "error": "Qwen2-VL not loaded"}
            
            print("      [RUN] Qwen2-VL analysis...")
            
            # Create ultra fast prompt
            prompt = self._create_ultra_fast_prompt(document_type)
            
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
            
            # ULTRA FAST generation settings
            generation_kwargs = {
                "max_new_tokens": 64,      # Very small for speed
                "temperature": 0.0,        # Deterministic for speed
                "do_sample": False,        # No sampling for speed
                "top_p": 0.5,              # Very small for speed
                "repetition_penalty": 1.0,
                "pad_token_id": self.qwen_processor.tokenizer.eos_token_id
            }
            
            # Generate
            print("      [GEN] Generating (ULTRA FAST)...")
            start_gen = time.time()
            
            with torch.no_grad():
                generated_ids = self.qwen_model.generate(
                    **inputs,
                    **generation_kwargs
                )
            
            gen_time = time.time() - start_gen
            print(f"      [TIME] Generation: {gen_time:.1f}s")
            
            # Decode
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            output_text = self.qwen_processor.batch_decode(
                generated_ids_trimmed,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]
            
            # Extract key info
            extracted_info = self._extract_key_info(output_text, document_type)
            
            print(f"      [OK] Qwen2-VL complete: {len(output_text)} chars")
            
            # Clear memory aggressively
            del inputs
            del generated_ids
            if self.device == "cuda":
                torch.cuda.empty_cache()
            gc.collect()
            
            return {
                "success": True,
                "model": "qwen2-vl-7b-instruct-LOCAL",
                "analysis": output_text,
                "extracted_text": output_text,
                "structured_data": extracted_info,
                "document_type": document_type,
                "processing_time": gen_time
            }
            
        except Exception as e:
            print(f"      [ERROR] Qwen2-VL error: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_ultra_fast_prompt(self, document_type: str) -> str:
        """Create ULTRA FAST, minimal prompts"""
        
        ultra_fast_prompts = {
            "lab_report": """Extract: Patient name, Blood type (A+, B-, O+, AB+), Lab name, Date. Format: PATIENT: [name], BLOOD TYPE: [type]""",
            
            "prescription": """Extract: Medications, Patient name, Doctor name. Format: MEDICATIONS: [list], PATIENT: [name]""",
            
            "general": """Extract: Patient details, Medical conditions, Test results"""
        }
        
        return ultra_fast_prompts.get(document_type, ultra_fast_prompts["general"])
    
    def _extract_key_info(self, response: str, document_type: str) -> Dict:
        """FAST extraction of key information"""
        
        result = {
            "text": response,
            "document_type": document_type,
            "extracted_fields": {}
        }
        
        # Quick blood type extraction
        blood_type = self._extract_blood_type_fast(response)
        if blood_type:
            result["extracted_fields"]["blood_type"] = blood_type
            print(f"      [EXTRACT] Blood type: {blood_type}")
        
        # Quick patient name extraction
        patient = self._extract_patient_name(response)
        if patient:
            result["extracted_fields"]["patient_name"] = patient
            print(f"      [EXTRACT] Patient: {patient}")
        
        return result
    
    def _extract_blood_type_fast(self, text: str) -> Optional[str]:
        """FAST blood type extraction"""
        patterns = [
            r'BLOOD\s+TYPE:\s*(A|B|AB|O)\s*(POSITIVE|NEGATIVE|\+|\-)',
            r'BLOOD TYPE:\s*(A|B|AB|O)\s*(POSITIVE|NEGATIVE|\+|\-)',
            r'(A|B|AB|O)\s*(POSITIVE|NEGATIVE|\+|\-)',
        ]
        
        text_upper = text.upper()
        
        for pattern in patterns:
            match = re.search(pattern, text_upper)
            if match:
                group = match.group(1)
                if len(match.groups()) > 1:
                    rh = match.group(2)
                    symbol = "+" if "POS" in rh or "+" in rh else "-"
                    return f"{group}{symbol}"
                else:
                    if "POSITIVE" in text_upper or "+" in text:
                        return f"{group}+"
                    elif "NEGATIVE" in text_upper:
                        return f"{group}-"
                    return f"{group}"
        
        return None
    
    def _extract_patient_name(self, text: str) -> Optional[str]:
        """Extract patient name"""
        patterns = [
            r'PATIENT:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'Patient:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'Name:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
    
    def clear_memory(self):
        """Clear GPU memory"""
        if self.device == "cuda":
            torch.cuda.empty_cache()
        gc.collect()


# Global instance
ultra_fast_vision_service = UltraFastMedicalVisionService()

