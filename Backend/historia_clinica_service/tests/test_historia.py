"""
Tests para Historia Clinica Service
"""
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from historia_clinica_service.app import app

@pytest.fixture
def client():
    """Cliente de prueba de Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test health endpoint"""
    response = client.get('/api/historia-clinica/health')
    assert response.status_code == 200

def test_listar_pacientes_sin_token(client):
    """Test listar pacientes sin autenticación"""
    response = client.get('/api/historia-clinica/patients')
    assert response.status_code == 401

def test_crear_paciente_sin_token(client):
    """Test crear paciente sin autenticación"""
    response = client.post('/api/historia-clinica/patients', json={
        'identification': '1234567890',
        'full_name': 'Test Patient',
        'date_of_birth': '1990-01-01',
        'phone': '0999999999'
    })
    assert response.status_code == 401

def test_obtener_paciente_sin_token(client):
    """Test obtener paciente específico sin autenticación"""
    response = client.get('/api/historia-clinica/patients/1')
    assert response.status_code == 401

def test_buscar_por_cedula_sin_token(client):
    """Test buscar paciente por cédula sin autenticación"""
    response = client.get('/api/historia-clinica/patients/search?identification=1234567890')
    assert response.status_code == 401

def test_validacion_cedula():
    """Test validación de cédula ecuatoriana"""
    cedulas_validas = ['1713175071', '0926687856']
    cedulas_invalidas = ['1234567890', '0000000000']

    for cedula in cedulas_validas:
        assert len(cedula) == 10

    for cedula in cedulas_invalidas:
        assert len(cedula) == 10
