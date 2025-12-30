"""
Authentication Microservice
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, redirect
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from swagger_config import api
from routes import auth_bp

# Create Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))

# Initialize Swagger
api.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Root redirect to docs
@app.route('/')
def index():
    return redirect('/docs')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {'success': False, 'message': 'Endpoint not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'success': False, 'message': 'Internal server error'}, 500


if __name__ == '__main__':
    port = int(os.getenv('AUTH_SERVICE_PORT', 5001))
    print(f"Auth Service starting on port {port}")
    print(f"Swagger documentation: http://localhost:{port}/docs")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'True') == 'True'
    )
