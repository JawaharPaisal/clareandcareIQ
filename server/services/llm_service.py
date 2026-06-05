"""
Local LLM Service using MedAlpaca GGUF
Handles medical Q&A and chat functionality
Primary service with Gemini as fallback
"""

import os
import re
import random
from typing import Dict, List, Optional
from llama_cpp import Llama

class LocalLLMService:
    """Medical chatbot using MedAlpaca GGUF model"""
    
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
        self.model_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'MedAlpaca-7B GGU', 
            'Med-Alpaca-2-7b-chat.Q4_K_M.gguf'
        )
        self.llm = None
        self.use_model = False
        
        print(f"🔧 Local LLM Service Initialization:")
        print(f"   Model Path: {self.model_path}")
        
        try:
            if os.path.exists(self.model_path):
                print(f"   ✅ Model file found")
                self._load_model()
            else:
                print(f"   ⚠️ Model file not found, LLM disabled")
        except Exception as e:
            print(f"   ❌ Error loading LLM: {e}")
            self.use_model = False
    
    def _load_model(self):
        """Load the GGUF model"""
        try:
            print("   🚀 Loading MedAlpaca model...")
            
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=2048,  # Context window
                n_threads=4,  # Number of CPU threads
                n_gpu_layers=0,  # Set to > 0 if you have GPU
                verbose=False
            )
            
            self.use_model = True
            print("   ✅ MedAlpaca model loaded successfully!")
            
        except Exception as e:
            print(f"   ❌ Failed to load model: {e}")
            self.use_model = False
    
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

Remember: Respond in ~30 words, match tone to context, and end with a yes/no question.

RESPONSE:"""

        return system_prompt.format(
            user_context=user_context if user_context else "No previous medical history available.",
            conversation_history=conversation_history if conversation_history else "This is the start of the conversation.",
            user_message=user_message
        )
    
    def ask_medical_question(self, user_message: str, user_context: str = "", conversation_history: str = "") -> Dict:
        """
        Ask a medical question and get AI response
        
        Args:
            user_message: User's question
            user_context: Medical context about the user
            conversation_history: Recent conversation for context
            
        Returns:
            Dictionary with reply and metadata
        """
        print(f"🤖 LLM Question Processing:")
        print(f"   Message: {user_message[:50]}...")
        print(f"   Context: {'✅ Available' if user_context else '❌ None'}")
        print(f"   Using Model: {self.use_model}")
        
        if not self.use_model or not self.llm:
            print("   🔄 LLM not available, returning fallback signal")
            return {
                "reply": None,  # Signal to use fallback
                "used_context": bool(user_context),
                "model": "fallback_needed",
                "success": False
            }
        
        try:
            print("   🚀 Calling MedAlpaca...")
            
            # Create the medical prompt
            prompt = self.create_medical_prompt(user_message, user_context, conversation_history)
            
            # Generate response (reduced max_tokens for shorter responses)
            response = self.llm(
                prompt,
                max_tokens=150,  # Reduced for shorter responses
                temperature=0.8,  # Slightly higher for more natural conversation
                top_p=0.9,
                repeat_penalty=1.1,
                stop=["USER:", "ASSISTANT:", "###", "\n\n"]  # Fixed stop sequences
            )
            
            # Extract text from response
            ai_reply = response['choices'][0]['text'].strip()
            
            # Check if response is too short or empty (lowered threshold for shorter responses)
            if not ai_reply or len(ai_reply) < 20:
                print(f"   ⚠️ Response too short ({len(ai_reply) if ai_reply else 0} chars): '{ai_reply}'")
                return {
                    "reply": None,
                    "used_context": bool(user_context),
                    "model": "fallback_needed",
                    "success": False
                }
            
            # Post-process to ensure short response with yes/no question
            processed_reply = self.process_response(ai_reply, user_message)
            print(f"   ✅ MedAlpaca response: {len(processed_reply)} characters (processed)")
            
            return {
                "reply": processed_reply,
                "used_context": bool(user_context),
                "model": "medalpaca-7b-gguf",
                "tokens_used": response['usage']['total_tokens'],
                "success": True
            }
            
        except Exception as e:
            print(f"   ❌ LLM error: {e}")
            return {
                "reply": None,
                "used_context": bool(user_context),
                "model": "fallback_needed",
                "error": str(e),
                "success": False
            }
    
    def summarize_chat_session(self, messages: List[Dict]) -> Optional[str]:
        """
        Summarize a chat session
        
        Args:
            messages: List of chat messages
            
        Returns:
            Summary text or None if failed
        """
        if not self.use_model or not self.llm:
            return None
        
        try:
            # Create summary from messages
            chat_text = "\n".join([
                f"{msg['sender']}: {msg['text']}" 
                for msg in messages
            ])
            
            summary_prompt = f"""Summarize this medical consultation in 2-3 sentences for medical records:

{chat_text}

Summary:"""
            
            response = self.llm(
                summary_prompt,
                max_tokens=150,
                temperature=0.5,
                stop=["\n\n"]
            )
            
            summary = response['choices'][0]['text'].strip()
            return summary if summary else None
            
        except Exception as e:
            print(f"   ❌ Summarization error: {e}")
            return None
    
    def analyze_report(self, report_text: str, filename: str, user_context: str = "") -> Optional[str]:
        """
        Analyze medical report and provide summary
        
        Args:
            report_text: Text extracted from report
            filename: Name of the report file
            user_context: User's medical context
            
        Returns:
            AI analysis summary or None if failed
        """
        if not self.use_model or not self.llm:
            return None
        
        try:
            context_info = f"\n\nPatient Context: {user_context}" if user_context else ""
            
            analysis_prompt = f"""Analyze this medical report and provide a clear summary:

Report: {filename}
{context_info}

Report Content:
{report_text[:2000]}  

Provide:
1. Key findings
2. Important values or results
3. Any concerns or abnormalities
4. Recommendations

Analysis:"""
            
            response = self.llm(
                analysis_prompt,
                max_tokens=512,
                temperature=0.7,
                stop=["\n\n\n"]
            )
            
            analysis = response['choices'][0]['text'].strip()
            return analysis if analysis else None
            
        except Exception as e:
            print(f"   ❌ Report analysis error: {e}")
            return None


# Global instance
local_llm = LocalLLMService()


