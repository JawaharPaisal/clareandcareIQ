"""
Medical Named Entity Recognition Service
Uses biomedical-ner-all model to extract medical entities from text
Replaces manual regex patterns with AI-powered extraction
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from services.vitals_labs_extractor import vitals_labs_extractor

class MedicalNERService:
    """Extract medical entities using biomedical-ner-all model"""
    
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), '..', 'biomedical-ner-all')
        self.model = None
        self.tokenizer = None
        self.ner_pipeline = None
        self.use_model = False
        
        print(f"🔧 Medical NER Service Initialization:")
        print(f"   Model Path: {self.model_path}")
        
        try:
            # Check if model files exist
            if os.path.exists(self.model_path):
                print(f"   ✅ Model directory found")
                self._load_model()
            else:
                print(f"   ⚠️ Model directory not found, NER disabled")
        except Exception as e:
            print(f"   ❌ Error loading NER model: {e}")
            self.use_model = False
    
    def _load_model(self):
        """Load the NER model and tokenizer"""
        try:
            print("   🚀 Loading NER model...")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForTokenClassification.from_pretrained(self.model_path)
            
            # Create NER pipeline
            self.ner_pipeline = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                aggregation_strategy="simple",
                device=-1  # Use CPU (-1) or change to 0 for GPU
            )
            
            self.use_model = True
            print("   ✅ NER model loaded successfully!")
            
        except Exception as e:
            print(f"   ❌ Failed to load NER model: {e}")
            self.use_model = False
    
    def extract_entities(self, text: str) -> Dict[str, List[Dict]]:
        """
        Extract medical entities from text
        
        Returns:
            {
                'conditions': [...],
                'medications': [...],
                'allergies': [...]
            }
        """
        if not self.use_model or not self.ner_pipeline:
            return {'conditions': [], 'medications': [], 'allergies': []}
        
        try:
            # Run NER pipeline
            entities = self.ner_pipeline(text)
            
            # Categorize entities
            categorized = {
                'conditions': [],
                'medications': [],
                'allergies': []
            }
            
            for entity in entities:
                entity_type = entity.get('entity_group', '').upper()
                entity_text = entity.get('word', '').strip()
                score = entity.get('score', 0.0)
                
                # Debug logging
                print(f"      Entity: '{entity_text}' Type: '{entity_type}' Score: {score:.2f}")
                
                # Skip subword tokens (tokenization artifacts)
                if entity_text.startswith('##') or entity_text.startswith('Ġ'):
                    print(f"         → Skipped (subword token)")
                    continue
                
                # Skip generic/non-specific words
                skip_words = ['allergic', 'high', 'low', 'elevated', 'normal', 'abnormal', 
                             'positive', 'negative', 'test', 'result', 'have', 'has', 'had']
                if entity_text.lower() in skip_words or len(entity_text) < 3:
                    print(f"         → Skipped (generic word or too short)")
                    continue
                
                # Lower confidence threshold and broader type matching
                if score < 0.5:  # Lowered from 0.7
                    continue
                
                # Categorize based on entity type
                entity_data = {
                    'name': entity_text.title(),
                    'mentioned_date': datetime.utcnow(),
                    'source': 'ner',
                    'confidence': float(round(score, 2))  # Convert numpy float to Python float
                }
                
                # More flexible entity type mapping
                entity_type_lower = entity_type.lower()
                text_lower = entity_text.lower()
                
                # Conditions/Diseases - check entity type OR text content
                condition_keywords = ['diabetes', 'hypertension', 'asthma', 'arthritis', 'cancer', 
                                     'heart attack', 'stroke', 'infection', 'disease', 'disorder',
                                     'syndrome', 'blood sugar', 'high sugar', 'bloodsugar', 'glucose',
                                     'cholesterol', 'pressure', 'bloodpressure', 'fever', 'pain', 'migraine']
                
                medication_keywords = ['metformin', 'aspirin', 'insulin', 'ibuprofen', 'paracetamol',
                                      'antibiotic', 'medicine', 'pill', 'tablet', 'drug',
                                      'lisinopril', 'atorvastatin', 'amlodipine', 'levothyroxine']
                
                allergy_keywords = ['penicillin', 'peanut', 'latex', 'sulfa', 'shellfish',
                                   'allerg', 'allergic', 'reaction']
                
                # Check text content first (most reliable)
                if any(keyword in text_lower for keyword in condition_keywords):
                    categorized['conditions'].append(entity_data)
                    print(f"         → Categorized as CONDITION (keyword match)")
                elif any(keyword in text_lower for keyword in medication_keywords):
                    categorized['medications'].append(entity_data)
                    print(f"         → Categorized as MEDICATION (keyword match)")
                elif any(keyword in text_lower for keyword in allergy_keywords):
                    categorized['allergies'].append(entity_data)
                    print(f"         → Categorized as ALLERGY (keyword match)")
                # Then check entity type
                elif any(word in entity_type_lower for word in ['disease', 'disorder', 'symptom', 'condition', 'syndrome', 'sign_symptom']):
                    categorized['conditions'].append(entity_data)
                    print(f"         → Categorized as CONDITION (type match)")
                elif any(word in entity_type_lower for word in ['drug', 'medication', 'chemical', 'medicine', 'pharmacologic']):
                    categorized['medications'].append(entity_data)
                    print(f"         → Categorized as MEDICATION (type match)")
                elif any(word in entity_type_lower for word in ['allergy', 'adverse', 'reaction']):
                    categorized['allergies'].append(entity_data)
                    print(f"         → Categorized as ALLERGY (type match)")
                else:
                    print(f"         → Not categorized (type: {entity_type})")
            
            # Remove duplicates
            for category in categorized:
                seen = set()
                unique_entities = []
                for entity in categorized[category]:
                    name_lower = entity['name'].lower()
                    if name_lower not in seen:
                        seen.add(name_lower)
                        unique_entities.append(entity)
                categorized[category] = unique_entities
            
            print(f"   🔍 NER Extracted: {len(categorized['conditions'])} conditions, "
                  f"{len(categorized['medications'])} medications, "
                  f"{len(categorized['allergies'])} allergies")
            
            return categorized
            
        except Exception as e:
            print(f"   ❌ NER extraction error: {e}")
            return {'conditions': [], 'medications': [], 'allergies': []}
    
    def extract_medical_info(self, message: str, user_id: str) -> Dict[str, Any]:
        """
        Extract medical information from a message (replaces old regex method)
        Enhanced with keyword matching for common misspellings
        
        Args:
            message: User's message text
            user_id: User ID for logging
            
        Returns:
            Dictionary with extracted medical information
        """
        print(f"🔍 Extracting medical entities from message (User: {user_id[:8]}...)")
        
        entities = self.extract_entities(message)
        
        # Additional keyword-based extraction for common terms (handles misspellings)
        message_lower = message.lower()
        
        # Cholesterol (common misspellings)
        if any(word in message_lower for word in ['cholesterol', 'colesterol', 'cholestrol', 'colestrol']):
            # Add if not already detected
            if not any(e['name'].lower() == 'cholesterol' for e in entities['conditions']):
                entities['conditions'].append({
                    'name': 'Cholesterol',
                    'mentioned_date': datetime.utcnow(),
                    'source': 'keyword',
                    'confidence': 0.95
                })
                print(f"      Keyword Match: 'Cholesterol' (misspelling corrected)")
        
        # Diabetes
        if 'diabetes' in message_lower or 'diabetic' in message_lower:
            if not any(e['name'].lower() == 'diabetes' for e in entities['conditions']):
                entities['conditions'].append({
                    'name': 'Diabetes',
                    'mentioned_date': datetime.utcnow(),
                    'source': 'keyword',
                    'confidence': 0.95
                })
                print(f"      Keyword Match: 'Diabetes'")
        
        # Hypertension (include variations and misspellings)
        if any(word in message_lower for word in ['hypertension', 'high blood pressure', 'high bp', 'bloodpressure', 'blood pressure']):
            # Replace any existing "bloodpressure" entries with "Hypertension"
            entities['conditions'] = [e for e in entities['conditions'] 
                                     if 'pressure' not in e['name'].lower()]
            
            if not any(e['name'].lower() == 'hypertension' for e in entities['conditions']):
                entities['conditions'].append({
                    'name': 'Hypertension',
                    'mentioned_date': datetime.utcnow(),
                    'source': 'keyword',
                    'confidence': 0.95
                })
                print(f"      Keyword Match: 'Hypertension' (normalized)")
        
        # Asthma
        if 'asthma' in message_lower:
            if not any(e['name'].lower() == 'asthma' for e in entities['conditions']):
                entities['conditions'].append({
                    'name': 'Asthma',
                    'mentioned_date': datetime.utcnow(),
                    'source': 'keyword',
                    'confidence': 0.95
                })
                print(f"      Keyword Match: 'Asthma'")
        
        # Heart Disease
        if any(word in message_lower for word in ['heart disease', 'heart attack', 'cardiac']):
            if not any('heart' in e['name'].lower() for e in entities['conditions']):
                entities['conditions'].append({
                    'name': 'Heart Disease',
                    'mentioned_date': datetime.utcnow(),
                    'source': 'keyword',
                    'confidence': 0.90
                })
                print(f"      Keyword Match: 'Heart Disease'")
        
        return {
            'conditions': entities['conditions'],
            'medications': entities['medications'],
            'allergies': entities['allergies'],
            'timestamp': datetime.utcnow()
        }
    
    def analyze_report_text(self, report_text: str) -> Dict[str, Any]:
        """
        Extract medical entities from a report including vitals and labs
        
        Args:
            report_text: Text extracted from medical report
            
        Returns:
            Dictionary with extracted entities including vitals and labs
        """
        print(f"🔍 Analyzing report text ({len(report_text)} characters)")
        
        # Extract named entities (conditions, medications, allergies)
        entities = self.extract_entities(report_text)
        
        # Extract vitals and lab values
        vitals_labs = vitals_labs_extractor.extract_all(report_text)
        vitals = vitals_labs.get('vitals', {})
        labs = vitals_labs.get('labs', {})
        
        # Check for abnormal values
        warnings = vitals_labs_extractor.check_abnormal_values(vitals, labs)
        
        print(f"   ✅ Extracted: {len(vitals)} vitals, {len(labs)} lab values")
        if warnings:
            print(f"   ⚠️ Found {len(warnings)} abnormal values")
        
        return {
            'extracted': {
                'conditions': entities['conditions'],
                'medications': entities['medications'],
                'allergies': entities['allergies'],
                'vitals': vitals,
                'labs': labs
            },
            'entity_count': {
                'conditions': len(entities['conditions']),
                'medications': len(entities['medications']),
                'allergies': len(entities['allergies']),
                'vitals': len(vitals),
                'labs': len(labs)
            },
            'abnormal_values': warnings
        }


# Global instance
medical_ner = MedicalNERService()


