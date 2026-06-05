#!/usr/bin/env python3
"""
Medical Report Processing Service
Handles PDF and image file processing for medical reports
"""

import os
import io
from typing import Dict, Optional
from datetime import datetime
from PIL import Image

# Import ULTRA FAST vision service for maximum speed
try:
    from services.ultra_fast_vision_service import ultra_fast_vision_service
    VISION_AVAILABLE = True
    print("[OK] ULTRA FAST Vision service loaded")
except ImportError:
    print("[WARNING] Ultra fast vision service not available, trying standard...")
    try:
        from services.vision_service import vision_service
        VISION_AVAILABLE = True
    except ImportError:
        print("[ERROR] Vision service not available")
        VISION_AVAILABLE = False

# Import OCR fallback
try:
    from services.ocr_fallback import ocr_fallback
    OCR_AVAILABLE = True
except ImportError:
    print("⚠️ OCR fallback not available")
    OCR_AVAILABLE = False

# Import Gemini Vision (most reliable)
try:
    from services.gemini_vision_service import gemini_vision
    GEMINI_VISION_AVAILABLE = gemini_vision.available
except ImportError:
    print("⚠️ Gemini Vision not available")
    GEMINI_VISION_AVAILABLE = False
    gemini_vision = None

# Import PDF processing
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    print("⚠️ PyMuPDF not available - PDF processing limited")
    PDF_AVAILABLE = False

