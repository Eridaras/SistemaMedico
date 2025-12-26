"""
Tests para Citas Service
"""
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from citas_service.app import app

@pytest.fixture
def client():
    """Cliente de prueba de Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test health endpoint"""
    response = client.get('/api/citas/health')
    assert response.status_code == 200

def test_listar_citas_sin_token(client):
    """Test listar citas sin autenticación"""
    response = client.get('/api/citas/appointments')
    assert response.status_code == 401

def test_crear_cita_sin_token(client):
    """Test crear cita sin autenticación"""
    response = client.post('/api/citas/appointments', json={
        'patient_id': 1,
        'doctor_id': 1,
        'appointment_date': '2025-12-30T10:00:00',
        'reason': 'Consulta general'
    })
    assert response.status_code == 401

def test_disponibilidad_doctor_sin_token(client):
    """Test verificar disponibilidad doctor sin autenticación"""
    response = client.get('/api/citas/availability/doctor/1?date=2025-12-30')
    assert response.status_code == 401

def test_actualizar_estado_sin_token(client):
    """Test actualizar estado cita sin autenticación"""
    response = client.put('/api/citas/appointments/1/status', json={
        'status': 'completed'
    })
    assert response.status_code == 401
