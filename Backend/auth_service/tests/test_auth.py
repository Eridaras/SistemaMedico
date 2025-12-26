"""
Tests para Auth Service
"""
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from auth_service.app import app

@pytest.fixture
def client():
    """Cliente de prueba de Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test health endpoint"""
    response = client.get('/api/auth/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert data['data']['status'] == 'healthy'

def test_login_sin_credenciales(client):
    """Test login sin datos"""
    response = client.post('/api/auth/login', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] == False

def test_login_email_invalido(client):
    """Test login con email inválido"""
    response = client.post('/api/auth/login', json={
        'email': 'invalid-email',
        'password': 'test123'
    })
    assert response.status_code == 400

def test_register_sin_datos(client):
    """Test registro sin datos"""
    response = client.post('/api/auth/register', json={})
    assert response.status_code == 400

def test_register_password_corto(client):
    """Test registro con contraseña corta"""
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'password': '123',
        'full_name': 'Test User'
    })
    assert response.status_code == 400

def test_validate_sin_token(client):
    """Test validación sin token"""
    response = client.get('/api/auth/validate')
    assert response.status_code == 401

def test_usuarios_sin_token(client):
    """Test listar usuarios sin autenticación"""
    response = client.get('/api/auth/users')
    assert response.status_code == 401

def test_roles_sin_token(client):
    """Test listar roles sin autenticación"""
    response = client.get('/api/auth/roles')
    assert response.status_code == 401
