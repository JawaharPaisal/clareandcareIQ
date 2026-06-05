#!/usr/bin/env python3
"""
Consent Middleware for Phase 5
Enforces consent requirements for data processing endpoints
"""

from flask import request, jsonify, current_app
from functools import wraps
from bson import ObjectId
from services.security_service import ConsentManager

def require_consent(consent_type: str):
    """
    Decorator to require specific consent for endpoint access
    
    Args:
        consent_type: Type of consent required (e.g., 'data_storage', 'ai_analysis')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip consent check for certain endpoints
            if request.endpoint in ['consent.get_consent_status', 'consent.give_consent', 'auth.get_current_user']:
                return f(*args, **kwargs)
            
            # Get user ID from JWT (assuming it's available in the request context)
            from flask_jwt_extended import get_jwt_identity
            user_id = get_jwt_identity()
            
            if not user_id:
                return jsonify({"error": "Authentication required"}), 401
            
            # Check consent
            db = current_app.db
            consent_record = db.consents.find_one({
                "userId": ObjectId(user_id),
                "status": "active"
            })
            
            if not ConsentManager.validate_consent(consent_record, consent_type):
                return jsonify({
                    "error": "Consent required",
                    "message": f"Consent for '{consent_type}' is required to access this feature",
                    "consentType": consent_type,
                    "consentDescription": ConsentManager.CONSENT_TYPES.get(consent_type, "Unknown consent type"),
                    "requiredConsent": True
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_full_consent():
    """
    Decorator to require full consent for sensitive operations
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip consent check for certain endpoints
            if request.endpoint in ['consent.get_consent_status', 'consent.give_consent', 'auth.get_current_user']:
                return f(*args, **kwargs)
            
            # Get user ID from JWT
            from flask_jwt_extended import get_jwt_identity
            user_id = get_jwt_identity()
            
            if not user_id:
                return jsonify({"error": "Authentication required"}), 401
            
            # Check full consent
            db = current_app.db
            consent_record = db.consents.find_one({
                "userId": ObjectId(user_id),
                "status": "active"
            })
            
            summary = ConsentManager.get_consent_summary(consent_record)
            
            if not summary['hasConsent']:
                return jsonify({
                    "error": "Full consent required",
                    "message": "Complete consent is required to access this feature",
                    "requiredConsent": True,
                    "consentStatus": summary
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_consent_activity(activity_type: str):
    """
    Decorator to log consent-related activities for audit trail
    
    Args:
        activity_type: Type of activity (e.g., 'data_access', 'data_modification')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Log the activity
            from flask_jwt_extended import get_jwt_identity
            user_id = get_jwt_identity()
            
            if user_id:
                db = current_app.db
                activity_log = {
                    "userId": ObjectId(user_id),
                    "activityType": activity_type,
                    "endpoint": request.endpoint,
                    "method": request.method,
                    "timestamp": current_app.datetime.utcnow(),
                    "ipAddress": request.remote_addr,
                    "userAgent": request.headers.get('User-Agent')
                }
                
                try:
                    db.consent_activities.insert_one(activity_log)
                except Exception as e:
                    print(f"Failed to log consent activity: {e}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

