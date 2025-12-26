"""
Script para poblar la base de datos con datos realistas
Sistema Médico - Ecuador
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from datetime import datetime, timedelta
import random
from faker import Faker
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import common modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config import Config

load_dotenv()

fake = Faker('es_ES')

DATABASE_URL = Config.DATABASE_URL or os.getenv('DATABASE_URL')

def validar_cedula_ecuatoriana(cedula):
    """Validación de cédula ecuatoriana (10 dígitos)"""
    if len(cedula) != 10:
        return False

    try:
        digitos = [int(d) for d in cedula]
        provincia = int(cedula[:2])

        if provincia < 1 or provincia > 24:
            return False

        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        suma = 0

        for i in range(9):
            valor = digitos[i] * coeficientes[i]
            if valor >= 10:
                valor -= 9
            suma += valor

        digito_verificador = (10 - (suma % 10)) % 10
        return digito_verificador == digitos[9]
    except:
        return False

def generar_cedula_valida():
    """Genera una cédula ecuatoriana válida"""
    while True:
        provincia = random.randint(1, 24)
        cedula_base = f"{provincia:02d}" + "".join([str(random.randint(0, 9)) for _ in range(7)])

        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        suma = 0

        for i in range(9):
            valor = int(cedula_base[i]) * coeficientes[i]
            if valor >= 10:
                valor -= 9
            suma += valor

        digito_verificador = (10 - (suma % 10)) % 10
        cedula = cedula_base + str(digito_verificador)

        if validar_cedula_ecuatoriana(cedula):
            return cedula

def conectar_db():
    """Conecta a la base de datos"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def poblar_roles(conn):
    """Crea los roles del sistema"""
    print("Poblando roles...")
    cursor = conn.cursor()

    roles = [
        (1, 'admin'),
        (2, 'doctor'),
        (3, 'receptionist')
    ]

    for role_id, name in roles:
        cursor.execute("""
            INSERT INTO roles (role_id, name)
            VALUES (%s, %s)
            ON CONFLICT (role_id) DO UPDATE
            SET name = EXCLUDED.name
        """, (role_id, name))

    conn.commit()
    cursor.close()
    print(f"  -> {len(roles)} roles creados\n")

