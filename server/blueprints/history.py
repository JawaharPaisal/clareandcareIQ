from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from bson import ObjectId

history_bp = Blueprint('history', __name__)

@history_bp.route('', methods=['GET'])
@jwt_required()
def get_history():
    """Get user's medical history summaries"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        # Query parameters
        limit = min(int(request.args.get('limit', 20)), 100)  # Max 100 items
        skip = int(request.args.get('skip', 0))
        source_type = request.args.get('sourceType')  # 'chat' or 'report'
        
        # Build query
        query = {"userId": ObjectId(user_id)}
        if source_type:
            query["sourceType"] = source_type
        
        # Get histories (exclude encrypted fields in list view)
        histories = list(db.medical_histories.find(
            query,
            {
                "summaryText_enc": 0  # Don't return encrypted data in list
            }
        ).sort("createdAt", -1).skip(skip).limit(limit))
        
        # Convert ObjectIds to strings
        for history in histories:
            history['_id'] = str(history['_id'])
            history['userId'] = str(history['userId'])
        
        # Get total count
        total_count = db.medical_histories.count_documents(query)
        
        return jsonify({
            "histories": histories,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "skip": skip,
                "hasMore": skip + len(histories) < total_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch history: {str(e)}"}), 500

@history_bp.route('/<history_id>', methods=['GET'])
@jwt_required()
def get_history_item(history_id):
    """Get specific history item with full details"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        history = db.medical_histories.find_one({
            "_id": ObjectId(history_id),
            "userId": ObjectId(user_id)
        })
        
        if not history:
            return jsonify({"error": "History item not found"}), 404
        
        # Convert ObjectIds to strings
        history['_id'] = str(history['_id'])
        history['userId'] = str(history['userId'])
        
        # TODO Phase 5: Decrypt summaryText_enc if present
        
        return jsonify({"history": history}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch history item: {str(e)}"}), 500

@history_bp.route('', methods=['POST'])
@jwt_required()
def add_history():
    """Add manual history entry"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        summary_text = data.get('summaryText', '').strip()
        source_type = data.get('sourceType', 'manual')
        tags = data.get('tags', [])
        
        if not summary_text:
            return jsonify({"error": "Summary text is required"}), 400
        
        db = current_app.db
        
        # Create history document
        history_doc = {
            "userId": ObjectId(user_id),
            "sourceType": source_type,
            "summaryText_plain": summary_text,  # For Phase 1, store plain text
            "extracted": {
                "conditions": [],
                "allergies": [],
                "medications": [],
                "vitals": {},
                "labs": {}
            },
            "tags": tags,
            "createdAt": datetime.utcnow()
        }
        
        # TODO Phase 5: Encrypt summaryText_plain -> summaryText_enc
        
        result = db.medical_histories.insert_one(history_doc)
        history_doc['_id'] = str(result.inserted_id)
        history_doc['userId'] = str(history_doc['userId'])
        
        return jsonify({
            "message": "History added successfully",
            "history": history_doc
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Failed to add history: {str(e)}"}), 500

@history_bp.route('/<history_id>', methods=['DELETE'])
@jwt_required()
def delete_history(history_id):
    """Delete a history item"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        result = db.medical_histories.delete_one({
            "_id": ObjectId(history_id),
            "userId": ObjectId(user_id)
        })
        
        if result.deleted_count == 0:
            return jsonify({"error": "History item not found"}), 404
        
        return jsonify({"message": "History deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to delete history: {str(e)}"}), 500

@history_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_history_stats():
    """Get user's history statistics"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        # Aggregate statistics
        pipeline = [
            {"$match": {"userId": ObjectId(user_id)}},
            {"$group": {
                "_id": "$sourceType",
                "count": {"$sum": 1}
            }}
        ]
        
        stats_cursor = db.medical_histories.aggregate(pipeline)
        stats = {item['_id']: item['count'] for item in stats_cursor}
        
        # Get recent activity count (last 30 days)
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_count = db.medical_histories.count_documents({
            "userId": ObjectId(user_id),
            "createdAt": {"$gte": recent_date}
        })
        
        return jsonify({
            "totalEntries": sum(stats.values()),
            "byType": stats,
            "recentActivity": recent_count
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch stats: {str(e)}"}), 500
