#!/usr/bin/env python3
"""
Medical Report Analysis Service
Uses Local LLM (MedAlpaca) + NER for analysis with Gemini as fallback
"""

import os
from typing import Dict, Optional
from datetime import datetime
from services.gemini_service import MedicalAIService
from services.medical_ner_service import medical_ner
from services.llm_service import local_llm

class ReportAnalyzer:
    """Service for analyzing medical reports using AI"""
    
    def __init__(self):
        self.ai_service = MedicalAIService()
        self.ner_service = medical_ner
        self.llm_service = local_llm
        
        print("🔧 Report Analyzer initialized with:")
        print(f"   Local LLM: {'✅ Available' if self.llm_service.use_model else '❌ Not available'}")
        print(f"   NER Service: {'✅ Available' if self.ner_service.use_model else '❌ Not available'}")
    
    def analyze_medical_report(self, extracted_text: str, filename: str, user_context: str = "") -> Dict:
        """
        Analyze medical report text using Local LLM + NER with Gemini fallback
        
        Args:
            extracted_text: Text extracted from medical report
            filename: Original filename
            user_context: User's medical history context
            
        Returns:
            Dict with AI analysis and summary
        """
        try:
            print(f"📊 Analyzing report: {filename}")
            print(f"   Text length: {len(extracted_text)} characters")
            print(f"   User context: {'✅ Available' if user_context else '❌ None'}")
            
            ai_summary = None
            model_used = "none"
            
            # Try Local LLM first
            if self.llm_service.use_model:
                print("   🚀 Using Local LLM for analysis...")
                ai_summary = self.llm_service.analyze_report(extracted_text, filename, user_context)
                if ai_summary:
                    model_used = "medalpaca-7b-gguf"
                    print(f"   ✅ Local LLM analysis: {len(ai_summary)} characters")
            
            # Fallback to Gemini if Local LLM failed or unavailable
            if not ai_summary:
                print("   🔄 Using Gemini fallback for analysis...")
                analysis_prompt = self._create_report_analysis_prompt(extracted_text, filename, user_context)
                ai_response = self.ai_service.ask_medical_question(analysis_prompt, user_context)
                ai_summary = ai_response.get('reply', 'Unable to analyze report')
                model_used = ai_response.get('model', 'fallback')
                print(f"   ✅ Gemini analysis: {len(ai_summary)} characters")
            
            # Create structured analysis result
            analysis_result = {
                "ai_summary": ai_summary,
                "model_used": model_used,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "filename": filename,
                "text_length": len(extracted_text),
                "has_user_context": bool(user_context),
                "status": "success"
            }
            
            return analysis_result
            
        except Exception as e:
            print(f"   ❌ Report analysis error: {e}")
            return {
                "ai_summary": f"Error analyzing medical report: {str(e)}",
                "model_used": "error",
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "filename": filename,
                "text_length": len(extracted_text),
                "has_user_context": bool(user_context),
                "status": "error",
                "error": str(e)
            }
    
    def _create_report_analysis_prompt(self, extracted_text: str, filename: str, user_context: str) -> str:
        """Create a specialized prompt for medical report analysis"""
        
        prompt = f"""You are analyzing a medical report for a patient. Please provide a comprehensive but concise summary.

**REPORT DETAILS:**
- Filename: {filename}
- Text Length: {len(extracted_text)} characters

**EXTRACTED TEXT:**
{extracted_text[:2000]}{'...' if len(extracted_text) > 2000 else ''}

**PATIENT CONTEXT (if available):**
{user_context if user_context else "No previous medical history available"}

**ANALYSIS REQUIREMENTS:**
Please provide a structured analysis including:

1. **Report Type**: What type of medical report is this? (lab results, imaging, consultation notes, etc.)

2. **Key Findings**: What are the most important medical findings or values?

3. **Normal vs Abnormal**: Which values are within normal ranges and which are concerning?

4. **Recommendations**: What should the patient do next? (follow-up tests, lifestyle changes, etc.)

5. **Summary**: A 2-3 sentence summary in simple terms for the patient.

**IMPORTANT SAFETY NOTES:**
- This is for educational purposes only
- Always recommend consulting a healthcare professional
- Highlight any urgent or concerning findings
- Use clear, non-medical language when possible

Please provide your analysis in a structured format that's easy for a patient to understand."""
        
        return prompt
    
    def generate_medical_history_entry(self, analysis_result: Dict, extracted_text: str) -> Dict:
        """
        Generate a medical history entry from the analysis
        Uses NER to extract medical entities from the report
        
        Args:
            analysis_result: Result from analyze_medical_report
            extracted_text: Original report text
            
        Returns:
            Dictionary suitable for medical_histories collection
        """
        print("📝 Generating medical history entry with NER extraction...")
        
        # Extract medical entities using NER
        ner_analysis = self.ner_service.analyze_report_text(extracted_text)
        
        # Get abnormal values if any
        abnormal_values = ner_analysis.get('abnormal_values', [])
        
        # Generate tags from extracted data
        tags = ["medical-report", "ai-analyzed"]
        if ner_analysis.get('extracted', {}).get('labs'):
            tags.append("lab-results")
        if ner_analysis.get('extracted', {}).get('vitals'):
            tags.append("vitals")
        if abnormal_values:
            tags.append("abnormal-values")
            # Add severity tags
            if any(w.get('level') == 'urgent' for w in abnormal_values):
                tags.append("urgent")
            elif any(w.get('level') == 'concern' for w in abnormal_values):
                tags.append("followup")
        
        # Create medical history document
        history_entry = {
            "sourceType": "report",
            "summaryText_plain": analysis_result.get('ai_summary', ''),
            "summaryText_enc": analysis_result.get('ai_summary', ''),  # For future encryption
            "extracted": ner_analysis.get('extracted', {
                'conditions': [],
                'allergies': [],
                'medications': [],
                'vitals': {},
                'labs': {}
            }),
            "abnormal_values": abnormal_values,
            "tags": tags,
            "createdAt": datetime.utcnow(),
            "metadata": {
                "filename": analysis_result.get('filename', ''),
                "model_used": analysis_result.get('model_used', ''),
                "analysis_timestamp": analysis_result.get('analysis_timestamp', ''),
                "text_length": analysis_result.get('text_length', 0),
                "entity_count": ner_analysis.get('entity_count', {}),
                "has_abnormal_values": len(abnormal_values) > 0
            }
        }
        
        print(f"   ✅ History entry created with {ner_analysis.get('entity_count', {}).get('conditions', 0)} conditions, "
              f"{ner_analysis.get('entity_count', {}).get('medications', 0)} medications, "
              f"{ner_analysis.get('entity_count', {}).get('allergies', 0)} allergies")
        
        return history_entry
