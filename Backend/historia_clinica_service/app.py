"""
Historia Clinica Microservice
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from routes import historia_clinica_bp

# Create Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))

# Register blueprints
app.register_blueprint(historia_clinica_bp, url_prefix='/api/historia-clinica')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {'success': False, 'message': 'Endpoint not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'success': False, 'message': 'Internal server error'}, 500


if __name__ == '__main__':
    port = int(os.getenv('HISTORIA_CLINICA_SERVICE_PORT', 5003))
    print(f"🚀 Historia Clinica Service starting on port {port}")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'True') == 'True'
    )
