"""
Facturacion Microservice
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from routes import facturacion_bp
from electronic_invoice_routes import electronic_invoice_bp

# Create Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))

# Register blueprints
app.register_blueprint(facturacion_bp, url_prefix='/api/facturacion')
app.register_blueprint(electronic_invoice_bp, url_prefix='/api/facturacion/sri')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {'success': False, 'message': 'Endpoint not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'success': False, 'message': 'Internal server error'}, 500


if __name__ == '__main__':
    port = int(os.getenv('FACTURACION_SERVICE_PORT', 5004))
    print(f"🚀 Facturacion Service starting on port {port}")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'True') == 'True'
    )
