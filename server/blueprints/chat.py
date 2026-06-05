from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from bson import ObjectId
import json
from middleware.consent_middleware import require_consent, require_full_consent

# Import services using current_app context
chat_bp = Blueprint('chat', __name__)

def get_gemini_service():
    """Get Gemini service from current app context"""
    from services.gemini_service import ask_medical_question, summarize_chat_session
    return ask_medical_question, summarize_chat_session

def get_context_builder():
    """Get context builder from current app context"""
    from services.context_builder import MedicalContextBuilder
    return MedicalContextBuilder

def get_medical_context_service():
    """Get medical context service from current app context"""
    from services.medical_context_service import MedicalContextService
    return MedicalContextService

def is_medical_query(message: str) -> bool:
    """
    Validate if a query is medical-related
    Returns True if medical, False if non-medical
    """
    message_lower = message.lower()
    
    # Medical keywords (accept these queries)
    medical_keywords = [
        # Symptoms & conditions
        'pain', 'ache', 'fever', 'symptom', 'sick', 'ill', 'hurt', 'sore',
        'headache', 'cough', 'cold', 'nausea', 'dizzy', 'tired', 'fatigue',
        'diabetes', 'cholesterol', 'hypertension', 'asthma', 'cancer',
        'heart', 'blood pressure', 'disease', 'condition', 'disorder',
        'infection', 'allergy', 'allergic', 'chronic',
        
        # Medical terms
        'medicine', 'medication', 'pill', 'drug', 'prescription', 'dose',
        'treatment', 'therapy', 'doctor', 'hospital', 'clinic', 'test',
        'lab', 'report', 'diagnosis', 'scan', 'x-ray', 'blood test',
        'medical', 'health', 'healthcare',
        
        # Body parts
        'stomach', 'chest', 'back', 'leg', 'arm', 'head', 'eye', 'ear',
        'throat', 'lung', 'kidney', 'liver', 'heart', 'brain', 'skin',
        'bone', 'joint', 'muscle', 'blood', 'body',
        
        # Health topics
        'diet', 'nutrition', 'exercise', 'sleep', 'weight', 'vitamin',
        'supplement', 'wellness', 'fitness', 'sugar', 'bp', 'pressure'
    ]
    
    # Non-medical keywords (reject these queries)
    non_medical_keywords = [
        'petrol', 'price', 'cost', 'cricket', 'match', 'weather', 
        'news', 'politics', 'movie', 'song', 'recipe', 'cooking',
        'travel', 'hotel', 'flight', 'train', 'car', 'bike',
        'football', 'sports', 'game', 'shopping', 'fashion',
        'stocks', 'market', 'business', 'job', 'salary'
    ]
    
    # Greetings are always allowed
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 
                 'good evening', 'thanks', 'thank you', 'bye', 'goodbye']
    if message_lower.strip() in greetings:
        return True
    
    # Short responses (follow-ups) are allowed
    simple_responses = ['yes', 'no', 'okay', 'ok', 'sure', 'yeah', 
                       'nope', 'yep', 'nah', 'maybe', 'not really']
    if message_lower.strip() in simple_responses or len(message.split()) <= 3:
        return True
    
    # Check for non-medical keywords first (higher priority)
    if any(keyword in message_lower for keyword in non_medical_keywords):
        return False
    
    # Check for medical keywords
    if any(keyword in message_lower for keyword in medical_keywords):
        return True
    
    # Default: Allow query (to avoid blocking valid medical questions)
    # Can be changed to False for stricter filtering
    return True

