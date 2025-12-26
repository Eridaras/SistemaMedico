"""
Tests para Inventario Service
"""
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from inventario_service.app import app

@pytest.fixture
def client():
    """Cliente de prueba de Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test health endpoint"""
    response = client.get('/api/inventario/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True

def test_listar_productos_sin_token(client):
    """Test listar productos sin autenticación"""
    response = client.get('/api/inventario/products')
    assert response.status_code == 401

def test_crear_producto_sin_token(client):
    """Test crear producto sin autenticación"""
    response = client.post('/api/inventario/products', json={
        'name': 'Test Product',
        'type': 'Medicina',
        'unit_price': 10.00,
        'current_stock': 100
    })
    assert response.status_code == 401

def test_listar_tratamientos_sin_token(client):
    """Test listar tratamientos sin autenticación"""
    response = client.get('/api/inventario/treatments')
    assert response.status_code == 401

def test_stock_bajo_sin_token(client):
    """Test productos con stock bajo sin autenticación"""
    response = client.get('/api/inventario/products/low-stock')
    assert response.status_code == 401

def test_motor_recetas_sin_token(client):
    """Test motor de recetas sin autenticación"""
    response = client.get('/api/inventario/treatments/1/recipe')
    assert response.status_code == 401
