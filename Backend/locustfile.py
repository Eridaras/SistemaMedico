"""
Locust Load Test Script
Sistema Médico Integral - Sprint 5-6

Ejecutar con:
    locust -f locustfile.py --host=http://localhost:5001
"""
from locust import HttpUser, task, between
import json
import random

class MedicalSystemUser(HttpUser):
    wait_time = between(1, 5)
    token = None

    def on_start(self):
        """Autenticarse al iniciar usuario virtual"""
        # Ajustar credenciales según tu entorno de pruebas
        response = self.client.post("/api/auth/login", json={
            "email": "admin@sistema.com",
            "password": "admin"
        })
        
        if response.status_code == 200:
            self.token = response.json().get("token")
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
            print("Usuario autenticado correctamente")
        else:
            print(f"Error login: {response.text}")

    @task(3)
    def view_dashboard_data(self):
        """Simular carga de datos dashboard (lectura frecuente)"""
        # Estos endpoints deben existir en tu API real
        self.client.get("/api/citas/dashboard", name="Dashboard Citas")
        self.client.get("/api/facturacion/resumen", name="Resumen Facturación")

    @task(2)
    def search_patients(self):
        """Simular búsqueda de pacientes"""
        if not self.token: return
        
        terms = ["Juan", "Maria", "Carlos", "Ana", "Luis"]
        term = random.choice(terms)
        self.client.get(f"/api/historia-clinica/pacientes?search={term}", name="Buscar Pacientes")

    @task(1)
    def create_appointment_attempt(self):
        """Simular intento de agendar cita (escritura)"""
        if not self.token: return
        
        # Payload de ejemplo
        data = {
            "patient_id": 1,
            "doctor_id": 1,
            "date": "2025-12-25",
            "time": "10:00",
            "reason": "Consulta General (Load Test)"
        }
        # Usamos POST pero esperamos que valida validaciones
        self.client.post("/api/citas/agendar", json=data, name="Crear Cita")

    @task(1)
    def check_metrics(self):
        """Verificar que el endpoint de métricas responde"""
        self.client.get("/metrics", name="Prometheus Metrics")