@chat_bp.route('/', methods=['POST'])
@jwt_required()
@require_consent('ai_analysis')
def chat_with_ai():
    """Chat with Clare AI using medical context"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Validate if query is medical-related
        if not is_medical_query(user_message):
            print(f"⚠️  Non-medical query blocked: '{user_message}'")
            return jsonify({
                "reply": "I'm Clare, your medical AI assistant. I specialize in health and medical topics. I can help you with symptoms, medications, medical reports, and health questions. How can I assist you with your health today?",
                "session_id": data.get('session_id'),
                "used_context": False,
                "model": "validation_filter",
                "timestamp": datetime.utcnow().isoformat()
            }), 200
        
        db = current_app.db
        
        # Extract medical information from user message
        medical_context_service = get_medical_context_service()(db)
        extracted_info = medical_context_service.extract_medical_info(user_message, user_id)
        
        print(f"🔍 DEBUG: User message: '{user_message}'")
        print(f"🔍 DEBUG: User ID: {user_id}")
        print(f"🔍 DEBUG: Extracted medical info: {extracted_info}")
        
        # Update user's medical profile with extracted information
        if extracted_info['conditions'] or extracted_info['medications'] or extracted_info['allergies']:
            print(f"🔍 DEBUG: Updating medical profile...")
            success = medical_context_service.update_medical_profile(user_id, extracted_info)
            print(f"🔍 DEBUG: Medical profile update result: {success}")
        else:
            print(f"🔍 DEBUG: No medical information to update")
        
        # Get user's current medical profile for AI context
        user_medical_profile = medical_context_service.get_medical_profile(user_id)
        print(f"🔍 DEBUG: Retrieved medical profile: {user_medical_profile}")
        
        # Build comprehensive medical context for AI response
        medical_context = ""
        if user_medical_profile:
            context_parts = []
            
            # Add conditions context
            if user_medical_profile.get('conditions') and len(user_medical_profile['conditions']) > 0:
                conditions = [c['name'] for c in user_medical_profile['conditions']]
                context_parts.append(f"User has medical conditions: {', '.join(conditions)}")
                print(f"🔍 DEBUG: Added conditions to context: {conditions}")
            
            # Add medications context
            if user_medical_profile.get('medications') and len(user_medical_profile['medications']) > 0:
                medications = [m['name'] for m in user_medical_profile['medications']]
                context_parts.append(f"User takes medications: {', '.join(medications)}")
                print(f"🔍 DEBUG: Added medications to context: {medications}")
            
            # Add allergies context
            if user_medical_profile.get('allergies') and len(user_medical_profile['allergies']) > 0:
                allergies = [a['name'] for a in user_medical_profile['allergies']]
                context_parts.append(f"User has allergies: {', '.join(allergies)}")
                print(f"🔍 DEBUG: Added allergies to context: {allergies}")
            
            if context_parts:
                medical_context = f"Medical Context: {'; '.join(context_parts)}. Consider these conditions when providing advice."
                print(f"🔍 DEBUG: Final medical context: {medical_context}")
            else:
                print(f"🔍 DEBUG: No medical context to add")
        else:
            print(f"🔍 DEBUG: No medical profile found for user")
        
        # Add report context if user selected a specific report
        selected_report_id = data.get('selected_report_id')
        report_context_used = False
        
        if selected_report_id:
            print(f"📄 User selected report: {selected_report_id}")
            try:
                report = db.reports.find_one({
                    "_id": ObjectId(selected_report_id),
                    "userId": ObjectId(user_id)
                })
                
                if report:
                    report_context = f"\n\nSELECTED MEDICAL REPORT:\n"
                    report_context += f"Report Name: {report.get('reportName', 'Unknown')}\n"
                    report_context += f"Report Type: {report.get('reportType', 'general')}\n"
                    report_context += f"Date: {report.get('createdAt', datetime.utcnow()).strftime('%Y-%m-%d')}\n"
                    report_context += f"\nAI Summary:\n{report.get('aiSummary', 'No summary available')}\n"
                    
                    # Add extracted information if available
                    if 'extracted' in report:
                        extracted = report['extracted']
                        
                        # Handle conditions (can be strings or objects)
                        if extracted.get('conditions'):
                            conditions = []
                            for condition in extracted['conditions']:
                                if isinstance(condition, str):
                                    conditions.append(condition)
                                elif isinstance(condition, dict):
                                    conditions.append(condition.get('name', condition.get('condition', str(condition))))
                                else:
                                    conditions.append(str(condition))
                            report_context += f"\nConditions found: {', '.join(conditions)}\n"
                        
                        # Handle medications (can be strings or objects)
                        if extracted.get('medications'):
                            medications = []
                            for med in extracted['medications']:
                                if isinstance(med, str):
                                    medications.append(med)
                                elif isinstance(med, dict):
                                    medications.append(med.get('name', med.get('medication', str(med))))
                                else:
                                    medications.append(str(med))
                            report_context += f"Medications found: {', '.join(medications)}\n"
                        
                        # Handle blood type
                        if extracted.get('blood_type'):
                            report_context += f"Blood Type: {extracted['blood_type']}\n"
                        
                        # Handle vitals (can be strings, numbers, or objects)
                        if extracted.get('vitals'):
                            vitals = extracted['vitals']
                            report_context += f"\nVital Signs:\n"
                            for key, value in vitals.items():
                                if isinstance(value, (str, int, float)):
                                    report_context += f"  - {key}: {value}\n"
                                elif isinstance(value, dict):
                                    display_value = value.get('value', value.get('measurement', str(value)))
                                    report_context += f"  - {key}: {display_value}\n"
                                else:
                                    report_context += f"  - {key}: {str(value)}\n"
                        
                        # Handle labs (can be strings, numbers, or objects)
                        if extracted.get('labs'):
                            labs = extracted['labs']
                            report_context += f"\nLab Values:\n"
                            for key, value in labs.items():
                                if isinstance(value, (str, int, float)):
                                    report_context += f"  - {key}: {value}\n"
                                elif isinstance(value, dict):
                                    display_value = value.get('value', value.get('measurement', str(value)))
                                    report_context += f"  - {key}: {display_value}\n"
                                else:
                                    report_context += f"  - {key}: {str(value)}\n"
                    
                    # Add extracted text preview (first 500 chars)
                    if 'extractedText' in report:
                        text_preview = report['extractedText'][:500]
                        report_context += f"\nReport Content Preview:\n{text_preview}...\n"
                    
                    medical_context += report_context
                    report_context_used = True
                    print(f"✅ Added report context to conversation")
                else:
                    print(f"⚠️ Report not found: {selected_report_id}")
            except Exception as e:
                print(f"❌ Error loading report context: {e}")
        
        # Build conversation history from session
        conversation_history = ""
        session_id = data.get('session_id')
        
        if session_id:
            # Get existing session to build conversation context
            existing_session = db.chat_sessions.find_one({
                "_id": ObjectId(session_id),
                "userId": ObjectId(user_id)
            })
            
            if existing_session and existing_session.get('messages'):
                # Get last 4 messages (2 exchanges) for context
                recent_messages = existing_session['messages'][-4:]
                conversation_parts = []
                
                for msg in recent_messages:
                    sender = "You" if msg['sender'] == 'bot' else "User"
                    conversation_parts.append(f"{sender}: {msg['text']}")
                
                if conversation_parts:
                    conversation_history = "\n".join(conversation_parts)
                    print(f"🔍 DEBUG: Conversation history built: {len(conversation_parts)} messages")
        
        # Get AI response with medical context and conversation history
        ask_medical_question, summarize_chat_session = get_gemini_service()
        ai_response = ask_medical_question(user_message, medical_context, conversation_history)
        
        # Create chat session if it doesn't exist
        current_time = datetime.utcnow()
        session_id = data.get('session_id')
        
        if session_id:
            # Continue existing session
            chat_session = db.chat_sessions.find_one({
                "_id": ObjectId(session_id),
                "userId": ObjectId(user_id)
            })
            
            if not chat_session:
                return jsonify({"error": "Chat session not found"}), 404
        else:
            # Create new session
            session_doc = {
                "userId": ObjectId(user_id),
                "messages": [],
                "startedAt": current_time,
                "expiresAt": current_time + timedelta(days=7)  # TTL for messages
            }
            result = db.chat_sessions.insert_one(session_doc)
            session_id = str(result.inserted_id)
        
        # Add user message
        user_msg = {
            "sender": "user",
            "text": user_message,
            "ts": current_time
        }
        
        # Add AI response
        ai_msg = {
            "sender": "bot",
            "text": ai_response["reply"],
            "ts": current_time
        }
        
        # Update chat session with both messages
        db.chat_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {
                "$push": {"messages": {"$each": [user_msg, ai_msg]}},
                "$set": {"endedAt": current_time}
            }
        )
        
        # Create medical history entry for this chat
        chat_summary = summarize_chat_session([user_msg, ai_msg])
        
        history_doc = {
            "userId": ObjectId(user_id),
            "sourceType": "chat",
            "summaryText_plain": chat_summary,
            "summaryText_enc": chat_summary,  # For Phase 5 encryption
            "extracted": {
                "conditions": [],
                "allergies": [],
                "medications": [],
                "vitals": {},
                "labs": {}
            },
            "tags": ["chat", "ai-consultation"],
            "createdAt": current_time,
            "chatSessionId": ObjectId(session_id)
        }
        
        db.medical_histories.insert_one(history_doc)
        
        # Return response with session info
        response_data = {
            "reply": ai_response["reply"],
            "session_id": session_id,
            "used_context": ai_response.get("used_context", False),
            "report_context_used": report_context_used,
            "selected_report_id": selected_report_id if report_context_used else None,
            "model": ai_response.get("model", "unknown"),
            "timestamp": current_time.isoformat()
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({"error": "Chat service error"}), 500

@chat_bp.route('/sessions', methods=['GET'])
@jwt_required()
@require_consent('data_storage')
def get_chat_sessions():
    """Get user's chat sessions"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        # Get recent chat sessions
        sessions = list(db.chat_sessions.find(
            {"userId": ObjectId(user_id)}
        ).sort("startedAt", -1).limit(10))
        
        # Convert ObjectIds to strings and add message count
        for session in sessions:
            session['_id'] = str(session['_id'])
            session['userId'] = str(session['userId'])
            # Add message count for frontend display
            session['messageCount'] = len(session.get('messages', []))
            # Don't include full messages in list view to reduce payload
            if 'messages' in session:
                del session['messages']
        
        return jsonify({"sessions": sessions}), 200
        
    except Exception as e:
        print(f"Get sessions error: {e}")
        return jsonify({"error": "Failed to retrieve chat sessions"}), 500

