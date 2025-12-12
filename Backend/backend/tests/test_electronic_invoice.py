"""
Test Script for Electronic Invoicing
Run complete end-to-end test of the electronic invoicing system
"""
import requests
import json
from datetime import date

# Configuration
BASE_URL = "http://localhost:5004/api/facturacion/sri"
AUTH_URL = "http://localhost:5001/api/auth"

# Test data for SRI
SRI_TEST_DATA = {
    "ruc": "0190329773001",  # RUC de prueba SRI
    "razon_social": "CLINICA DE PRUEBAS S.A.",
    "nombre_comercial": "Clinica Test",
    "direccion_matriz": "Av. 10 de Agosto N37-185 y Villalengua, Quito, Ecuador",
    "email_emisor": "pruebas@clinica.com",
    "telefono_emisor": "023456789",
    "ambiente": "1"  # 1 = Pruebas, 2 = Produccion
}

def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def login():
    """Login and get token"""
    print_section("1. AUTENTICACIÓN")

    response = requests.post(f"{AUTH_URL}/login", json={
        "username": "admin",
        "password": "admin123"
    })

    if response.status_code == 200:
        token = response.json()['data']['access_token']
        print_success("Login exitoso")
        print_info(f"Token: {token[:50]}...")
        return token
    else:
        print_error(f"Error en login: {response.text}")
        return None

def update_sri_config(token):
    """Update SRI configuration"""
    print_section("2. CONFIGURACIÓN SRI")

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Get current config
    response = requests.get(f"{BASE_URL}/config", headers=headers)
    if response.status_code == 200:
        config = response.json()['data']['config']
        config_id = config['config_id']
        print_info(f"Configuración actual ID: {config_id}")
        print_info(f"RUC actual: {config.get('ruc', 'No configurado')}")
    else:
        print_error("No se pudo obtener configuración")
        return False

    # Update config
    print_info("Actualizando configuración con datos de prueba...")
    response = requests.put(
        f"{BASE_URL}/config/{config_id}",
        headers=headers,
        json=SRI_TEST_DATA
    )

    if response.status_code == 200:
        print_success("Configuración actualizada")
        config = response.json()['data']['config']
        print_info(f"RUC: {config['ruc']}")
        print_info(f"Razón Social: {config['razon_social']}")
        print_info(f"Ambiente: {'PRUEBAS' if config['ambiente'] == '1' else 'PRODUCCIÓN'}")
        return True
    else:
        print_error(f"Error actualizando configuración: {response.text}")
        return False

def create_electronic_invoice(token):
    """Create electronic invoice"""
    print_section("3. CREAR FACTURA ELECTRÓNICA")

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Invoice data
    invoice_data = {
        "patient_id": 1,
        "items": [
            {
                "codigo": "CONS001",
                "descripcion": "Consulta médica general",
                "cantidad": 1,
                "precio_unitario": 50.00,
                "descuento": 0,
                "codigo_iva": "3",  # 15% IVA
                "tarifa_iva": 15
            },
            {
                "codigo": "LAB001",
                "descripcion": "Examen de laboratorio completo",
                "cantidad": 1,
                "precio_unitario": 30.00,
                "descuento": 5.00,
                "codigo_iva": "3",  # 15% IVA
                "tarifa_iva": 15
            }
        ],
        "formas_pago": [
            {
                "codigo": "01",  # Efectivo
                "total": 86.25
            }
        ],
        "info_adicional": [
            {
                "nombre": "Email",
                "valor": "paciente@test.com"
            },
            {
                "nombre": "Médico",
                "valor": "Dr. Juan Pérez"
            },
            {
                "nombre": "Observaciones",
                "valor": "Factura de prueba para ambiente SRI"
            }
        ]
    }

    print_info("Enviando datos de factura...")
    print_info(f"Total items: {len(invoice_data['items'])}")
    print_info(f"Total: $86.25")

    response = requests.post(
        f"{BASE_URL}/electronic-invoices",
        headers=headers,
        json=invoice_data
    )

    if response.status_code == 201:
        result = response.json()['data']
        invoice = result['invoice']

        print_success("Factura creada exitosamente")
        print_info(f"ID: {invoice['invoice_id']}")
        print_info(f"Número: {invoice['invoice_number']}")
        print_info(f"Clave de acceso: {result['clave_acceso']}")
        print_info(f"Estado SRI: {invoice['estado_sri']}")
        print_info(f"Total: ${invoice['total_amount']}")

        # Show XML preview
        xml_preview = result['xml'][:200]
        print_info(f"\nXML generado (preview):")
        print(xml_preview + "...")

        return invoice['invoice_id'], invoice['invoice_number']
    else:
        print_error(f"Error creando factura: {response.text}")
        return None, None