class ReportProcessor:
    """Service for processing medical reports"""
    
    def __init__(self):
        self.supported_formats = {
            'pdf': self._process_pdf,
            'txt': self._process_text,
            'jpg': self._process_image,
            'jpeg': self._process_image,
            'png': self._process_image
        }
        # Use ultra fast vision service for maximum speed
        if VISION_AVAILABLE:
            try:
                self.ultra_fast_vision_service = ultra_fast_vision_service
                self.vision_service = None  # Don't use slow version
                print("[OK] Using ULTRA FAST vision service")
            except:
                self.vision_service = vision_service
                self.ultra_fast_vision_service = None
                print("[WARNING] Using standard vision service")
        else:
            self.vision_service = None
            self.ultra_fast_vision_service = None
    
    def process_file(self, file_content: bytes, filename: str, file_type: str) -> Dict:
        """
        Process uploaded medical report file
        
        Args:
            file_content: Raw file content
            filename: Original filename
            file_type: File extension (pdf, txt, jpg, etc.)
            
        Returns:
            Dict with extracted text and metadata
        """
        try:
            if file_type not in self.supported_formats:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Process the file based on type
            processor = self.supported_formats[file_type]
            extracted_text = processor(file_content)
            
            # Create processing result
            result = {
                "filename": filename,
                "file_type": file_type,
                "extracted_text": extracted_text,
                "text_length": len(extracted_text),
                "processed_at": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
            return result
            
        except Exception as e:
            return {
                "filename": filename,
                "file_type": file_type,
                "extracted_text": "",
                "text_length": 0,
                "processed_at": datetime.utcnow().isoformat(),
                "status": "error",
                "error": str(e)
            }
    
    def _process_pdf(self, file_content: bytes) -> str:
        """Process PDF files with text extraction and vision analysis"""
        try:
            if not PDF_AVAILABLE:
                return "[PDF processing unavailable - PyMuPDF not installed]"
            
            # Open PDF from bytes
            pdf_document = fitz.open(stream=file_content, filetype="pdf")
            
            extracted_text = []
            
            # Process each page
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                
                # Extract text
                page_text = page.get_text()
                if page_text.strip():
                    extracted_text.append(f"--- Page {page_num + 1} ---\n{page_text}")
                
                # If page has images or little text, use vision analysis
                if len(page_text.strip()) < 50 or page.get_images():
                    # Convert page to image for vision analysis
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scale for better quality
                    img_bytes = pix.tobytes("png")
                    
                    if self.vision_service:
                        print(f"   📄 Analyzing PDF page {page_num + 1} with vision model...")
                        vision_result = self.vision_service.analyze_medical_image(
                            img_bytes,
                            document_type="general"
                        )
                        
                        if vision_result.get('success'):
                            extracted_text.append(f"\n--- Vision Analysis (Page {page_num + 1}) ---\n{vision_result['extracted_text']}")
            
            pdf_document.close()
            
            full_text = "\n\n".join(extracted_text)
            return full_text if full_text.strip() else "[No text extracted from PDF]"
            
        except Exception as e:
            print(f"   ❌ PDF processing error: {e}")
            return f"[PDF processing error: {str(e)}]"
    
    def _process_text(self, file_content: bytes) -> str:
        """Process plain text files"""
        try:
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    return file_content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, return a safe representation
            return file_content.decode('utf-8', errors='replace')
            
        except Exception as e:
            return f"Error processing text file: {str(e)}"
    
    def _process_image(self, file_content: bytes) -> str:
        """Process image files using vision models with OCR fallback"""
        try:
            # Load image
            image = Image.open(io.BytesIO(file_content))
            
            # Determine document type
            document_type = self._detect_document_type(image)
            
            print(f"   🖼️ Processing image (type: {document_type}, size: {image.size})...")
            
            # PRIMARY: Try ULTRA FAST LOCAL vision models
            if hasattr(self, 'ultra_fast_vision_service') and self.ultra_fast_vision_service:
                print(f"   [ULTRA FAST] Attempting ULTRA FAST LOCAL vision model analysis...")
                result = self.ultra_fast_vision_service.analyze_medical_image_ultra_fast(
                    image,
                    document_type=document_type,
                    timeout=15  # 15 second timeout
                )
            elif self.vision_service:
                print(f"   🥇 Attempting LOCAL vision model analysis...")
                result = self.vision_service.analyze_medical_image(
                    image,
                    document_type=document_type
                )
                
                if result.get('success'):
                    # Check if it was a local model (not Gemini fallback)
                    model_used = result.get('model', '')
                    is_local = 'LOCAL' in model_used or 'qwen2-vl' in model_used.lower() or 'llava' in model_used.lower()
                    
                    if is_local:
                        print(f"   ✅ SUCCESS with LOCAL model: {result['model']}")
                    else:
                        print(f"   ℹ️ Used fallback: {result['model']}")
                    
                    # Build analysis text
                    analysis_text = f"--- Vision Analysis ({result['model']}) ---\n"
                    analysis_text += f"Document Type: {document_type}\n\n"
                    analysis_text += f"{result['extracted_text']}\n"
                    
                    # Add structured data if available
                    if 'structured_data' in result and result['structured_data'].get('extracted_fields'):
                        analysis_text += "\n--- Extracted Information ---\n"
                        for key, value in result['structured_data']['extracted_fields'].items():
                            if isinstance(value, list):
                                analysis_text += f"{key}:\n"
                                for item in value:
                                    if isinstance(item, dict):
                                        analysis_text += f"  - {item}\n"
                                    else:
                                        analysis_text += f"  - {item}\n"
                            else:
                                analysis_text += f"{key}: {value}\n"
                    
                    return analysis_text
                else:
                    print(f"   ⚠️ All vision services failed: {result.get('error', 'Unknown')}")
            
            # Fallback to Tesseract OCR
            if OCR_AVAILABLE:
                print(f"   🔄 Falling back to OCR (Tesseract)...")
                ocr_result = ocr_fallback.analyze_medical_document(image, document_type)
                
                if ocr_result.get('success'):
                    analysis_text = f"--- OCR Analysis (Tesseract) ---\n"
                    analysis_text += f"Document Type: {document_type}\n\n"
                    analysis_text += f"{ocr_result['extracted_text']}\n"
                    
                    # Add structured data
                    if 'structured_data' in ocr_result and ocr_result['structured_data'].get('extracted_fields'):
                        analysis_text += "\n--- Extracted Information ---\n"
                        for key, value in ocr_result['structured_data']['extracted_fields'].items():
                            if isinstance(value, list):
                                analysis_text += f"{key}:\n"
                                for item in value:
                                    analysis_text += f"  - {item}\n"
                            else:
                                analysis_text += f"{key}: {value}\n"
                    
                    return analysis_text
            
            # Last resort: Return basic info
            return f"[IMAGE RECEIVED] - Analysis unavailable. Image size: {image.size}, Mode: {image.mode}. Please install vision models or Tesseract OCR for analysis."
            
        except Exception as e:
            print(f"   ❌ Image processing error: {e}")
            return f"[IMAGE PROCESSING ERROR: {str(e)}]"
    
    def _detect_document_type(self, image: Image.Image) -> str:
        """Detect document type from image characteristics"""
        # Basic heuristics - can be enhanced with ML
        width, height = image.size
        aspect_ratio = width / height if height > 0 else 1
        
        # Medical images are often square or specific ratios
        if 0.9 <= aspect_ratio <= 1.1:
            # Square images might be X-rays, CT, MRI
            return "xray"  # Can be refined
        elif aspect_ratio > 1.3:
            # Wide images are often prescriptions or lab reports
            return "prescription"
        
        # Default to general medical document
        return "general"
    
    def extract_medical_info(self, text: str) -> Dict:
        """
        Extract key medical information from processed text
        
        Args:
            text: Extracted text from medical report
            
        Returns:
            Dict with structured medical information
        """
        # Simple keyword extraction for medical terms
        medical_keywords = {
            'conditions': ['diabetes', 'hypertension', 'cholesterol', 'asthma', 'arthritis', 'cancer', 'heart disease'],
            'medications': ['mg', 'tablet', 'capsule', 'injection', 'dose', 'prescription'],
            'vitals': ['blood pressure', 'heart rate', 'temperature', 'weight', 'height', 'bmi'],
            'lab_values': ['glucose', 'cholesterol', 'hemoglobin', 'creatinine', 'alt', 'ast']
        }
        
        found_info = {}
        text_lower = text.lower()
        
        for category, keywords in medical_keywords.items():
            found_info[category] = []
            for keyword in keywords:
                if keyword in text_lower:
                    found_info[category].append(keyword)
        
        return {
            "extracted_conditions": found_info.get('conditions', []),
            "extracted_medications": found_info.get('medications', []),
            "extracted_vitals": found_info.get('vitals', []),
            "extracted_lab_values": found_info.get('lab_values', []),
            "text_preview": text[:500] + "..." if len(text) > 500 else text
        }

