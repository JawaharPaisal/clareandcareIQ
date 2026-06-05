"""
Medical Context Service
Uses AI-powered NER to extract medical entities instead of manual regex patterns
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from bson import ObjectId
from services.medical_ner_service import medical_ner

class MedicalContextService:
    def __init__(self, db):
        self.db = db
        self.users_collection = db.users
        self.ner_service = medical_ner
        
        print("🔧 Medical Context Service initialized with AI-powered NER")

    def extract_medical_info(self, message: str, user_id: str) -> Dict[str, Any]:
        """
        Extract medical information from a chat message using NER
        Replaces old regex-based extraction
        """
        print(f"🔍 DEBUG: Extracting medical info using NER")
        print(f"🔍 DEBUG: User ID: {user_id}")
        print(f"🔍 DEBUG: Message: {message[:100]}...")
        
        # Use NER service to extract entities
        extracted_info = self.ner_service.extract_medical_info(message, user_id)
        
        print(f"🔍 DEBUG: NER Extracted: {len(extracted_info['conditions'])} conditions, "
              f"{len(extracted_info['medications'])} medications, "
              f"{len(extracted_info['allergies'])} allergies")
        
        return extracted_info

    def update_medical_profile(self, user_id: str, extracted_info: Dict[str, Any]) -> bool:
        """Update user's medical profile with extracted information"""
        try:
            print(f"🔍 DEBUG: Updating medical profile for user: {user_id}")
            print(f"🔍 DEBUG: Extracted info: {extracted_info}")
            
            # Get existing user document
            user = self.users_collection.find_one({'_id': ObjectId(user_id)})
            
            if not user:
                print(f"❌ ERROR: User not found: {user_id}")
                return False
            
            print(f"🔍 DEBUG: Found user: {user.get('email', 'Unknown')}")
            
            # Initialize medical fields if they don't exist or convert strings to arrays
            if 'medicalConditions' not in user or not isinstance(user.get('medicalConditions'), list):
                user['medicalConditions'] = []
            if 'medications' not in user or not isinstance(user.get('medications'), list):
                user['medications'] = []
            if 'allergies' not in user or not isinstance(user.get('allergies'), list):
                user['allergies'] = []
            
            print(f"🔍 DEBUG: Initialized arrays - Conditions: {len(user['medicalConditions'])}, "
                  f"Medications: {len(user['medications'])}, Allergies: {len(user['allergies'])}")
            
            # Update conditions (avoid duplicates)
            for condition in extracted_info['conditions']:
                existing = next((c for c in user['medicalConditions'] 
                               if c['name'].lower() == condition['name'].lower()), None)
                if not existing:
                    user['medicalConditions'].append(condition)
                    print(f"   ✅ Added condition: {condition['name']}")
                else:
                    # Update timestamp if condition is mentioned again
                    existing['mentioned_date'] = condition['mentioned_date']
                    print(f"   🔄 Updated condition: {condition['name']}")
            
            # Update medications (avoid duplicates)
            for medication in extracted_info['medications']:
                existing = next((m for m in user['medications'] 
                               if m['name'].lower() == medication['name'].lower()), None)
                if not existing:
                    user['medications'].append(medication)
                    print(f"   ✅ Added medication: {medication['name']}")
                else:
                    existing['mentioned_date'] = medication['mentioned_date']
                    print(f"   🔄 Updated medication: {medication['name']}")
            
            # Update allergies (avoid duplicates)
            for allergy in extracted_info['allergies']:
                existing = next((a for a in user['allergies'] 
                               if a['name'].lower() == allergy['name'].lower()), None)
                if not existing:
                    user['allergies'].append(allergy)
                    print(f"   ✅ Added allergy: {allergy['name']}")
                else:
                    existing['mentioned_date'] = allergy['mentioned_date']
                    print(f"   🔄 Updated allergy: {allergy['name']}")
            
            # Update user document in database
            self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'medicalConditions': user['medicalConditions'],
                        'medications': user['medications'],
                        'allergies': user['allergies'],
                        'lastUpdated': datetime.utcnow()
                    }
                }
            )
            
            print(f"✅ Medical profile updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error updating medical profile: {e}")
            return False

    def get_medical_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's medical profile"""
        try:
            user = self.users_collection.find_one({'_id': ObjectId(user_id)})
            if user:
                # Handle empty strings and convert to proper arrays
                conditions = user.get('medicalConditions', [])
                medications = user.get('medications', [])
                allergies = user.get('allergies', [])
                
                # Convert empty strings to empty arrays
                if isinstance(medications, str) and medications.strip() == "":
                    medications = []
                if isinstance(allergies, str) and allergies.strip() == "":
                    allergies = []
                
                return {
                    'conditions': conditions,
                    'medications': medications,
                    'allergies': allergies
                }
            return None
        except Exception as e:
            print(f"❌ Error getting medical profile: {e}")
            return None

    def build_context_prompt(self, user_id: str, current_question: str) -> str:
        """Build medical context for AI prompt"""
        profile = self.get_medical_profile(user_id)
        
        if not profile:
            return ""
        
        context_parts = []
        
        # Add conditions context
        if profile.get('conditions') and len(profile['conditions']) > 0:
            conditions = [c['name'] for c in profile['conditions']]
            context_parts.append(f"User has medical conditions: {', '.join(conditions)}")
        
        # Add medications context
        if profile.get('medications') and len(profile['medications']) > 0:
            medications = [m['name'] for m in profile['medications']]
            context_parts.append(f"User takes medications: {', '.join(medications)}")
        
        # Add allergies context
        if profile.get('allergies') and len(profile['allergies']) > 0:
            allergies = [a['name'] for a in profile['allergies']]
            context_parts.append(f"User has allergies: {', '.join(allergies)}")
        
        if context_parts:
            return f"Medical Context: {'; '.join(context_parts)}. Consider these conditions when providing advice."
        
        return ""

    def delete_condition(self, user_id: str, condition_name: str) -> bool:
        """Delete a specific condition from user's profile"""
        try:
            result = self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$pull': {'medicalConditions': {'name': condition_name}}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error deleting condition: {e}")
            return False

    def delete_medication(self, user_id: str, medication_name: str) -> bool:
        """Delete a specific medication from user's profile"""
        try:
            result = self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$pull': {'medications': {'name': medication_name}}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error deleting medication: {e}")
            return False

    def delete_allergy(self, user_id: str, allergy_name: str) -> bool:
        """Delete a specific allergy from user's profile"""
        try:
            result = self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$pull': {'allergies': {'name': allergy_name}}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error deleting allergy: {e}")
            return False

    def clear_medical_profile(self, user_id: str) -> bool:
        """Clear all medical information for a user"""
        try:
            result = self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$unset': {
                        'medicalConditions': '',
                        'medications': '',
                        'allergies': ''
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error clearing medical profile: {e}")
            return False
