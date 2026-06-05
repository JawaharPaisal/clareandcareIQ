from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId
from services.report_processor import ReportProcessor
from services.report_analyzer import ReportAnalyzer
from services.context_builder import MedicalContextBuilder
from middleware.consent_middleware import require_consent, require_full_consent

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('', methods=['POST'])
@jwt_required()
@require_full_consent()
def upload_report():
    """Upload and process medical report with user-provided name"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Get user-provided metadata
        report_name = request.form.get('reportName', file.filename)
        report_type = request.form.get('reportType', 'general')
        
        print(f"📄 Uploading report: {report_name} (type: {report_type})")
        
        # Validate file type
        allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png', 'txt'}
        file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_extension not in allowed_extensions:
            return jsonify({"error": f"File type '{file_extension}' not supported. Supported types: {', '.join(allowed_extensions)}"}), 400
        
        # Read file content
        file_content = file.read()
        if len(file_content) == 0:
            return jsonify({"error": "Empty file uploaded"}), 400
        
        # Process the file (includes vision analysis for images)
        processor = ReportProcessor()
        processing_result = processor.process_file(file_content, file.filename, file_extension)
        
        if processing_result['status'] != 'success':
            return jsonify({"error": f"File processing failed: {processing_result.get('error', 'Unknown error')}"}), 400
        
        # Get user's medical context for personalized analysis
        context_builder = MedicalContextBuilder(db)
        user_context = context_builder.get_user_medical_context(user_id)
        
        # Analyze the extracted text with AI
        analyzer = ReportAnalyzer()
        analysis_result = analyzer.analyze_medical_report(
            processing_result['extracted_text'],
            file.filename,
            user_context
        )
        
        if analysis_result['status'] != 'success':
            return jsonify({"error": f"AI analysis failed: {analysis_result.get('error', 'Unknown error')}"}), 500
        
        # Generate medical history entry
        history_entry = analyzer.generate_medical_history_entry(
            analysis_result,
            processing_result['extracted_text']
        )
        
        # Add user ID and metadata
        history_entry['userId'] = ObjectId(user_id)
        history_entry['_id'] = ObjectId()
        history_id = history_entry['_id']
        
        # Save to medical history
        db.medical_histories.insert_one(history_entry)
        
        # Create report document with user-provided name
        report_doc = {
            "_id": ObjectId(),
            "userId": ObjectId(user_id),
            "reportName": report_name,
            "reportType": report_type,
            "fileName": file.filename,
            "fileType": file_extension,
            "fileSize": len(file_content),
            "extractedText": processing_result['extracted_text'],
            "aiSummary": analysis_result.get('ai_summary', ''),
            "modelUsed": analysis_result.get('model_used', 'unknown'),
            "extracted": history_entry.get('extracted', {}),
            "tags": history_entry.get('tags', []),
            "historyId": history_id,
            "status": "completed",
            "createdAt": datetime.utcnow(),
            "processedAt": datetime.utcnow()
        }
        
        # Save to reports collection
        db.reports.insert_one(report_doc)
        
        print(f"✅ Report saved: {report_name} (ID: {report_doc['_id']})")
        
        # Return success response
        response_data = {
            "success": True,
            "message": "Report uploaded and analyzed successfully",
            "reportId": str(report_doc['_id']),
            "reportName": report_name,
            "reportType": report_type,
            "historyId": str(history_id),
            "filename": file.filename,
            "fileType": file_extension,
            "aiSummary": analysis_result.get('ai_summary', ''),
            "modelUsed": analysis_result.get('model_used', 'unknown'),
            "textLength": processing_result['text_length'],
            "timestamp": datetime.utcnow().isoformat(),
            "hasUserContext": analysis_result.get('has_user_context', False),
            "extractedInfo": {
                "conditions": len(history_entry.get('extracted', {}).get('conditions', [])),
                "medications": len(history_entry.get('extracted', {}).get('medications', [])),
                "vitals": len(history_entry.get('extracted', {}).get('vitals', {})),
                "labs": len(history_entry.get('extracted', {}).get('labs', {}))
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ Report upload error: {e}")
        return jsonify({"error": f"Report upload failed: {str(e)}"}), 500

@reports_bp.route('', methods=['GET'])
@jwt_required()
def get_reports():
    """Get user's uploaded reports from reports collection"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        # Fetch from reports collection
        reports = list(db.reports.find(
            {"userId": ObjectId(user_id)},
            {
                "extractedText": 0  # Don't return full text in list view
            }
        ).sort("createdAt", -1).limit(50))
        
        # Convert ObjectIds to strings
        for report in reports:
            report['_id'] = str(report['_id'])
            report['userId'] = str(report['userId'])
            if 'historyId' in report:
                report['historyId'] = str(report['historyId'])
        
        print(f"📋 Found {len(reports)} reports for user {user_id}")
        
        return jsonify({"success": True, "reports": reports, "count": len(reports)}), 200
        
    except Exception as e:
        print(f"❌ Error fetching reports: {e}")
        return jsonify({"error": f"Failed to fetch reports: {str(e)}"}), 500

@reports_bp.route('/<report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    """Get specific report details with full extracted text"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        report = db.reports.find_one({
            "_id": ObjectId(report_id),
            "userId": ObjectId(user_id)
        })
        
        if not report:
            return jsonify({"error": "Report not found"}), 404
        
        # Convert ObjectIds to strings
        report['_id'] = str(report['_id'])
        report['userId'] = str(report['userId'])
        if 'historyId' in report:
            report['historyId'] = str(report['historyId'])
        
        return jsonify({"success": True, "report": report}), 200
        
    except Exception as e:
        print(f"❌ Error fetching report: {e}")
        return jsonify({"error": f"Failed to fetch report: {str(e)}"}), 500

@reports_bp.route('/<report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    """Delete a report and its associated medical history"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        # Find the report first to get historyId
        report = db.reports.find_one({
            "_id": ObjectId(report_id),
            "userId": ObjectId(user_id)
        })
        
        if not report:
            return jsonify({"error": "Report not found"}), 404
        
        # Delete the report
        db.reports.delete_one({"_id": ObjectId(report_id)})
        
        # Also delete associated medical history if exists
        if 'historyId' in report:
            db.medical_histories.delete_one({"_id": report['historyId']})
        
        print(f"🗑️ Deleted report: {report.get('reportName', 'Unknown')}")
        
        return jsonify({"success": True, "message": "Report deleted successfully"}), 200
        
    except Exception as e:
        print(f"❌ Error deleting report: {e}")
        return jsonify({"error": f"Failed to delete report: {str(e)}"}), 500
