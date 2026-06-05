from flask import Blueprint, request, jsonify, current_app, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, set_access_cookies, unset_jwt_cookies
from datetime import datetime
import os
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import json
from bson import ObjectId

auth_bp = Blueprint('auth', __name__)

# Google OAuth configuration
GOOGLE_CLIENT_CONFIG = {
    "web": {
        "client_id": os.getenv('GOOGLE_CLIENT_ID'),
        "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/callback')],
        "scopes": ["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"]
    }
}

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info - requires JWT"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        # Convert string user_id back to ObjectId for MongoDB query
        from bson import ObjectId
        user = db.users.find_one({"_id": ObjectId(user_id)}, {"googleSub": 0})  # Don't expose googleSub
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Convert ObjectId to string for JSON serialization
        user['_id'] = str(user['_id'])
        
        return jsonify({"user": user}), 200
        
    except Exception as e:
        return jsonify({"error": "Authentication failed"}), 401

@auth_bp.route('/google', methods=['GET'])
def google_auth():
    """Initiate Google OAuth flow"""
    try:
        if not GOOGLE_CLIENT_CONFIG["web"]["client_id"]:
            return jsonify({"error": "Google OAuth not configured"}), 500
        
        # Create OAuth flow
        flow = Flow.from_client_config(
            GOOGLE_CLIENT_CONFIG,
            scopes=GOOGLE_CLIENT_CONFIG["web"]["scopes"]
        )
        flow.redirect_uri = GOOGLE_CLIENT_CONFIG["web"]["redirect_uris"][0]
        
        # Generate authorization URL
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Store state in session (for production, use Redis or database)
        # For now, we'll use a simple approach
        current_app.config['OAUTH_STATE'] = state
        
        return redirect(authorization_url)
        
    except Exception as e:
        return jsonify({"error": f"OAuth initialization failed: {str(e)}"}), 500

@auth_bp.route('/callback', methods=['GET'])
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Get authorization code from callback
        code = request.args.get('code')
        state = request.args.get('state')
        
        if not code:
            return jsonify({"error": "Authorization code not received"}), 400
        
        # Verify state (basic security check)
        if state != current_app.config.get('OAUTH_STATE'):
            return jsonify({"error": "Invalid state parameter"}), 400
        
        # Create OAuth flow
        flow = Flow.from_client_config(
            GOOGLE_CLIENT_CONFIG,
            scopes=GOOGLE_CLIENT_CONFIG["web"]["scopes"]
        )
        flow.redirect_uri = GOOGLE_CLIENT_CONFIG["web"]["redirect_uris"][0]
        
        # Exchange code for tokens
        flow.fetch_token(code=code)
        
        # Get user info from ID token
        id_info = id_token.verify_oauth2_token(
            flow.credentials.id_token,
            google_requests.Request(),
            GOOGLE_CLIENT_CONFIG["web"]["client_id"]
        )
        
        # Extract user information
        google_sub = id_info['sub']
        email = id_info['email']
        name = id_info.get('name', email.split('@')[0])
        picture = id_info.get('picture', 'https://via.placeholder.com/150')
        
        db = current_app.db
        
        # Find or create user
        user = db.users.find_one({"googleSub": google_sub})
        if not user:
            # Create new user
            user_doc = {
                "googleSub": google_sub,
                "email": email,
                "name": name,
                "picture": picture,
                "consent": {
                    "given": True,
                    "timestamp": datetime.utcnow(),
                    "policyVersion": "v1.0"
                },
                "createdAt": datetime.utcnow(),
                "lastLogin": datetime.utcnow()
            }
            result = db.users.insert_one(user_doc)
            user_id = str(result.inserted_id)
        else:
            # Update existing user
            user_id = str(user['_id'])
            db.users.update_one(
                {"_id": user['_id']},
                {"$set": {"lastLogin": datetime.utcnow()}}
            )
        
        # Create consent record for AI analysis (required for chat)
        from services.security_service import ConsentManager
        existing_consent = db.consents.find_one({
            "userId": ObjectId(user_id),
            "status": "active"
        })
        
        if not existing_consent:
            # Create full consent record for development
            consent_types = {
                'data_storage': True,
                'ai_analysis': True,
                'medical_history': True,
                'personalization': True,
                'data_sharing': False  # Optional
            }
            
            consent_record = ConsentManager.create_consent_record(user_id, consent_types)
            consent_record['status'] = 'active'
            consent_record['userId'] = ObjectId(user_id)
            
            db.consents.insert_one(consent_record)
            print(f"✅ Created consent record for Google user {user_id}")
        
        # Create JWT
        access_token = create_access_token(identity=user_id)
        
        # For testing, redirect to frontend instead of backend success page
        # In production, this would redirect to FRONTEND_URL
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        response = redirect(f"{frontend_url}/?auth_success=true&user_id={user_id}")
        set_access_cookies(response, access_token)
        
        return response
        
    except Exception as e:
        return jsonify({"error": f"OAuth callback failed: {str(e)}"}), 500

