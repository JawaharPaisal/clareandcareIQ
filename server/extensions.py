from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient

jwt = JWTManager()

def init_db(uri):
    """Initialize MongoDB connection"""
    client = MongoClient(uri)
    db = client.get_default_database()
    
    # Create indexes
    db.users.create_index("email", unique=True)
    db.users.create_index("googleSub", unique=True)
    db.medical_histories.create_index([("userId", 1), ("createdAt", -1)])
    db.chat_sessions.create_index("userId")
    db.chat_sessions.create_index("expiresAt", expireAfterSeconds=0)  # TTL index
    
    return db

def init_extensions(app):
    """Initialize Flask extensions"""
    # CORS - allow credentials for JWT cookies
    CORS(app, 
         supports_credentials=True, 
         origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5000", "http://127.0.0.1:5000"],  # React dev servers + local testing
         allow_headers=["Content-Type", "Authorization"])
    
    # JWT
    jwt.init_app(app)
    
    # Rate limiting
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["60 per minute"],
        storage_uri="memory://"
    )
    
    return limiter