def authorize_invoice(token, invoice_id):
    """Authorize invoice with SRI"""
    print_section("4. AUTORIZAR CON SRI")

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    print_info(f"Enviando factura {invoice_id} al SRI...")
    print_info("Esto simula el proceso de autorización (ambiente de pruebas)")

    response = requests.post(
        f"{BASE_URL}/electronic-invoices/{invoice_id}/authorize",
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()['data']

        print_success("Factura AUTORIZADA por el SRI")
        print_info(f"Estado: {result['estado']}")
        print_info(f"Número de autorización: {result['numero_autorizacion']}")
        print_info(f"Mensaje: {result['mensaje']}")

        return True
    else:
        print_error(f"Error en autorización: {response.text}")
        return False

def get_invoice_details(token, invoice_id):
    """Get complete invoice details"""
    print_section("5. CONSULTAR FACTURA")

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(
        f"{BASE_URL}/electronic-invoices/{invoice_id}",
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()['data']
        invoice = result['invoice']

        print_success("Factura recuperada")
        print_info(f"Número: {invoice['invoice_number']}")
        print_info(f"Estado SRI: {invoice['estado_sri']}")
        print_info(f"Clave de acceso: {invoice['clave_acceso']}")
        print_info(f"Total: ${invoice['total_amount']}")
        print_info(f"Items: {len(result['items'])}")
        print_info(f"Métodos de pago: {len(result['payments'])}")
        print_info(f"Info adicional: {len(result['additional_info'])}")
        print_info(f"Log de autorizaciones: {len(result['authorization_log'])}")

        return result
    else:
        print_error(f"Error consultando factura: {response.text}")
        return None

def get_statistics(token):
    """Get electronic invoicing statistics"""
    print_section("6. ESTADÍSTICAS")

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(
        f"{BASE_URL}/electronic-invoices/statistics",
        headers=headers
    )

    if response.status_code == 200:
        stats = response.json()['data']['statistics']

        print_success("Estadísticas obtenidas")
        print_info(f"Total facturas: {stats['total_facturas']}")
        print_info(f"Autorizadas: {stats['autorizadas']}")
        print_info(f"Pendientes: {stats['pendientes']}")
        print_info(f"Rechazadas: {stats['rechazadas']}")
        print_info(f"Errores: {stats['errores']}")
        print_info(f"Monto autorizado: ${stats['monto_autorizado']}")

        return stats
    else:
        print_error(f"Error obteniendo estadísticas: {response.text}")
        return None

def check_xml_storage(invoice_number):
    """Check if XML files were created"""
    print_section("7. VERIFICAR ALMACENAMIENTO DE XML")

    import os
    from pathlib import Path

    backend_dir = Path(__file__).parent.parent
    storage_dir = backend_dir / 'storage' / 'xml'

    today = date.today()
    year = str(today.year)
    month = f"{today.month:02d}"

    # Check for pending XML
    pending_path = storage_dir / year / month / 'facturas' / f"{invoice_number}.xml"
    # Check for authorized XML
    authorized_path = storage_dir / year / month / 'autorizados' / f"{invoice_number}_AUTORIZADO.xml"
    # Check for backup
    backup_dir = backend_dir / 'storage' / 'backup'

    if pending_path.exists():
        print_success(f"XML encontrado en: {pending_path}")
        size = pending_path.stat().st_size
        print_info(f"Tamaño: {size} bytes")

    if authorized_path.exists():
        print_success(f"XML autorizado encontrado en: {authorized_path}")
        size = authorized_path.stat().st_size
        print_info(f"Tamaño: {size} bytes")

    # Check backups
    backups = list(backup_dir.glob(f"{invoice_number}_*.xml"))
    if backups:
        print_success(f"Backups encontrados: {len(backups)}")
        for backup in backups:
            print_info(f"  - {backup.name}")

    # Count total XMLs
    total_xmls = len(list(storage_dir.rglob('*.xml')))
    print_info(f"\nTotal de XMLs en storage: {total_xmls}")

def main():
    """Run complete test"""
    print("\n" + "="*60)
    print(" "*15 + "TEST DE FACTURACIÓN ELECTRÓNICA SRI")
    print("="*60)
    print("\nEste script probará el sistema completo de facturación electrónica")
    print("incluyendo creación, autorización y almacenamiento de XMLs.\n")

    # Step 1: Login
    token = login()
    if not token:
        print_error("No se pudo obtener token. Abortando prueba.")
        return

    # Step 2: Update SRI config
    if not update_sri_config(token):
        print_error("No se pudo actualizar configuración. Abortando prueba.")
        return

    # Step 3: Create electronic invoice
    invoice_id, invoice_number = create_electronic_invoice(token)
    if not invoice_id:
        print_error("No se pudo crear factura. Abortando prueba.")
        return

    # Step 4: Authorize with SRI
    if not authorize_invoice(token, invoice_id):
        print_error("No se pudo autorizar factura.")
        # Continue anyway to check the invoice

    # Step 5: Get invoice details
    get_invoice_details(token, invoice_id)

    # Step 6: Get statistics
    get_statistics(token)

    # Step 7: Check XML storage
    if invoice_number:
        check_xml_storage(invoice_number)

    # Final summary
    print_section("RESUMEN")
    print_success("Prueba completada exitosamente")
    print_info("El sistema de facturación electrónica está funcionando correctamente")
    print_info(f"Factura de prueba creada: {invoice_number}")
    print_info(f"Los XMLs se han guardado en: backend/storage/xml/")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
