#!/usr/bin/env python3
"""
Consent Management Blueprint for Phase 5
Handles user consent for data processing and privacy controls
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId
from services.security_service import ConsentManager, DataPrivacyManager

consent_bp = Blueprint('consent', __name__)

@consent_bp.route('/status', methods=['GET'])
@jwt_required()
def get_consent_status():
    """Get user's current consent status"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        # Get user's consent record
        consent_record = db.consents.find_one({
            "userId": ObjectId(user_id),
            "status": "active"
        })
        
        # Get consent summary
        summary = ConsentManager.get_consent_summary(consent_record)
        
        # Add available consent types for frontend
        summary['availableConsentTypes'] = ConsentManager.CONSENT_TYPES
        summary['consentVersions'] = ConsentManager.CONSENT_VERSIONS
        
        return jsonify(summary), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get consent status: {str(e)}"}), 500

@consent_bp.route('/give', methods=['POST'])
@jwt_required()
def give_consent():
    """User gives consent for data processing"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        data = request.get_json()
        consent_types = data.get('consentTypes', {})
        version = data.get('version', 'v1.0')
        
        # Validate consent types
        valid_types = set(ConsentManager.CONSENT_TYPES.keys())
        provided_types = set(consent_types.keys())
        
        if not provided_types.issubset(valid_types):
            invalid_types = provided_types - valid_types
            return jsonify({"error": f"Invalid consent types: {list(invalid_types)}"}), 400
        
        # Create consent record
        consent_record = ConsentManager.create_consent_record(
            user_id, consent_types, version
        )
        
        # Deactivate any existing consent records
        db.consents.update_many(
            {"userId": ObjectId(user_id), "status": "active"},
            {"$set": {"status": "superseded", "supersededAt": datetime.utcnow()}}
        )
        
        # Save new consent record
        consent_record['_id'] = ObjectId()
        consent_record['userId'] = ObjectId(user_id)
        db.consents.insert_one(consent_record)
        
        # Get updated summary
        summary = ConsentManager.get_consent_summary(consent_record)
        
        return jsonify({
            "message": "Consent recorded successfully",
            "consentId": str(consent_record['_id']),
            "summary": summary
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to record consent: {str(e)}"}), 500

@consent_bp.route('/withdraw', methods=['POST'])
@jwt_required()
def withdraw_consent():
    """User withdraws consent for data processing"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        data = request.get_json()
        consent_types = data.get('consentTypes', [])  # List of consent types to withdraw
        
        if not consent_types:
            return jsonify({"error": "No consent types specified for withdrawal"}), 400
        
        # Update consent record
        result = db.consents.update_one(
            {"userId": ObjectId(user_id), "status": "active"},
            {
                "$set": {
                    "consentTypes": {consent_type: False for consent_type in consent_types},
                    "withdrawnAt": datetime.utcnow(),
                    "withdrawnTypes": consent_types
                }
            }
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "No active consent record found"}), 404
        
        return jsonify({
            "message": f"Consent withdrawn for: {', '.join(consent_types)}",
            "withdrawnTypes": consent_types
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to withdraw consent: {str(e)}"}), 500

@consent_bp.route('/data-summary', methods=['GET'])
@jwt_required()
def get_data_summary():
    """Get summary of user's stored data for privacy dashboard"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        # Get all user data
        user_data = list(db.medical_histories.find(
            {"userId": ObjectId(user_id)},
            {"summaryText_enc": 0, "rawData": 0}  # Exclude encrypted fields
        ))
        
        # Get data summary
        summary = DataPrivacyManager.get_user_data_summary(user_data)
        
        return jsonify(summary), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get data summary: {str(e)}"}), 500

@consent_bp.route('/export', methods=['GET'])
@jwt_required()
def export_user_data():
    """Export user's data in JSON format"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        # Get all user data
        user_data = list(db.medical_histories.find(
            {"userId": ObjectId(user_id)}
        ))
        
        # Convert ObjectIds to strings
        for item in user_data:
            item['_id'] = str(item['_id'])
            item['userId'] = str(item['userId'])
        
        return jsonify({
            "message": "Data export successful",
            "exportDate": datetime.utcnow().isoformat(),
            "recordCount": len(user_data),
            "data": user_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to export data: {str(e)}"}), 500

@consent_bp.route('/delete-all', methods=['DELETE'])
@jwt_required()
def delete_all_user_data():
    """Delete all user's data (Right to be forgotten)"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        # Get count before deletion
        count = db.medical_histories.count_documents({"userId": ObjectId(user_id)})
        
        # Delete all user data
        result = db.medical_histories.delete_many({"userId": ObjectId(user_id)})
        
        # Deactivate consent records
        db.consents.update_many(
            {"userId": ObjectId(user_id)},
            {"$set": {"status": "deleted", "deletedAt": datetime.utcnow()}}
        )
        
        return jsonify({
            "message": "All user data deleted successfully",
            "deletedRecords": result.deleted_count,
            "deletedAt": datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to delete user data: {str(e)}"}), 500

@consent_bp.route('/anonymize', methods=['POST'])
@jwt_required()
def anonymize_data_for_research():
    """Anonymize user's data for research purposes"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        # Check if user has given consent for data sharing
        consent_record = db.consents.find_one({
            "userId": ObjectId(user_id),
            "status": "active",
            "consentTypes.data_sharing": True
        })
        
        if not consent_record:
            return jsonify({"error": "Consent for data sharing required"}), 403
        
        # Get user data
        user_data = list(db.medical_histories.find({"userId": ObjectId(user_id)}))
        
        # Anonymize data
        anonymized_data = [DataPrivacyManager.anonymize_data(item) for item in user_data]
        
        return jsonify({
            "message": "Data anonymized for research",
            "anonymizedRecords": len(anonymized_data),
            "data": anonymized_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to anonymize data: {str(e)}"}), 500