@chat_bp.route('/sessions/<session_id>', methods=['GET'])
@jwt_required()
def get_chat_session(session_id):
    """Get specific chat session with messages"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        # Get chat session
        session = db.chat_sessions.find_one({
            "_id": ObjectId(session_id),
            "userId": ObjectId(user_id)
        })
        
        if not session:
            return jsonify({"error": "Chat session not found"}), 404
        
        # Convert ObjectIds to strings
        session['_id'] = str(session['_id'])
        session['userId'] = str(session['userId'])
        
        return jsonify({"session": session}), 200
        
    except Exception as e:
        print(f"Get session error: {e}")
        return jsonify({"error": "Failed to retrieve chat session"}), 500

@chat_bp.route('/sessions/<session_id>', methods=['DELETE'])
@jwt_required()
def delete_chat_session(session_id):
    """Delete a chat session"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        # Delete chat session
        result = db.chat_sessions.delete_one({
            "_id": ObjectId(session_id),
            "userId": ObjectId(user_id)
        })
        
        if result.deleted_count == 0:
            return jsonify({"error": "Chat session not found"}), 404
        
        # Also delete associated medical history
        db.medical_histories.delete_many({
            "chatSessionId": ObjectId(session_id)
        })
        
        return jsonify({"message": "Chat session deleted successfully"}), 200
        
    except Exception as e:
        print(f"Delete session error: {e}")
        return jsonify({"error": "Failed to delete chat session"}), 500

