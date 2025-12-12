"""
Common logging utility for all services
"""
import requests
import os
from threading import Thread

class ServiceLogger:
    """Helper class to send logs to the Logs Service"""

    def __init__(self, service_name):
        self.service_name = service_name
        self.logs_service_url = os.getenv('LOGS_SERVICE_URL', 'http://localhost:5006/api/logs')

    def _send_log(self, action, level='INFO', user_id=None, details=None, ip_address=None):
        """Send log entry to Logs Service (non-blocking)"""
        try:
            payload = {
                'service_name': self.service_name,
                'action': action,
                'level': level,
                'user_id': user_id,
                'details': details,
                'ip_address': ip_address
            }

            # Send in a separate thread to avoid blocking the main request
            def send():
                try:
                    requests.post(
                        f"{self.logs_service_url}/logs",
                        json=payload,
                        timeout=2
                    )
                except:
                    # Silently fail - don't break the main application
                    pass

            thread = Thread(target=send)
            thread.daemon = True
            thread.start()

        except Exception as e:
            # Silently fail - logging should never break the application
            print(f"Logger warning: {str(e)}")

    def debug(self, action, user_id=None, details=None, ip_address=None):
        """Log DEBUG level message"""
        self._send_log(action, 'DEBUG', user_id, details, ip_address)

    def info(self, action, user_id=None, details=None, ip_address=None):
        """Log INFO level message"""
        self._send_log(action, 'INFO', user_id, details, ip_address)

    def warning(self, action, user_id=None, details=None, ip_address=None):
        """Log WARNING level message"""
        self._send_log(action, 'WARNING', user_id, details, ip_address)

    def error(self, action, user_id=None, details=None, ip_address=None):
        """Log ERROR level message"""
        self._send_log(action, 'ERROR', user_id, details, ip_address)

    def critical(self, action, user_id=None, details=None, ip_address=None):
        """Log CRITICAL level message"""
        self._send_log(action, 'CRITICAL', user_id, details, ip_address)


# Create logger instances for each service
auth_logger = ServiceLogger('auth')
inventario_logger = ServiceLogger('inventario')
historia_clinica_logger = ServiceLogger('historia_clinica')
facturacion_logger = ServiceLogger('facturacion')
citas_logger = ServiceLogger('citas')
logs_logger = ServiceLogger('logs')
