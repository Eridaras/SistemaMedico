# Guía Completa: Swagger, Tests e Integración entre Servicios

## 📚 Índice

1. [Swagger/OpenAPI](#swagger-openapi)
2. [Pruebas Unitarias](#pruebas-unitarias)
3. [Integración entre Servicios](#integración-entre-servicios)

---

## 🎯 1. Swagger/OpenAPI

### Instalación

Las dependencias ya están agregadas en los `requirements.txt`:
- `flask-restx==1.3.0`

### Acceso a Swagger UI

Después de implementar Swagger, podrás acceder a la documentación interactiva en:

- **Auth Service**: http://localhost:5001/docs
- **Inventario Service**: http://localhost:5002/docs
- **Historia Clínica**: http://localhost:5003/docs
- **Facturación**: http://localhost:5004/docs
- **Citas**: http://localhost:5005/docs

### Ejemplo de implementación (Auth Service)

**Archivo:** `auth_service/app_swagger.py`

```python
"""
Auth Service con Swagger
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_cors import CORS
from flask_restx import Api, Resource, fields, Namespace
from dotenv import load_dotenv
import bcrypt
import jwt
from datetime import datetime, timedelta

from common.database import db
from auth_service.models import UserModel, RoleModel

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))

# Configure Swagger
authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'JWT Authorization header. Example: "Bearer {token}"'
    }
}

api = Api(
    app,
    version='1.0',
    title='Auth Service API',
    description='Microservicio de Autenticación - Sistema Gestión Clínica',
    doc='/docs',
    authorizations=authorizations,
    security='Bearer'
)

# Namespace
ns = api.namespace('auth', description='Operaciones de autenticación')

# Models
login_model = api.model('Login', {
    'email': fields.String(required=True, description='Email del usuario', example='admin@clinica.com'),
    'password': fields.String(required=True, description='Contraseña', example='admin123')
})

register_model = api.model('Register', {
    'email': fields.String(required=True, description='Email del usuario'),
    'password': fields.String(required=True, description='Contraseña (mínimo 6 caracteres)'),
    'full_name': fields.String(required=True, description='Nombre completo'),
    'role_id': fields.Integer(description='ID del rol', default=2)
})

user_response = api.model('UserResponse', {
    'user_id': fields.Integer(),
    'full_name': fields.String(),
    'email': fields.String(),
    'role_id': fields.Integer(),
    'role_name': fields.String(),
    'is_active': fields.Boolean()
})

login_response = api.model('LoginResponse', {
    'success': fields.Boolean(),
    'message': fields.String(),
    'data': fields.Nested(api.model('LoginData', {
        'token': fields.String(description='JWT Token'),
        'user': fields.Nested(user_response)
    }))
})

# Endpoints
@ns.route('/login')
class Login(Resource):
    @ns.doc('login')
    @ns.expect(login_model)
    @ns.response(200, 'Login exitoso', login_response)
    @ns.response(400, 'Datos inválidos')
    @ns.response(401, 'Credenciales incorrectas')
    def post(self):
        """Iniciar sesión y obtener token JWT"""
        data = api.payload

        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not email or not password:
            return {'success': False, 'message': 'Email y contraseña requeridos'}, 400

        user = UserModel.get_by_email(email)
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return {'success': False, 'message': 'Credenciales inválidas'}, 401

        if not user['is_active']:
            return {'success': False, 'message': 'Usuario desactivado'}, 403

        # Generate token
        token_payload = {
            'user_id': user['user_id'],
            'role_id': user['role_id'],
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(token_payload, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')

        return {
            'success': True,
            'message': 'Login exitoso',
            'data': {
                'token': token,
                'user': {
                    'user_id': user['user_id'],
                    'full_name': user['full_name'],
                    'email': user['email'],
                    'role_id': user['role_id'],
                    'role_name': user['role_name']
                }
            }
        }, 200

@ns.route('/register')
class Register(Resource):
    @ns.doc('register')
    @ns.expect(register_model)
    @ns.response(201, 'Usuario creado exitosamente')
    @ns.response(400, 'Datos inválidos')
    @ns.response(409, 'Usuario ya existe')
    def post(self):
        """Registrar nuevo usuario"""
        data = api.payload

        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        role_id = data.get('role_id', 2)

        if not email or not password or not full_name:
            return {'success': False, 'message': 'Todos los campos son requeridos'}, 400

        if len(password) < 6:
            return {'success': False, 'message': 'La contraseña debe tener al menos 6 caracteres'}, 400

        # Check existing
        if UserModel.get_by_email(email):
            return {'success': False, 'message': 'El email ya está registrado'}, 409

        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create user
        user = UserModel.create(role_id, full_name, email, password_hash)

        return {
            'success': True,
            'message': 'Usuario registrado exitosamente',
            'data': {'user': dict(user)}
        }, 201

@ns.route('/health')
class Health(Resource):
    @ns.doc('health_check')
    def get(self):
        """Verificar estado del servicio"""
        return {'success': True, 'data': {'status': 'healthy', 'service': 'auth'}}, 200

if __name__ == '__main__':
    port = int(os.getenv('AUTH_SERVICE_PORT', 5001))
    print(f"🚀 Auth Service con Swagger: http://localhost:{port}/docs")
    app.run(host='0.0.0.0', port=port, debug=True)
```

---

## 🧪 2. Pruebas Unitarias

### Estructura de Tests

```
Backend/
├── auth_service/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py         # Configuración de pytest
│   │   ├── test_auth.py        # Tests de autenticación
│   │   └── test_users.py       # Tests de usuarios
│   └── ...
```

### Ejemplo: Tests para Auth Service

**Archivo:** `auth_service/tests/conftest.py`

```python
"""
Configuración de pytest para Auth Service
"""
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from auth_service.app import app as flask_app

@pytest.fixture
def app():
    """Create application for testing"""
    flask_app.config.update({
        'TESTING': True,
    })
    yield flask_app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()
```

**Archivo:** `auth_service/tests/test_auth.py`

```python
"""
Tests para endpoints de autenticación
"""
import pytest
import json

class TestAuth:
    """Test class for authentication endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/auth/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['status'] == 'healthy'

    def test_login_missing_fields(self, client):
        """Test login with missing fields"""
        response = client.post('/api/auth/login',
                              json={},
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/api/auth/login',
                              json={
                                  'email': 'invalid@test.com',
                                  'password': 'wrongpass'
                              },
                              content_type='application/json')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] == False

    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post('/api/auth/register',
                              json={
                                  'email': f'test{__import__("time").time()}@test.com',
                                  'password': 'testpass123',
                                  'full_name': 'Test User',
                                  'role_id': 2
                              },
                              content_type='application/json')
        # Could be 201 (created) or 409 (already exists)
        assert response.status_code in [201, 409]

    def test_register_short_password(self, client):
        """Test registration with short password"""
        response = client.post('/api/auth/register',
                              json={
                                  'email': 'test@test.com',
                                  'password': '123',
                                  'full_name': 'Test User'
                              },
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'contraseña' in data['message'].lower() or 'password' in data['message'].lower()
```

### Ejecutar Tests

```bash
# Tests de un servicio específico
cd auth_service
pytest tests/ -v

# Tests con coverage
pytest tests/ --cov=. --cov-report=html

# Tests de todos los servicios
cd Backend
pytest */tests/ -v
```

---

## 🔗 3. Integración entre Servicios

### Arquitectura de Integración

Los microservicios se comunican entre sí mediante HTTP REST. Ejemplo de flujos:

1. **Crear Cita con Tratamiento**:
   - Citas Service → Inventario Service (verificar stock)
   - Citas Service → Historia Clínica Service (obtener datos del paciente)

2. **Generar Factura desde Cita**:
   - Facturación Service → Citas Service (obtener detalles de la cita)
   - Facturación Service → Inventario Service (obtener precios de productos)

### Utilidad para Llamadas entre Servicios

**Archivo:** `common/service_client.py`

```python
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


# Service clients
class AuthServiceClient(ServiceClient):
    def __init__(self):
        base_url = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001/api/auth')
        super().__init__(base_url, 'Auth Service')

    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token"""
        return self.get('/validate', token=token)


class InventarioServiceClient(ServiceClient):
    def __init__(self):
        base_url = os.getenv('INVENTARIO_SERVICE_URL', 'http://localhost:5002/api/inventario')
        super().__init__(base_url, 'Inventario Service')

    def check_treatment_stock(self, treatment_id: int, quantity: int, token: str) -> Dict[str, Any]:
        """Check if there's enough stock for a treatment"""
        return self.get(f'/treatments/{treatment_id}/check-stock', token=token, params={'quantity': quantity})

    def get_product(self, product_id: int, token: str) -> Dict[str, Any]:
        """Get product details"""
        return self.get(f'/products/{product_id}', token=token)


class HistoriaClinicaServiceClient(ServiceClient):
    def __init__(self):
        base_url = os.getenv('HISTORIA_CLINICA_SERVICE_URL', 'http://localhost:5003/api/historia-clinica')
        super().__init__(base_url, 'Historia Clinica Service')

    def get_patient(self, patient_id: int, token: str) -> Dict[str, Any]:
        """Get patient details"""
        return self.get(f'/patients/{patient_id}', token=token)


class CitasServiceClient(ServiceClient):
    def __init__(self):
        base_url = os.getenv('CITAS_SERVICE_URL', 'http://localhost:5005/api/citas')
        super().__init__(base_url, 'Citas Service')

    def get_appointment(self, appointment_id: int, token: str) -> Dict[str, Any]:
        """Get appointment with all details"""
        return self.get(f'/appointments/{appointment_id}', token=token)
```

### Ejemplo de Uso: Crear Factura desde Cita

**Archivo:** `facturacion_service/integration_example.py`

```python
"""
Ejemplo de integración: Crear factura automáticamente desde una cita
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.service_client import CitasServiceClient, InventarioServiceClient
from facturacion_service.models import InvoiceModel
from common.utils import calculate_iva

def create_invoice_from_appointment(appointment_id: int, token: str) -> dict:
    """
    Crea una factura automáticamente desde una cita completada

    Este flujo integra:
    1. Citas Service - obtener detalles de la cita
    2. Inventario Service - obtener precios de productos
    3. Facturación Service - crear la factura
    """

    # 1. Obtener detalles de la cita
    citas_client = CitasServiceClient()
    appointment = citas_client.get_appointment(appointment_id, token)

    if not appointment['success']:
        raise Exception('No se pudo obtener la cita')

    appointment_data = appointment['data']['appointment']

    # 2. Calcular subtotal
    subtotal = appointment_data['total']

    # 3. Calcular IVA
    iva_rate = 15.0
    iva_amount = calculate_iva(subtotal, iva_rate)
    total_amount = subtotal + iva_amount

    # 4. Generar número de factura
    invoice_number = InvoiceModel.get_next_invoice_number()

    # 5. Crear factura
    invoice = InvoiceModel.create(
        patient_id=appointment_data['patient_id'],
        appointment_id=appointment_id,
        invoice_number=invoice_number,
        issue_date=appointment_data['start_time'].date(),
        subtotal=subtotal,
        iva_rate=iva_rate,
        iva_amount=iva_amount,
        total_amount=total_amount,
        status='ISSUED'
    )

    return {
        'success': True,
        'message': 'Factura creada exitosamente desde la cita',
        'data': {
            'invoice': dict(invoice),
            'appointment_id': appointment_id
        }
    }
```

### Configurar URLs de Servicios

Agregar al `.env`:

```env
# Service URLs
AUTH_SERVICE_URL=http://localhost:5001/api/auth
INVENTARIO_SERVICE_URL=http://localhost:5002/api/inventario
HISTORIA_CLINICA_SERVICE_URL=http://localhost:5003/api/historia-clinica
FACTURACION_SERVICE_URL=http://localhost:5004/api/facturacion
CITAS_SERVICE_URL=http://localhost:5005/api/citas
```

---

## 🚀 Script de Ejecución de Tests

**Archivo:** `Backend/run_tests.sh`

```bash
#!/bin/bash

echo "=================================="
echo "Ejecutando tests de todos los servicios..."
echo "=================================="

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

failed=0

# Auth Service
echo ""
echo "Testing Auth Service..."
cd auth_service
pytest tests/ -v
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Auth Service tests failed${NC}"
    failed=1
else
    echo -e "${GREEN}✅ Auth Service tests passed${NC}"
fi
cd ..

# Inventario Service
echo ""
echo "Testing Inventario Service..."
cd inventario_service
pytest tests/ -v
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Inventario Service tests failed${NC}"
    failed=1
else
    echo -e "${GREEN}✅ Inventario Service tests passed${NC}"
fi
cd ..

# Historia Clinica Service
echo ""
echo "Testing Historia Clinica Service..."
cd historia_clinica_service
pytest tests/ -v
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Historia Clinica Service tests failed${NC}"
    failed=1
else
    echo -e "${GREEN}✅ Historia Clinica Service tests passed${NC}"
fi
cd ..

# Facturacion Service
echo ""
echo "Testing Facturacion Service..."
cd facturacion_service
pytest tests/ -v
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Facturacion Service tests failed${NC}"
    failed=1
else
    echo -e "${GREEN}✅ Facturacion Service tests passed${NC}"
fi
cd ..

# Citas Service
echo ""
echo "Testing Citas Service..."
cd citas_service
pytest tests/ -v
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Citas Service tests failed${NC}"
    failed=1
else
    echo -e "${GREEN}✅ Citas Service tests passed${NC}"
fi
cd ..

echo ""
echo "=================================="
if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✅ Todos los tests pasaron exitosamente!${NC}"
else
    echo -e "${RED}❌ Algunos tests fallaron${NC}"
    exit 1
fi
echo "=================================="
```

**Windows:** `Backend/run_tests.bat`

```batch
@echo off
echo ==================================
echo Ejecutando tests de todos los servicios...
echo ==================================

set failed=0

echo.
echo Testing Auth Service...
cd auth_service
pytest tests/ -v
if %ERRORLEVEL% NEQ 0 set failed=1
cd ..

echo.
echo Testing Inventario Service...
cd inventario_service
pytest tests/ -v
if %ERRORLEVEL% NEQ 0 set failed=1
cd ..

echo.
echo Testing Historia Clinica Service...
cd historia_clinica_service
pytest tests/ -v
if %ERRORLEVEL% NEQ 0 set failed=1
cd ..

echo.
echo Testing Facturacion Service...
cd facturacion_service
pytest tests/ -v
if %ERRORLEVEL% NEQ 0 set failed=1
cd ..

echo.
echo Testing Citas Service...
cd citas_service
pytest tests/ -v
if %ERRORLEVEL% NEQ 0 set failed=1
cd ..

echo.
echo ==================================
if %failed% EQU 0 (
    echo Todos los tests pasaron exitosamente!
) else (
    echo Algunos tests fallaron
    exit /b 1
)
echo ==================================
pause
```

---

## 📋 Checklist de Implementación

### Swagger

- [ ] Instalar dependencias (`pip install -r requirements.txt`)
- [ ] Crear configuración de Swagger en cada servicio
- [ ] Definir modelos de request/response
- [ ] Documentar todos los endpoints
- [ ] Verificar acceso a `/docs` en cada servicio

### Tests

- [ ] Crear estructura de directorios `tests/`
- [ ] Configurar pytest en `conftest.py`
- [ ] Escribir tests para cada endpoint
- [ ] Alcanzar >80% de cobertura
- [ ] Ejecutar tests automáticamente en CI/CD

### Integración

- [ ] Crear `service_client.py` en common
- [ ] Configurar URLs de servicios en `.env`
- [ ] Implementar clientes para cada servicio
- [ ] Crear ejemplos de flujos integrados
- [ ] Documentar casos de uso

---

## 🎯 Próximos Pasos

1. **Implementar Swagger**: Comenzar con Auth Service
2. **Crear Tests**: Escribir tests básicos para cada endpoint
3. **Integrar Servicios**: Implementar flujos comunes
4. **CI/CD**: Configurar GitHub Actions para tests automáticos
5. **Documentación**: Actualizar README con nuevas funcionalidades

---

**¡Sistema listo para desarrollo completo!** 🚀
