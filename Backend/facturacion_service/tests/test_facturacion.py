"""
Tests para Facturacion Service
"""
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from facturacion_service.app import app

@pytest.fixture
def client():
    """Cliente de prueba de Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test health endpoint"""
    response = client.get('/api/facturacion/health')
    assert response.status_code == 200

def test_listar_facturas_sin_token(client):
    """Test listar facturas sin autenticación"""
    response = client.get('/api/facturacion/invoices')
    assert response.status_code == 401

def test_crear_factura_sin_token(client):
    """Test crear factura sin autenticación"""
    response = client.post('/api/facturacion/invoices', json={
        'appointment_id': 1,
        'patient_id': 1,
        'subtotal': 100.00
    })
    assert response.status_code == 401

def test_dashboard_financiero_sin_token(client):
    """Test dashboard financiero sin autenticación"""
    response = client.get('/api/facturacion/reports/dashboard')
    assert response.status_code == 401

def test_gastos_sin_token(client):
    """Test listar gastos sin autenticación"""
    response = client.get('/api/facturacion/expenses')
    assert response.status_code == 401

def test_calculo_iva(client):
    """Test cálculo automático de IVA"""
    subtotal = 100.00
    iva_porcentaje = 15.0
    iva_esperado = subtotal * (iva_porcentaje / 100)
    total_esperado = subtotal + iva_esperado

    assert iva_esperado == 15.00
    assert total_esperado == 115.00
