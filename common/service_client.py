"""
Cliente HTTP para comunicación entre microservicios
"""
import requests
import os
from typing import Dict, Any, Optional


class ServiceClient:
    """HTTP client for inter-service communication"""

    def __init__(self, base_url: str, service_name: str):
        self.base_url = base_url
        self.service_name = service_name
        self.timeout = 10

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """Get request headers"""
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        return headers

    def get(self, endpoint: str, token: Optional[str] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(
                url,
                headers=self._get_headers(token),
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error calling {self.service_name}: {str(e)}")
            raise

    def post(self, endpoint: str, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        """Make POST request"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.post(
                url,
                json=data,
                headers=self._get_headers(token),
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error calling {self.service_name}: {str(e)}")
            raise

    def put(self, endpoint: str, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        """Make PUT request"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.put(
                url,
                json=data,
                headers=self._get_headers(token),
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error calling {self.service_name}: {str(e)}")
            raise

    def delete(self, endpoint: str, token: Optional[str] = None) -> Dict[str, Any]:
        """Make DELETE request"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.delete(
                url,
                headers=self._get_headers(token),
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error calling {self.service_name}: {str(e)}")
            raise


# ==================== Service Clients ====================

class AuthServiceClient(ServiceClient):
    """Client for Auth Service"""

    def __init__(self):
        base_url = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001/api/auth')
        super().__init__(base_url, 'Auth Service')

    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token"""
        return self.get('/validate', token=token)

    def get_user(self, user_id: int, token: str) -> Dict[str, Any]:
        """Get user by ID"""
        return self.get(f'/users/{user_id}', token=token)


class InventarioServiceClient(ServiceClient):
    """Client for Inventario Service"""

    def __init__(self):
        base_url = os.getenv('INVENTARIO_SERVICE_URL', 'http://localhost:5002/api/inventario')
        super().__init__(base_url, 'Inventario Service')

    def check_treatment_stock(self, treatment_id: int, quantity: int, token: str) -> Dict[str, Any]:
        """Check if there's enough stock for a treatment"""
        return self.get(f'/treatments/{treatment_id}/check-stock', token=token, params={'quantity': quantity})

    def get_product(self, product_id: int, token: str) -> Dict[str, Any]:
        """Get product details"""
        return self.get(f'/products/{product_id}', token=token)

    def get_treatment(self, treatment_id: int, token: str) -> Dict[str, Any]:
        """Get treatment details with recipe"""
        return self.get(f'/treatments/{treatment_id}', token=token)

    def update_stock(self, product_id: int, quantity_change: int, token: str) -> Dict[str, Any]:
        """Update product stock"""
        return self.post(f'/products/{product_id}/stock', {'quantity_change': quantity_change}, token=token)


class HistoriaClinicaServiceClient(ServiceClient):
    """Client for Historia Clinica Service"""

    def __init__(self):
        base_url = os.getenv('HISTORIA_CLINICA_SERVICE_URL', 'http://localhost:5003/api/historia-clinica')
        super().__init__(base_url, 'Historia Clinica Service')

    def get_patient(self, patient_id: int, token: str) -> Dict[str, Any]:
        """Get patient details with full history"""
        return self.get(f'/patients/{patient_id}', token=token)

    def create_patient(self, patient_data: Dict[str, Any], token: str) -> Dict[str, Any]:
        """Create new patient"""
        return self.post('/patients', patient_data, token=token)


class FacturacionServiceClient(ServiceClient):
    """Client for Facturacion Service"""

    def __init__(self):
        base_url = os.getenv('FACTURACION_SERVICE_URL', 'http://localhost:5004/api/facturacion')
        super().__init__(base_url, 'Facturacion Service')

    def create_invoice(self, invoice_data: Dict[str, Any], token: str) -> Dict[str, Any]:
        """Create new invoice"""
        return self.post('/invoices', invoice_data, token=token)

    def get_invoice(self, invoice_id: int, token: str) -> Dict[str, Any]:
        """Get invoice details"""
        return self.get(f'/invoices/{invoice_id}', token=token)


class CitasServiceClient(ServiceClient):
    """Client for Citas Service"""

    def __init__(self):
        base_url = os.getenv('CITAS_SERVICE_URL', 'http://localhost:5005/api/citas')
        super().__init__(base_url, 'Citas Service')

    def get_appointment(self, appointment_id: int, token: str) -> Dict[str, Any]:
        """Get appointment with all details"""
        return self.get(f'/appointments/{appointment_id}', token=token)

    def check_availability(self, doctor_id: int, start_time: str, end_time: str, token: str) -> Dict[str, Any]:
        """Check doctor availability"""
        data = {
            'doctor_id': doctor_id,
            'start_time': start_time,
            'end_time': end_time
        }
        return self.post('/appointments/check-availability', data, token=token)

    def create_appointment(self, appointment_data: Dict[str, Any], token: str) -> Dict[str, Any]:
        """Create new appointment"""
        return self.post('/appointments', appointment_data, token=token)
