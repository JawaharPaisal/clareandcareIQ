import os
import google.generativeai as genai
from typing import List, Dict, Optional
import json
import re
from services.llm_service import local_llm

# Configure Gemini AI (Fallback only)
USE_MOCK = os.getenv('USE_MOCK_AI', 'false').lower() == 'true'
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class MedicalAIService:
    """
    AI service for medical assistance
    Primary: Local LLM (MedAlpaca)
    Fallback: Google Gemini
    """
    
    # Yes/No question templates for different topics
    QUESTION_TEMPLATES = [
        "Would you like to know more about this?",
        "Are you experiencing any symptoms?",
        "Have you consulted a doctor about this?",
        "Would you like some tips to help?",
        "Is this something you're dealing with currently?",
        "Do you have any specific concerns?",
        "Are you taking any medications for this?",
        "Would you like to discuss this further?"
    ]
    
    def __init__(self):
        self.gemini_model = None
        self.use_mock = USE_MOCK
        self.local_llm = local_llm
        
        print(f"🔧 Medical AI Service Initialization:")
        print(f"   USE_MOCK: {USE_MOCK}")
        print(f"   Local LLM Available: {self.local_llm.use_model}")
        print(f"   GEMINI_API_KEY: {'✅ Set' if GEMINI_API_KEY else '❌ Not Set'}")
        
        # Initialize Gemini as fallback
        if not self.use_mock and GEMINI_API_KEY:
            try:
                print("   🚀 Initializing Gemini as fallback...")
                genai.configure(api_key=GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel("gemini-2.5-pro")
                print("   ✅ Gemini fallback ready!")
            except Exception as e:
                print(f"   ⚠️ Gemini fallback not available: {e}")
                self.gemini_model = None
        
        # Determine service mode
        if self.local_llm.use_model:
            print("   ✅ Using Local LLM as primary service")
        elif self.gemini_model:
            print("   ⚠️ Using Gemini (fallback mode)")
        else:
            print("   ⚠️ Using mock responses only")
    
    def process_response(self, response_text: str, user_message: str) -> str:
        """
        Post-process AI response to ensure it's short and ends with yes/no question
        
        Args:
            response_text: Original AI response
            user_message: User's original message for context
            
        Returns:
            Processed response (~30 words with yes/no question)
        """
        # Clean up the response
        response = response_text.strip()
        
        # Remove any existing disclaimers or long medical advice patterns
        response = re.sub(r'(However|Nevertheless|It\'s important to note|Please note|Disclaimer)[^.]*\.', '', response)
        response = re.sub(r'(Consult|See|Visit) (a|your) (doctor|healthcare professional|physician)[^.]*\.', '', response)
        
        # Check if response already ends with a question mark
        has_question = response.rstrip().endswith('?')
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # If there's already a yes/no question at the end, keep it
        if has_question:
            # Take first sentence or two plus the question
            question_sentence = sentences[-1] if sentences else ""
            other_sentences = sentences[:-1] if len(sentences) > 1 else []
            
            # Build short response
            short_response = ". ".join(other_sentences[:2]) if other_sentences else ""
            if short_response:
                final_response = f"{short_response}. {question_sentence}?"
            else:
                final_response = f"{question_sentence}?"
        else:
            # No question - need to add one
            # Take first 1-2 sentences (keep it under 30 words)
            word_count = 0
            selected_sentences = []
            
            for sentence in sentences:
                words_in_sentence = len(sentence.split())
                if word_count + words_in_sentence < 25:  # Leave room for question
                    selected_sentences.append(sentence)
                    word_count += words_in_sentence
                else:
                    break
            
            if not selected_sentences and sentences:
                # If first sentence is too long, truncate it
                first_sentence = sentences[0]
                words = first_sentence.split()
                selected_sentences = [" ".join(words[:20])]
            
            statement = ". ".join(selected_sentences) if selected_sentences else response[:100]
            
            # Select appropriate yes/no question based on context
            question = self._select_question(user_message, statement)
            final_response = f"{statement}. {question}"
        
        # Final check: if still too long, truncate
        words = final_response.split()
        if len(words) > 40:
            # Keep first ~25 words and add a question
            truncated = " ".join(words[:25])
            question = self._select_question(user_message, truncated)
            final_response = f"{truncated}. {question}"
        
        return final_response.strip()
    
    def _select_question(self, user_message: str, response_statement: str) -> str:
        """Select appropriate yes/no question based on context"""
        message_lower = user_message.lower()
        response_lower = response_statement.lower()
        
        # Context-aware question selection
        if any(word in message_lower for word in ['medication', 'medicine', 'drug', 'pill']):
            return "Are you currently taking any medications for this?"
        elif any(word in message_lower for word in ['symptom', 'pain', 'hurt', 'ache', 'feel']):
            return "Are you experiencing these symptoms now?"
        elif any(word in message_lower for word in ['diabetes', 'cholesterol', 'pressure', 'disease']):
            return "Have you had this checked by a doctor recently?"
        elif any(word in message_lower for word in ['diet', 'food', 'eat', 'nutrition']):
            return "Do you currently track what you eat?"
        elif any(word in message_lower for word in ['exercise', 'workout', 'activity', 'fitness']):
            return "Are you currently physically active?"
        elif 'doctor' in response_lower or 'consult' in response_lower:
            return "Have you seen a doctor about this?"
        else:
            # Default questions
            import random
            return random.choice(self.QUESTION_TEMPLATES)
    
    def create_medical_prompt(self, user_message: str, user_context: str = "", conversation_history: str = "") -> str:
        """Create a medical assistance prompt with safety guidelines"""
        
        system_prompt = """You are "Clare & CareIQ", a friendly and conversational AI medical assistant. Your role is to have natural, engaging conversations about health.

CONVERSATION STYLE:
- Keep responses SHORT (around 30 words maximum)
- Be conversational and empathetic, matching the context appropriately
- ALWAYS end with a YES/NO question to encourage interaction
- If user gives simple answers (yes/no/okay), understand the context and respond naturally
- Never diagnose, prescribe, or give specific medical advice

TONE GUIDELINES:
- When user mentions HEALTH CONDITIONS (diabetes, cholesterol, hypertension, etc.): Show understanding and concern, NOT excitement
  Example: "I understand managing cholesterol can be challenging" (NOT "That's great!")
- When user mentions POSITIVE BEHAVIORS (exercise, healthy eating, tracking): Be encouraging and praise them
  Example: "That's excellent! Regular exercise helps a lot"
- Match your tone to the context - be supportive but not inappropriately cheerful about medical problems

IMPORTANT RULES:
- NEVER diagnose conditions or prescribe treatments
- Keep it brief and conversational
- Always end with an engaging yes/no question
- Be encouraging about positive behaviors, understanding about health challenges
- For serious symptoms, gently suggest seeing a doctor

USER CONTEXT (Medical Profile):
{user_context}

CONVERSATION HISTORY:
{conversation_history}

USER MESSAGE:
{user_message}

Remember: Respond in ~30 words, match tone to context, and end with a yes/no question."""

        return system_prompt.format(
            user_context=user_context if user_context else "No previous medical history available.",
            conversation_history=conversation_history if conversation_history else "This is the start of the conversation.",
            user_message=user_message
        )
    
    def ask_medical_question(self, user_message: str, user_context: str = "", conversation_history: str = "") -> Dict:
        """Ask a medical question and get AI response"""
        
        print(f"🤖 AI Question Processing:")
        print(f"   Message: {user_message[:50]}...")
        print(f"   Context: {'✅ Available' if user_context else '❌ None'}")
        
        # Try Local LLM first
        if self.local_llm.use_model:
            print("   🚀 Trying Local LLM (MedAlpaca)...")
            local_response = self.local_llm.ask_medical_question(user_message, user_context, conversation_history)
            
            if local_response.get('success') and local_response.get('reply'):
                # Post-process the response
                processed_reply = self.process_response(local_response['reply'], user_message)
                print(f"   ✅ Local LLM response: {len(processed_reply)} characters (processed)")
                local_response['reply'] = processed_reply
                return local_response
            else:
                print("   ⚠️ Local LLM failed, trying fallback...")
        
        # Fallback to Gemini
        if not self.use_mock and self.gemini_model:
            try:
                print("   🔄 Using Gemini fallback...")
                prompt = self.create_medical_prompt(user_message, user_context, conversation_history)
                
                response = self.gemini_model.generate_content(prompt)
                ai_reply = response.text if response.text else "I apologize, but I couldn't generate a response at this time."
                
                # Post-process the response
                processed_reply = self.process_response(ai_reply, user_message)
                print(f"   ✅ Gemini response: {len(processed_reply)} characters (processed)")
                
                return {
                    "reply": processed_reply,
                    "used_context": bool(user_context),
                    "model": "gemini-2.5-pro-fallback",
                    "prompt_tokens": getattr(response, 'prompt_token_count', 0),
                    "response_tokens": getattr(response, 'response_token_count', 0),
                    "success": True
                }
                
            except Exception as e:
                print(f"   ❌ Gemini fallback error: {e}")
        
        # Last resort: Fallback response (already short with questions)
        print("   🔄 Using manual fallback response")
        fallback_response = self.get_fallback_response(user_message, user_context, conversation_history)
        return {
            "reply": fallback_response,
            "used_context": bool(user_context),
            "model": "fallback",
            "success": True
        }
    
    def get_fallback_response(self, user_message: str, user_context: str = "", conversation_history: str = "") -> str:
        """Provide intelligent fallback responses for common medical questions"""
        message_lower = user_message.lower()
        
        # Check if it's a simple yes/no answer
        simple_answers = ['yes', 'no', 'yeah', 'nope', 'yep', 'nah', 'ok', 'okay', 'sure', 'not really', 'kind of', 'maybe']
        is_simple_answer = any(message_lower.strip() == ans for ans in simple_answers) or len(user_message.split()) <= 3
        
        # If it's a simple answer, provide contextual follow-up
        if is_simple_answer and conversation_history:
            if 'yes' in message_lower or 'yeah' in message_lower or 'yep' in message_lower or 'ok' in message_lower or 'sure' in message_lower:
                return "That's great to hear! Are you keeping track of your progress regularly?"
            elif 'no' in message_lower or 'nope' in message_lower or 'nah' in message_lower or 'not' in message_lower:
                return "No worries! Would you like some tips to help you get started?"
            else:
                return "I understand. Do you have any specific concerns you'd like to discuss?"
        
        # Check if user has specific medical conditions from context
        has_cholesterol = 'cholesterol' in user_context.lower()
        has_diabetes = 'diabetes' in user_context.lower()
        has_hypertension = 'hypertension' in user_context.lower()
        
        # Diabetes information
        if 'diabetes' in message_lower:
            if has_diabetes:
                return "Since you have diabetes, focus on blood sugar monitoring and balanced meals. Are you checking your levels daily?"
            else:
                return "Diabetes affects blood sugar regulation. Managing it involves diet, exercise, and monitoring. Are you concerned about diabetes risk?"
        
        # Cholesterol information
        elif any(word in message_lower for word in ['cholesterol', 'colestral', 'lipid']):
            if has_cholesterol:
                return "Focus on heart-healthy foods like fruits and vegetables. Are you currently on any cholesterol medication?"
            else:
                return "Cholesterol management involves healthy eating and regular exercise. Have you had your cholesterol checked recently?"
        
        # Diet and nutrition questions
        elif any(word in message_lower for word in ['diet', 'eat', 'food', 'nutrition']):
            return "Balanced meals with fruits, vegetables, and lean proteins work best. Do you currently track what you eat?"
        
        # General health questions
        elif any(word in message_lower for word in ['symptom', 'pain', 'fever', 'headache']):
            return "Track your symptoms including when they occur and severity. Have you noticed any patterns with the symptoms?"
        
        # Default response
        else:
            return "I'm here to help with your health questions! Would you like to know about any specific health topic?"
    
    def summarize_chat_session(self, messages: List[Dict]) -> str:
        """Summarize a chat session for medical history"""
        
        # Try local LLM first
        if self.local_llm.use_model:
            summary = self.local_llm.summarize_chat_session(messages)
            if summary:
                return summary
        
        # Try Gemini fallback
        if not self.use_mock and self.gemini_model:
            try:
                chat_text = "\n".join([
                    f"{msg['sender']}: {msg['text']}" 
                    for msg in messages
                ])
                
                summary_prompt = f"""Summarize this medical consultation in 2-3 sentences for medical records:

{chat_text}

Summary:"""
                
                response = self.gemini_model.generate_content(summary_prompt)
                return response.text if response.text else "Chat session summary unavailable."
                
            except Exception as e:
                print(f"Summary generation error: {e}")
        
        # Manual summary as last resort
        return self._create_manual_summary(messages)
    
    def _create_manual_summary(self, messages: List[Dict]) -> str:
        """Create intelligent summaries manually"""
        if not messages:
            return "Empty chat session"
        
        user_messages = [msg for msg in messages if msg.get('sender') == 'user']
        bot_messages = [msg for msg in messages if msg.get('sender') == 'bot']
        
        if not user_messages:
            return "No user messages in session"
        
        user_text = " ".join([msg.get('text', '') for msg in user_messages]).lower()
        
        conditions = []
        if 'cholesterol' in user_text:
            conditions.append('cholesterol')
        if 'diabetes' in user_text:
            conditions.append('diabetes')
        if 'blood pressure' in user_text or 'hypertension' in user_text:
            conditions.append('hypertension')
        if 'pain' in user_text or 'symptom' in user_text:
            conditions.append('symptoms')
        
        if conditions:
            summary = f"User discussed {', '.join(conditions)}. "
        else:
            summary = "User asked general health questions. "
        
        summary += f"Session included {len(user_messages)} user questions and {len(bot_messages)} AI responses."
        
        return summary


# Global instance
medical_ai = MedicalAIService()

def ask_gemini(prompt: str) -> str:
    """Legacy function for backward compatibility"""
    result = medical_ai.ask_medical_question(prompt)
    return result.get("reply", "No response generated")

def ask_medical_question(user_message: str, user_context: str = "", conversation_history: str = "") -> Dict:
    """Main function to ask medical questions"""
    return medical_ai.ask_medical_question(user_message, user_context, conversation_history)

def summarize_chat_session(messages: List[Dict]) -> str:
    """Summarize chat sessions for medical history"""
    return medical_ai.summarize_chat_session(messages)