@chat_bp.route('/context', methods=['GET'])
@jwt_required()
def get_medical_context():
    """Get user's medical context for AI responses"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        # Build comprehensive medical context
        context_builder = get_context_builder()(db)
        context = context_builder.build_structured_context(user_id)
        
        return jsonify({"context": context}), 200
        
    except Exception as e:
        print(f"Get context error: {e}")
        return jsonify({"error": "Failed to retrieve medical context"}), 500

@chat_bp.route('/medical-profile', methods=['GET'])
@jwt_required()
def get_medical_profile():
    """Get user's medical profile"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        medical_context_service = get_medical_context_service()(db)
        profile = medical_context_service.get_medical_profile(user_id)
        
        if not profile:
            return jsonify({
                "conditions": [],
                "medications": [],
                "allergies": []
            }), 200
        
        return jsonify({
            "conditions": profile.get('conditions', []),
            "medications": profile.get('medications', []),
            "allergies": profile.get('allergies', [])
        }), 200
        
    except Exception as e:
        print(f"Get medical profile error: {e}")
        return jsonify({"error": "Failed to retrieve medical profile"}), 500

@chat_bp.route('/medical-profile/condition/<condition_name>', methods=['DELETE'])
@jwt_required()
def delete_condition(condition_name):
    """Delete a specific condition from user's medical profile"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        medical_context_service = get_medical_context_service()(db)
        success = medical_context_service.delete_condition(user_id, condition_name)
        
        if success:
            return jsonify({"message": "Condition deleted successfully"}), 200
        else:
            return jsonify({"error": "Condition not found"}), 404
            
    except Exception as e:
        print(f"Delete condition error: {e}")
        return jsonify({"error": "Failed to delete condition"}), 500

@chat_bp.route('/medical-profile/medication/<medication_name>', methods=['DELETE'])
@jwt_required()
def delete_medication(medication_name):
    """Delete a specific medication from user's medical profile"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        medical_context_service = get_medical_context_service()(db)
        success = medical_context_service.delete_medication(user_id, medication_name)
        
        if success:
            return jsonify({"message": "Medication deleted successfully"}), 200
        else:
            return jsonify({"error": "Medication not found"}), 404
            
    except Exception as e:
        print(f"Delete medication error: {e}")
        return jsonify({"error": "Failed to delete medication"}), 500

@chat_bp.route('/medical-profile/allergy/<allergy_name>', methods=['DELETE'])
@jwt_required()
def delete_allergy(allergy_name):
    """Delete a specific allergy from user's medical profile"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        medical_context_service = get_medical_context_service()(db)
        success = medical_context_service.delete_allergy(user_id, allergy_name)
        
        if success:
            return jsonify({"message": "Allergy deleted successfully"}), 200
        else:
            return jsonify({"error": "Allergy not found"}), 404
            
    except Exception as e:
        print(f"Delete allergy error: {e}")
        return jsonify({"error": "Failed to delete allergy"}), 500

@chat_bp.route('/medical-profile/clear', methods=['DELETE'])
@jwt_required()
def clear_medical_profile():
    """Clear all medical information for a user"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        medical_context_service = get_medical_context_service()(db)
        success = medical_context_service.clear_medical_profile(user_id)
        
        if success:
            return jsonify({"message": "Medical profile cleared successfully"}), 200
        else:
            return jsonify({"error": "No medical profile found"}), 404
            
    except Exception as e:
        print(f"Clear medical profile error: {e}")
        return jsonify({"error": "Failed to clear medical profile"}), 500
