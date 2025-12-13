import requests
import json

BASE_URL = "http://localhost:5001/api/auth"
PATIENTS_URL = "http://localhost:5003/api/historia-clinica"
INVENTORY_URL = "http://localhost:5002/api/inventario"

def test_system():
    # 1. Login
    print("1. Intentando Login...")
    try:
        resp = requests.post(f"{BASE_URL}/login", json={
            "email": "admin@clinica.com",
            "password": "admin123"
        })
        print(f"Login Status: {resp.status_code}")
        if resp.status_code != 200:
            print(resp.text)
            return
        
        data = resp.json()
        token = data['data']['token']
        user = data['data']['user']
        print(f"Login OK. Usuario: {user['full_name']}")
        print(f"Token: {token[:20]}...")
    except Exception as e:
        print(f"Error Login: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Listar Pacientes
    print("\n2. Listando Pacientes...")
    try:
        # CORREGIDO: /patients en lugar de /pacientes
        resp = requests.get(f"{PATIENTS_URL}/patients", headers=headers)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            patients = resp.json()['data']['patients']
            print(f"Pacientes encontrados: {len(patients)}")
            for p in patients:
                print(f"- {p['first_name']} {p['last_name']} ({p['doc_number']})")
        else:
            print(resp.text)
    except Exception as e:
        print(f"Error Pacientes: {e}")

    # 3. Listar Inventario
    print("\n3. Listando Inventario...")
    try:
        # CORREGIDO: /products en lugar de /productos
        resp = requests.get(f"{INVENTORY_URL}/products", headers=headers)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            products = resp.json()['data']['products']
            print(f"Productos encontrados: {len(products)}")
            for p in products:
                print(f"- {p['name']} (Stock: {p['stock_quantity']})")
        else:
            print(resp.text)
    except Exception as e:
        print(f"Error Inventario: {e}")

if __name__ == "__main__":
    test_system()