@auth_bp.route('/success', methods=['GET'])
def auth_success():
    """OAuth success page for testing"""
    user_id = request.args.get('user_id')
    return f"""
    <html>
    <head><title>OAuth Success</title></head>
    <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
        <h1 style="color: #4CAF50;">✅ Authentication Successful!</h1>
        <p>Welcome to Clare & CareIQ!</p>
        <p><strong>User ID:</strong> {user_id}</p>
        <p><strong>JWT Cookie:</strong> Set successfully</p>
        <hr>
        <h3>Test Your Authentication:</h3>
        <p><a href="/auth/me" style="color: #2196F3;">Test /auth/me endpoint</a></p>
        <p><a href="/auth/logout" style="color: #f44336;">Logout</a></p>
        <hr>
        <p><em>This is a test page. In production, you'd be redirected to your React frontend.</em></p>
    </body>
    </html>
    """

@auth_bp.route('/logout', methods=['POST', 'GET'])
@jwt_required()
def logout():
    """Logout user by clearing JWT cookie"""
    response = jsonify({"message": "Logged out successfully"})
    unset_jwt_cookies(response)
    
    # For GET requests, return HTML page
    if request.method == 'GET':
        response = f"""
        <html>
        <head><title>Logged Out</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
            <h1 style="color: #f44336;">👋 Logged Out Successfully</h1>
            <p>Your JWT cookies have been cleared.</p>
            <hr>
            <p><a href="/auth/google" style="color: #2196F3;">Login Again with Google</a></p>
            <p><a href="/auth/dev-login" style="color: #4CAF50;">Dev Login (for testing)</a></p>
        </body>
        </html>
        """
        return response
    
    return response

# Keep dev login for development/testing
@auth_bp.route('/dev-login', methods=['GET'])
def dev_login_page():
    """Development only - show dev login page"""
    if os.getenv('FLASK_ENV') != 'development':
        return jsonify({"error": "Not available in production"}), 403
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dev Login - Clare & CareIQ</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }
            .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #4CAF50; margin-bottom: 30px; }
            input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
            button { width: 100%; padding: 12px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #45a049; }
            .error { color: red; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 Dev Login</h1>
            <p>For development and testing purposes</p>
            <form id="devLoginForm">
                <input type="text" id="name" placeholder="Your Name" value="Test User" required>
                <input type="email" id="email" placeholder="Your Email" value="test@example.com" required>
                <button type="submit">Login</button>
            </form>
            <div id="error" class="error" style="display: none;"></div>
        </div>
        
        <script>
            document.getElementById('devLoginForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const name = document.getElementById('name').value;
                const email = document.getElementById('email').value;
                const errorDiv = document.getElementById('error');
                
                try {
                    const response = await fetch('/auth/dev-login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ name, email })
                    });
                    
                    if (response.ok) {
                        window.location.href = '/';
                    } else {
                        const error = await response.json();
                        errorDiv.textContent = error.error || 'Login failed';
                        errorDiv.style.display = 'block';
                    }
                } catch (error) {
                    errorDiv.textContent = 'Network error: ' + error.message;
                    errorDiv.style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    """

@auth_bp.route('/dev-login', methods=['POST'])
def dev_login():
    """Development only - create dummy user and JWT"""
    if os.getenv('FLASK_ENV') != 'development':
        return jsonify({"error": "Not available in production"}), 403
    
    try:
        data = request.get_json()
        name = data.get('name', 'Test User')
        email = data.get('email', 'test@example.com')
        
        db = current_app.db
        
        # Create or find test user
        user = db.users.find_one({"email": email})
        if not user:
            user_doc = {
                "googleSub": "dev_user_123",
                "email": email,
                "name": name,
                "picture": "https://via.placeholder.com/150",
                "consent": {
                    "given": True,
                    "timestamp": datetime.utcnow(),
                    "policyVersion": "v1.0"
                },
                "createdAt": datetime.utcnow(),
                "lastLogin": datetime.utcnow()
            }
            result = db.users.insert_one(user_doc)
            user_id = str(result.inserted_id)
        else:
            user_id = str(user['_id'])
            # Update last login
            db.users.update_one(
                {"_id": user['_id']},
                {"$set": {"lastLogin": datetime.utcnow()}}
            )
        
        # Create consent record for AI analysis (required for chat)
        from services.security_service import ConsentManager
        existing_consent = db.consents.find_one({
            "userId": ObjectId(user_id),
            "status": "active"
        })
        
        if not existing_consent:
            # Create full consent record for development
            consent_types = {
                'data_storage': True,
                'ai_analysis': True,
                'medical_history': True,
                'personalization': True,
                'data_sharing': False  # Optional
            }
            
            consent_record = ConsentManager.create_consent_record(user_id, consent_types)
            consent_record['status'] = 'active'
            consent_record['userId'] = ObjectId(user_id)
            
            db.consents.insert_one(consent_record)
            print(f"✅ Created consent record for user {user_id}")
        
        # Create JWT
        access_token = create_access_token(identity=user_id)
        response = jsonify({"message": "Dev login successful", "user_id": user_id})
        set_access_cookies(response, access_token)
        
        return response, 200
        
    except Exception as e:
        return jsonify({"error": f"Dev login failed: {str(e)}"}), 500
