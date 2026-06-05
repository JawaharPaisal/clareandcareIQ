import os
from datetime import timedelta

class Config:
    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'change_me_super_secret')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET', 'change_me_super_secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_COOKIE_CSRF_PROTECT = False
    
    # Database
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/clarecare')
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/callback')
    
    # AI
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    USE_MOCK_AI = os.getenv('USE_MOCK_AI', 'true').lower() == 'true'
    
    # Security
    FIELD_ENC_KEY_BASE64 = os.getenv('FIELD_ENC_KEY_BASE64')
    
class DevelopmentConfig(Config):
    DEBUG = True
    JWT_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False
    JWT_COOKIE_SECURE = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
