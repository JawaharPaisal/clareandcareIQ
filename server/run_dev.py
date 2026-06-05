#!/usr/bin/env python3
"""
Development server runner with environment setup
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set default environment variables for development
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('USE_MOCK_AI', 'false')
os.environ.setdefault('MONGO_URI', 'mongodb://localhost:27017/clarecare')
os.environ.setdefault('JWT_SECRET', 'dev_secret_change_in_production')
os.environ.setdefault('PORT', '5000')

# Import and run the app
from app import create_app

if __name__ == '__main__':
    print("🚀 Starting Clare & CareIQ Development Server")
    print("=" * 50)
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"Port: {os.getenv('PORT', '5000')}")
    print(f"MongoDB: {os.getenv('MONGO_URI', 'mongodb://localhost:27017/clarecare')}")
    print(f"Mock AI: {os.getenv('USE_MOCK_AI', 'true')}")
    print("=" * 50)
    
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    
    try:
        app.run(
            host='0.0.0.0', 
            port=port, 
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n💥 Server crashed: {e}")
        sys.exit(1)

