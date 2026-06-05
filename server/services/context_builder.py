from typing import List, Dict, Optional
from datetime import datetime, timedelta
from bson import ObjectId
import re

class MedicalContextBuilder:
    """Builds medical context from user history for AI responses"""
    
    def __init__(self, db):
        self.db = db
    
    def get_user_medical_context(self, user_id: str, limit: int = 10) -> str:
        """Get user's medical context from recent history with intelligent extraction"""
        try:
            # Convert string user_id to ObjectId
            user_object_id = ObjectId(user_id)

            # Get recent medical history items
            history_items = list(
                self.db.medical_histories.find(
                    {"userId": user_object_id}
                ).sort("createdAt", -1).limit(limit)
            )

            if not history_items:
                return "No previous medical history available."

            # Build intelligent context
            context_parts = []
            user_conditions = []
            user_medications = []
            user_allergies = []
            
            for item in history_items:
                source_type = item.get("sourceType", "unknown")
                summary = item.get("summaryText_plain", "")
                created_date = item.get("createdAt", "")
                extracted = item.get("extracted", {})

                # Extract medical conditions from chat summaries
                if source_type == "chat" and summary:
                    # Look for medical conditions in chat text
                    conditions = self._extract_conditions_from_text(summary)
                    if conditions:
                        user_conditions.extend(conditions)

                # Use extracted structured data if available
                if extracted.get("conditions"):
                    user_conditions.extend(extracted["conditions"])
                if extracted.get("medications"):
                    user_medications.extend(extracted["medications"])
                if extracted.get("allergies"):
                    user_allergies.extend(extracted["allergies"])

            # Build personalized context
            if user_conditions:
                context_parts.append(f"**Your Medical Conditions**: {', '.join(set(user_conditions))}")
            
            if user_medications:
                context_parts.append(f"**Your Medications**: {', '.join(set(user_medications))}")
            
            if user_allergies:
                context_parts.append(f"**Your Allergies**: {', '.join(set(user_allergies))}")

            # Add recent chat summaries for context
            recent_chats = [item for item in history_items if item.get("sourceType") == "chat"][:3]
            for item in recent_chats:
                summary = item.get("summaryText_plain", "")
                if summary:
                    context_parts.append(f"**Recent Chat**: {summary}")

            return "\n\n".join(context_parts)

        except Exception as e:
            print(f"Error building medical context: {e}")
            return "Unable to retrieve medical history at this time."
    
    def get_relevant_conditions(self, user_id: str) -> List[str]:
        """Extract relevant medical conditions from user history"""
        try:
            user_object_id = ObjectId(user_id)
            
            # Get conditions from medical history
            conditions = []
            history_items = self.db.medical_histories.find(
                {"userId": user_object_id, "extracted.conditions": {"$exists": True}}
            )
            
            for item in history_items:
                extracted = item.get("extracted", {})
                if extracted.get("conditions"):
                    conditions.extend(extracted["conditions"])
            
            # Remove duplicates and return
            return list(set(conditions))
            
        except Exception as e:
            print(f"Error getting conditions: {e}")
            return []
    
    def get_medications(self, user_id: str) -> List[str]:
        """Get user's current medications"""
        try:
            user_object_id = ObjectId(user_id)
            
            medications = []
            history_items = self.db.medical_histories.find(
                {"userId": user_object_id, "extracted.medications": {"$exists": True}}
            )
            
            for item in history_items:
                extracted = item.get("extracted", {})
                if extracted.get("medications"):
                    medications.extend(extracted["medications"])
            
            return list(set(medications))
            
        except Exception as e:
            print(f"Error getting medications: {e}")
            return []
    
    def get_allergies(self, user_id: str) -> List[str]:
        """Get user's known allergies"""
        try:
            user_object_id = ObjectId(user_id)
            
            allergies = []
            history_items = self.db.medical_histories.find(
                {"userId": user_object_id, "extracted.allergies": {"$exists": True}}
            )
            
            for item in history_items:
                extracted = item.get("extracted", {})
                if extracted.get("allergies"):
                    allergies.extend(extracted["allergies"])
            
            return list(set(allergies))
            
        except Exception as e:
            print(f"Error getting allergies: {e}")
            return []
    
    def calculate_age(self, date_of_birth: str) -> Optional[int]:
        """Calculate age from date of birth"""
        try:
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    dob = datetime.strptime(date_of_birth, fmt)
                    today = datetime.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    return age
                except:
                    continue
            return None
        except:
            return None
    
    def get_recent_vitals_labs(self, user_id: str) -> Dict:
        """Get most recent vitals and lab values"""
        try:
            user_object_id = ObjectId(user_id)
            
            # Get most recent history entry with vitals or labs
            recent = self.db.medical_histories.find_one(
                {
                    "userId": user_object_id,
                    "$or": [
                        {"extracted.vitals": {"$ne": {}}},
                        {"extracted.labs": {"$ne": {}}}
                    ]
                },
                sort=[("createdAt", -1)]
            )
            
            if recent:
                extracted = recent.get('extracted', {})
                return {
                    'vitals': extracted.get('vitals', {}),
                    'labs': extracted.get('labs', {}),
                    'date': recent.get('createdAt')
                }
            return {'vitals': {}, 'labs': {}, 'date': None}
            
        except Exception as e:
            print(f"Error getting recent vitals/labs: {e}")
            return {'vitals': {}, 'labs': {}, 'date': None}
    
    def build_structured_context(self, user_id: str) -> Dict:
        """Build comprehensive structured medical context for AI"""
        try:
            user_object_id = ObjectId(user_id)
            
            # Get user profile
            user = self.db.users.find_one({'_id': user_object_id})
            
            context = {
                "medical_history": self.get_user_medical_context(user_id),
                "conditions": self.get_relevant_conditions(user_id),
                "medications": self.get_medications(user_id),
                "allergies": self.get_allergies(user_id),
                "demographics": {},
                "recent_vitals": {},
                "recent_labs": {},
                "context_summary": ""
            }
            
            # Add demographics if available
            if user:
                demographics = {}
                
                # Age
                if user.get('dateOfBirth'):
                    age = self.calculate_age(user['dateOfBirth'])
                    if age:
                        demographics['age'] = age
                
                # Blood type
                if user.get('bloodType'):
                    demographics['bloodType'] = user['bloodType']
                
                context["demographics"] = demographics
            
            # Get recent vitals and labs
            recent_data = self.get_recent_vitals_labs(user_id)
            context["recent_vitals"] = recent_data.get('vitals', {})
            context["recent_labs"] = recent_data.get('labs', {})
            
            # Create enhanced summary
            summary_parts = []
            
            # Add age and blood type
            if context["demographics"]:
                demo = context["demographics"]
                if 'age' in demo:
                    summary_parts.append(f"Patient is {demo['age']} years old")
                if 'bloodType' in demo:
                    summary_parts.append(f"Blood type: {demo['bloodType']}")
            
            # Add conditions
            if context["conditions"]:
                summary_parts.append(f"Known conditions: {', '.join(context['conditions'])}")
            
            # Add medications
            if context["medications"]:
                summary_parts.append(f"Current medications: {', '.join(context['medications'])}")
            
            # Add allergies
            if context["allergies"]:
                summary_parts.append(f"Known allergies: {', '.join(context['allergies'])}")
            
            # Add recent vitals
            if context["recent_vitals"]:
                vitals_summary = []
                if 'bloodPressure' in context["recent_vitals"]:
                    vitals_summary.append(f"BP: {context['recent_vitals']['bloodPressure']}")
                if 'heartRate' in context["recent_vitals"]:
                    vitals_summary.append(f"HR: {context['recent_vitals']['heartRate']}")
                if vitals_summary:
                    summary_parts.append(f"Recent vitals: {', '.join(vitals_summary)}")
            
            # Add recent labs
            if context["recent_labs"]:
                labs_summary = []
                if 'HbA1c' in context["recent_labs"]:
                    labs_summary.append(f"HbA1c: {context['recent_labs']['HbA1c']}")
                if 'glucose' in context["recent_labs"]:
                    labs_summary.append(f"Glucose: {context['recent_labs']['glucose']}")
                if labs_summary:
                    summary_parts.append(f"Recent labs: {', '.join(labs_summary)}")
            
            context["context_summary"] = ". ".join(summary_parts) + "." if summary_parts else ""
            
            return context
            
        except Exception as e:
            print(f"Error building structured context: {e}")
            return {
                "medical_history": "Unable to retrieve medical history.",
                "conditions": [],
                "medications": [],
                "allergies": [],
                "demographics": {},
                "recent_vitals": {},
                "recent_labs": {},
                "context_summary": "Context unavailable."
            }

    def _extract_conditions_from_text(self, text: str) -> List[str]:
        """Intelligently extract medical conditions from chat text"""
        text_lower = text.lower()
        conditions = []
        
        # Common medical conditions to look for
        condition_keywords = {
            'diabetes': ['diabetes', 'diabetic', 'blood sugar', 'insulin'],
            'cholesterol': ['cholesterol', 'colestral', 'lipid', 'hdl', 'ldl'],
            'hypertension': ['hypertension', 'high blood pressure', 'bp'],
            'asthma': ['asthma', 'breathing', 'respiratory'],
            'arthritis': ['arthritis', 'joint pain', 'rheumatoid'],
            'depression': ['depression', 'anxiety', 'mental health'],
            'obesity': ['obesity', 'overweight', 'weight gain'],
            'heart disease': ['heart disease', 'cardiac', 'cardiovascular']
        }
        
        for condition, keywords in condition_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                conditions.append(condition)
        
        return conditions

def build_context(db, user_id: str, limit: int = 5) -> str:
    """Legacy function for backward compatibility"""
    builder = MedicalContextBuilder(db)
    return builder.get_user_medical_context(user_id, limit)
