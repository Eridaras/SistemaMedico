"""
Notifications Service
Handles user notifications, low stock alerts, and appointment reminders
"""
from flask import Flask
from flask_cors import CORS
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import get_cors_config
from notifications_service.routes import notifications_bp

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Configure CORS
CORS(app, **get_cors_config())

# Register blueprints
app.register_blueprint(notifications_bp, url_prefix='/api/notifications')

if __name__ == '__main__':
    port = int(os.getenv('NOTIFICATIONS_SERVICE_PORT', 5007))
    print(f"🔔 Notifications Service running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
