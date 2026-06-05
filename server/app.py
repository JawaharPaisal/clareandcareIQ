from flask import Flask
from flask_jwt_extended import JWTManager
import os
from datetime import timedelta

from extensions import init_extensions, init_db
from blueprints.auth import auth_bp
from blueprints.chat import chat_bp
from blueprints.reports import reports_bp
from blueprints.history import history_bp
from blueprints.consent import consent_bp
from blueprints.profile import profile_bp

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'change_me_super_secret')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
    app.config['JWT_COOKIE_HTTPONLY'] = True
    app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Simplified for MVP
    
    # Initialize extensions
    limiter = init_extensions(app)
    
    # Initialize database
    app.db = init_db(os.getenv('MONGO_URI', 'mongodb://localhost:27017/clarecare'))
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(history_bp, url_prefix='/history')
    app.register_blueprint(consent_bp, url_prefix='/consent')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'Clare & CareIQ API'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')