def poblar_usuarios(conn):
    """Crea usuarios del sistema"""
    print("Poblando usuarios...")
    cursor = conn.cursor()

    usuarios = [
        (1, 'Admin Sistema', 'admin@clinica.ec', 'admin123'),
        (3, 'Dr. Carlos Mendoza', 'cmendoza@clinica.ec', 'doctor123'),
        (3, 'Dra. María González', 'mgonzalez@clinica.ec', 'doctor123'),
        (3, 'Dr. Juan Pérez', 'jperez@clinica.ec', 'doctor123'),
        (2, 'Sofía Ramírez', 'sramirez@clinica.ec', 'recep123'),
        (2, 'Ana Torres', 'atorres@clinica.ec', 'recep123'),
    ]

    for role_id, full_name, email, password in usuarios:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8')
        cursor.execute("""
            INSERT INTO users (role_id, full_name, email, password_hash)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, (role_id, full_name, email, password_hash))

    conn.commit()
    print(f"OK {len(usuarios)} usuarios creados")

def poblar_pacientes(conn, cantidad=50):
    """Genera pacientes con cédulas ecuatorianas válidas"""
    print(f"Generando {cantidad} pacientes...")
    cursor = conn.cursor()

    tipos_sangre = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']

    for i in range(cantidad):
        cedula = generar_cedula_valida()
        nombre = fake.first_name()
        apellido = fake.last_name()
        full_name = f"{nombre} {apellido}"

        fecha_nacimiento = fake.date_of_birth(minimum_age=1, maximum_age=90)
        telefono = f"09{random.randint(10000000, 99999999)}"
        email = f"{nombre.lower()}.{apellido.lower()}@gmail.com"
        direccion = fake.address()
        tipo_sangre = random.choice(tipos_sangre)

        cursor.execute("""
            INSERT INTO patients (identification, full_name, date_of_birth, phone, email, address, blood_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (identification) DO NOTHING
        """, (cedula, full_name, fecha_nacimiento, telefono, email, direccion, tipo_sangre))

    conn.commit()
    print(f"OK {cantidad} pacientes generados")

def poblar_productos(conn):
    """Crea productos médicos"""
    print("Poblando inventario...")
    cursor = conn.cursor()

    productos = [
        ('Paracetamol 500mg', 'Tableta', 'Analgésico antipirético', 0.50, 1000, 100, True, 15),
        ('Ibuprofeno 400mg', 'Tableta', 'Antiinflamatorio no esteroideo', 0.75, 800, 100, True, 15),
        ('Amoxicilina 500mg', 'Cápsula', 'Antibiótico de amplio espectro', 1.20, 500, 50, True, 15),
        ('Omeprazol 20mg', 'Cápsula', 'Inhibidor de bomba de protones', 0.90, 600, 80, True, 15),
        ('Losartán 50mg', 'Tableta', 'Antihipertensivo', 1.50, 400, 60, True, 15),
        ('Metformina 850mg', 'Tableta', 'Antidiabético oral', 0.80, 500, 70, True, 15),
        ('Atorvastatina 20mg', 'Tableta', 'Hipolipemiante', 1.80, 300, 50, True, 15),
        ('Salbutamol inhalador', 'Aerosol', 'Broncodilatador', 8.50, 100, 20, True, 0),
        ('Diclofenaco gel 1%', 'Gel tópico', 'Antiinflamatorio tópico', 5.20, 150, 25, True, 0),
        ('Alcohol antiséptico 70%', 'Solución', 'Desinfectante', 2.50, 200, 30, False, 0),
        ('Gasas estériles pack x10', 'Material médico', 'Curación de heridas', 1.50, 300, 50, False, 0),
        ('Jeringas 5ml desechables', 'Material médico', 'Administración parenteral', 0.25, 1000, 100, False, 0),
        ('Guantes látex talla M x100', 'Material médico', 'Protección personal', 8.00, 150, 20, False, 0),
        ('Termómetro digital', 'Equipo médico', 'Medición temperatura', 12.00, 50, 10, False, 0),
        ('Tensiómetro digital', 'Equipo médico', 'Medición presión arterial', 45.00, 20, 5, False, 0),
        ('Vitamina C 1000mg', 'Tableta', 'Suplemento vitamínico', 0.60, 500, 80, True, 0),
        ('Complejo B', 'Tableta', 'Suplemento vitamínico', 0.70, 400, 60, True, 0),
        ('Suero oral 500ml', 'Solución', 'Rehidratación oral', 1.20, 200, 40, False, 0),
        ('Clotrimazol crema 1%', 'Crema tópica', 'Antimicótico', 3.50, 120, 25, True, 0),
        ('Cetirizina 10mg', 'Tableta', 'Antihistamínico', 0.40, 600, 100, True, 15),
    ]

    for nombre, tipo, descripcion, precio_unitario, stock_actual, stock_minimo, requiere_receta, iva_porcentaje in productos:
        cursor.execute("""
            INSERT INTO products (name, type, description, unit_price, current_stock, minimum_stock, requires_prescription, iva_percentage)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (nombre, tipo, descripcion, precio_unitario, stock_actual, stock_minimo, requiere_receta, iva_porcentaje))

    conn.commit()
    print(f"OK {len(productos)} productos agregados")

def poblar_tratamientos(conn):
    """Crea tratamientos con recetas médicas"""
    print("Poblando tratamientos...")
    cursor = conn.cursor()

    tratamientos = [
        ('Tratamiento Gripe Común', 'Manejo sintomático de gripe', 15.00, 0, [
            (1, 'Paracetamol 500mg', 12, 'Tomar 1 tableta cada 8 horas por 3 días'),
            (20, 'Cetirizina 10mg', 6, 'Tomar 1 tableta cada 12 horas por 3 días'),
            (16, 'Vitamina C 1000mg', 10, 'Tomar 1 tableta diaria por 10 días'),
        ]),
        ('Tratamiento Infección Bacteriana', 'Antibiótico + analgésico', 25.00, 0, [
            (3, 'Amoxicilina 500mg', 21, 'Tomar 1 cápsula cada 8 horas por 7 días'),
            (2, 'Ibuprofeno 400mg', 12, 'Tomar 1 tableta cada 8 horas por 4 días si hay dolor'),
        ]),
        ('Control Hipertensión Arterial', 'Manejo crónico de HTA', 30.00, 0, [
            (5, 'Losartán 50mg', 30, 'Tomar 1 tableta diaria en la mañana'),
        ]),
        ('Control Diabetes Tipo 2', 'Manejo de diabetes', 20.00, 0, [
            (6, 'Metformina 850mg', 60, 'Tomar 1 tableta cada 12 horas con alimentos'),
        ]),
        ('Tratamiento Gastritis', 'Protector gástrico', 18.00, 0, [
            (4, 'Omeprazol 20mg', 30, 'Tomar 1 cápsula en ayunas por 30 días'),
        ]),
        ('Tratamiento Dolor Muscular', 'Antiinflamatorio tópico y oral', 22.00, 0, [
            (2, 'Ibuprofeno 400mg', 15, 'Tomar 1 tableta cada 8 horas por 5 días'),
            (9, 'Diclofenaco gel 1%', 1, 'Aplicar en zona afectada 3 veces al día'),
        ]),
        ('Curaci\u00f3n de Herida Menor', 'Materiales para curación', 8.00, 0, [
            (10, 'Alcohol antiséptico 70%', 1, 'Desinfectar la zona'),
            (11, 'Gasas estériles pack x10', 1, 'Cubrir la herida'),
        ]),
    ]

    cursor.execute("SELECT product_id, name FROM products")
    productos_db = {row['name']: row['product_id'] for row in cursor.fetchall()}

    for nombre, descripcion, precio_base, iva_porcentaje, receta in tratamientos:
        cursor.execute("""
            INSERT INTO treatments (name, description, base_price, iva_percentage, is_active)
            VALUES (%s, %s, %s, %s, true)
            RETURNING treatment_id
        """, (nombre, descripcion, precio_base, iva_porcentaje))
        treatment_id = cursor.fetchone()['treatment_id']

        for _, producto_nombre, cantidad, instrucciones in receta:
            product_id = productos_db.get(producto_nombre)
            if product_id:
                cursor.execute("""
                    INSERT INTO treatment_recipes (treatment_id, product_id, quantity, instructions)
                    VALUES (%s, %s, %s, %s)
                """, (treatment_id, product_id, cantidad, instrucciones))

    conn.commit()
    print(f"OK {len(tratamientos)} tratamientos con recetas creados")

def poblar_citas(conn, cantidad=100):
    """Genera citas médicas"""
    print(f"Generando {cantidad} citas...")
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE role_id = 3")
    doctores = [row['user_id'] for row in cursor.fetchall()]

    cursor.execute("SELECT patient_id FROM patients LIMIT 50")
    pacientes = [row['patient_id'] for row in cursor.fetchall()]

    cursor.execute("SELECT treatment_id, name FROM treatments")
    tratamientos = {row['treatment_id']: row['name'] for row in cursor.fetchall()}

    estados = ['scheduled', 'completed', 'cancelled', 'no_show']

    inicio = datetime.now() - timedelta(days=60)

    for i in range(cantidad):
        doctor_id = random.choice(doctores)
        patient_id = random.choice(pacientes)
        treatment_id = random.choice(list(tratamientos.keys())) if random.random() > 0.3 else None

        fecha_cita = inicio + timedelta(days=random.randint(0, 90))
        hora = random.choice([8, 9, 10, 11, 14, 15, 16, 17])
        appointment_date = fecha_cita.replace(hour=hora, minute=0, second=0)

        if appointment_date < datetime.now():
            status = random.choices(estados, weights=[0.1, 0.7, 0.1, 0.1])[0]
        else:
            status = 'scheduled'

        motivo = random.choice([
            'Consulta general',
            'Control rutinario',
            'Dolor abdominal',
            'Cefalea',
            'Fiebre',
            'Dolor de garganta',
            'Control presión arterial',
            'Control glucosa',
            'Renovación de receta',
        ])

        notas = f"Paciente refiere {motivo.lower()}" if status == 'completed' else None

        cursor.execute("""
            INSERT INTO appointments (patient_id, doctor_id, treatment_id, appointment_date, status, notes, reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (patient_id, doctor_id, treatment_id, appointment_date, status, notas, motivo))

    conn.commit()
    print(f"OK {cantidad} citas generadas")

def poblar_facturas(conn, cantidad=50):
    """Genera facturas"""
    print(f"Generando {cantidad} facturas...")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.appointment_id, a.patient_id, a.doctor_id, a.treatment_id
        FROM appointments a
        WHERE a.status = 'completed'
        ORDER BY RANDOM()
        LIMIT %s
    """, (cantidad,))
    citas = cursor.fetchall()

    cursor.execute("SELECT treatment_id, base_price, iva_percentage FROM treatments")
    tratamientos = {row['treatment_id']: (row['base_price'], row['iva_percentage']) for row in cursor.fetchall()}

    for cita in citas:
        subtotal = 20.00
        iva_porcentaje = 15.0

        if cita['treatment_id'] and cita['treatment_id'] in tratamientos:
            precio_tratamiento, iva_tratamiento = tratamientos[cita['treatment_id']]
            subtotal += float(precio_tratamiento)
            iva_porcentaje = max(iva_porcentaje, float(iva_tratamiento))

        iva = subtotal * (iva_porcentaje / 100)
        total = subtotal + iva

        payment_method = random.choice(['Efectivo', 'Tarjeta', 'Transferencia'])
        status = random.choices(['paid', 'pending', 'cancelled'], weights=[0.85, 0.10, 0.05])[0]

        cursor.execute("""
            INSERT INTO invoices (appointment_id, patient_id, subtotal, iva_percentage, iva, total, payment_method, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (cita['appointment_id'], cita['patient_id'], subtotal, iva_porcentaje, iva, total, payment_method, status))

    conn.commit()
    print(f"OK {cantidad} facturas generadas")

def poblar_gastos(conn):
    """Genera gastos operacionales"""
    print("Generando gastos operacionales...")
    cursor = conn.cursor()

    categorias = ['Servicios básicos', 'Mantenimiento', 'Suministros', 'Personal', 'Otros']

    gastos = [
        ('Luz eléctrica', 'Servicios básicos', 120.00),
        ('Agua potable', 'Servicios básicos', 45.00),
        ('Internet', 'Servicios básicos', 50.00),
        ('Limpieza y mantenimiento', 'Mantenimiento', 200.00),
        ('Insumos de oficina', 'Suministros', 80.00),
        ('Pago nómina', 'Personal', 3500.00),
        ('Seguro médico', 'Otros', 150.00),
        ('Alquiler local', 'Otros', 800.00),
    ]

    for descripcion, categoria, monto in gastos:
        fecha = datetime.now() - timedelta(days=random.randint(1, 30))

        cursor.execute("""
            INSERT INTO expenses (description, category, amount, expense_date)
            VALUES (%s, %s, %s, %s)
        """, (descripcion, categoria, monto, fecha))

    conn.commit()
    print(f"OK {len(gastos)} gastos registrados")

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("SISTEMA DE POBLADO DE DATOS - CLÍNICA MÉDICA ECUADOR")
    print("="*60 + "\n")

    try:
        conn = conectar_db()
        print("Conectado a la base de datos\n")

        poblar_roles(conn)
        poblar_usuarios(conn)
        poblar_pacientes(conn, 50)
        poblar_productos(conn)
        poblar_tratamientos(conn)
        poblar_citas(conn, 100)
        poblar_facturas(conn, 50)
        poblar_gastos(conn)

        conn.close()

        print("\n" + "="*60)
        print("PROCESO COMPLETADO EXITOSAMENTE")
        print("="*60)
        print("\nCredenciales de acceso:")
        print("  Admin:      admin@clinica.ec / admin123")
        print("  Doctor:     cmendoza@clinica.ec / doctor123")
        print("  Recepcion:  sramirez@clinica.ec / recep123")
        print("\n")

    except Exception as e:
        print(f"\nERROR: {str(e)}\n")
        raise

if __name__ == '__main__':
    main()
