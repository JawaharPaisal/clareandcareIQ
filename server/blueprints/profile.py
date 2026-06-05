from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import base64
from datetime import datetime
from bson import ObjectId
# Profile data is stored in plain text for user viewing/editing
import uuid

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile information"""
    try:
        user_id = get_jwt_identity()
        user = current_app.db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Profile data should be stored in plain text for user viewing/editing
        profile_data = {
            "id": str(user["_id"]),
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "avatar": user.get("avatar", ""),
            "phone": user.get("phone", ""),
            "dateOfBirth": user.get("dateOfBirth", ""),
            "address": user.get("address", ""),
            "emergencyContact": user.get("emergencyContact", ""),
            "bloodType": user.get("bloodType", ""),
            "allergies": user.get("allergies", ""),
            "medications": user.get("medications", ""),
            "conditions": user.get("conditions", ""),
            "createdAt": user.get("createdAt", ""),
            "updatedAt": user.get("updatedAt", "")
        }
        
        return jsonify(profile_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting profile: {str(e)}")
        return jsonify({"error": "Failed to get profile"}), 500

@profile_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile information"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Prepare update data for profile fields
        update_data = {
            "updatedAt": datetime.utcnow().isoformat()
        }
        
        # Store profile fields in plain text (user needs to see/edit their own data)
        profile_fields = ['phone', 'dateOfBirth', 'address', 'emergencyContact', 
                         'bloodType', 'allergies', 'medications', 'conditions']
        
        for field in profile_fields:
            if field in data:
                update_data[field] = data[field]  # Store as plain text
        
        # Update non-sensitive fields
        if 'name' in data:
            update_data['name'] = data['name']
        
        # Update user in database
        result = current_app.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            return jsonify({"error": "No changes made"}), 400
        
        return jsonify({"message": "Profile updated successfully"}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error updating profile: {str(e)}")
        return jsonify({"error": "Failed to update profile"}), 500

@profile_bp.route('/profile/upload-image', methods=['POST'])
@jwt_required()
def upload_profile_image():
    """Upload and update profile image"""
    try:
        user_id = get_jwt_identity()
        
        # Check if file is present
        if 'profileImage' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['profileImage']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({"error": "Invalid file type"}), 400
        
        # Read file data and convert to base64
        file_data = file.read()
        file_base64 = base64.b64encode(file_data).decode('utf-8')
        
        # Create image object for MongoDB
        image_data = {
            "data": {"$binary": {"base64": file_base64, "subType": "00"}},
            "contentType": file.content_type
        }
        
        # Update user's avatar in database
        result = current_app.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "avatar": image_data,
                    "updatedAt": datetime.utcnow().isoformat()
                }
            }
        )
        
        if result.modified_count == 0:
            return jsonify({"error": "Failed to update profile image"}), 400
        
        # Return the image URL (in a real app, you'd return a proper URL)
        image_url = f"data:{file.content_type};base64,{file_base64}"
        
        return jsonify({
            "message": "Profile image updated successfully",
            "imageUrl": image_url
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error uploading profile image: {str(e)}")
        return jsonify({"error": "Failed to upload profile image"}), 500

@profile_bp.route('/profile/image/<user_id>', methods=['GET'])
def get_profile_image(user_id):
    """Get user profile image"""
    try:
        user = current_app.db.users.find_one(
            {"_id": ObjectId(user_id)},
            {"avatar": 1}
        )
        
        if not user or not user.get("avatar"):
            return jsonify({"error": "Image not found"}), 404
        
        avatar_data = user["avatar"]
        
        # Return the image data
        return jsonify({
            "contentType": avatar_data.get("contentType", "image/jpeg"),
            "data": avatar_data.get("data", {}).get("$binary", {}).get("base64", "")
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting profile image: {str(e)}")
        return jsonify({"error": "Failed to get profile image"}), 500
