"""
Logs Microservice - Sistema de Auditoría y Registro
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, redirect
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from logs_service.routes import logs_bp

# Create Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))

# Register blueprints
app.register_blueprint(logs_bp, url_prefix='/api/logs')

# Root redirect
@app.route('/')
def index():
    return {
        'service': 'Logs Service',
        'version': '1.0',
        'description': 'Sistema de Auditoría y Registro de Eventos',
        'endpoints': '/api/logs'
    }

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {'success': False, 'message': 'Endpoint not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'success': False, 'message': 'Internal server error'}, 500


if __name__ == '__main__':
    port = int(os.getenv('LOGS_SERVICE_PORT', 5006))
    print(f"Logs Service starting on port {port}")
    print(f"API Documentation: http://localhost:{port}/api/logs")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'True') == 'True'
    )
