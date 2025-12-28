"""
Script para poblar la base de datos con datos realistas V2
Optimizado para esquema escalable
Sistema Médico - Ecuador
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from datetime import datetime, timedelta, date
import random
from faker import Faker
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config import Config

load_dotenv()

fake = Faker('es_ES')

DATABASE_URL = Config.DATABASE_URL or os.getenv('DATABASE_URL')

def validar_cedula_ecuatoriana(cedula):
    """Validación de cédula ecuatoriana (10 dígitos)"""
    if len(cedula) != 10:
        return False

    # Los primeros 2 dígitos deben ser válidos (provincia)
    provincia = int(cedula[0:2])
    if provincia < 1 or provincia > 24:
        return False

    # El tercer dígito debe ser menor a 6
    tercer_digito = int(cedula[2])
    if tercer_digito > 5:
        return False

    # Validar dígito verificador
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0

    for i in range(9):
        valor = int(cedula[i]) * coeficientes[i]
        if valor > 9:
            valor -= 9
        suma += valor

    digito_verificador = (10 - (suma % 10)) % 10

    return digito_verificador == int(cedula[9])

def generar_cedula_valida():
    """Genera una cédula ecuatoriana válida"""
    while True:
        provincia = random.randint(1, 24)
        tercer_digito = random.randint(0, 5)
        cedula_base = f"{provincia:02d}{tercer_digito}" + ''.join([str(random.randint(0, 9)) for _ in range(6)])

        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        suma = 0

        for i in range(9):
            valor = int(cedula_base[i]) * coeficientes[i]
            if valor > 9:
                valor -= 9
            suma += valor

        digito_verificador = (10 - (suma % 10)) % 10
        cedula = cedula_base + str(digito_verificador)

        if validar_cedula_ecuatoriana(cedula):
            return cedula

def conectar_db():
    """Conecta a la base de datos"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def poblar_usuarios(conn):
    """Crea usuarios del sistema"""
    print("Poblando usuarios...")
    cursor = conn.cursor()

    usuarios = [
        (1, 'Admin Sistema', 'admin@clinica.ec', 'admin123'),
        (2, 'Dr. Carlos Mendoza', 'cmendoza@clinica.ec', 'doctor123'),
        (2, 'Dra. María Rodríguez', 'mrodriguez@clinica.ec', 'doctor123'),
        (2, 'Dr. Juan Pérez', 'jperez@clinica.ec', 'doctor123'),
        (3, 'Sara Ramírez', 'sramirez@clinica.ec', 'recep123'),
        (3, 'Luis Torres', 'ltorres@clinica.ec', 'recep123'),
    ]

    for role_id, full_name, email, password in usuarios:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8')
        cursor.execute("""
            INSERT INTO users (role_id, full_name, email, password_hash, is_active)
            VALUES (%s, %s, %s, %s, true)
            ON CONFLICT (email) DO NOTHING
        """, (role_id, full_name, email, password_hash))

    conn.commit()
    print(f"OK {len(usuarios)} usuarios creados")

def poblar_pacientes(conn, cantidad=50):
    """Genera pacientes con cédulas ecuatorianas válidas"""
    print(f"Generando {cantidad} pacientes...")
    cursor = conn.cursor()

    tipos_sangre = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
    generos = ['M', 'F']
    ciudades = ['Quito', 'Guayaquil', 'Cuenca', 'Ambato', 'Loja', 'Manta', 'Riobamba']
    provincias = ['Pichincha', 'Guayas', 'Azuay', 'Tungurahua', 'Loja', 'Manabí', 'Chimborazo']

    for _ in range(cantidad):
        cedula = generar_cedula_valida()
        full_name = fake.name()
        fecha_nacimiento = fake.date_of_birth(minimum_age=1, maximum_age=90)
        telefono = f"09{random.randint(10000000, 99999999)}"
        email = fake.email()
        direccion = fake.address()
        tipo_sangre = random.choice(tipos_sangre)
        genero = random.choice(generos)
        ciudad = random.choice(ciudades)
        provincia = random.choice(provincias)

        # Contacto de emergencia
        emergency_name = fake.name()
        emergency_phone = f"09{random.randint(10000000, 99999999)}"
        emergency_rel = random.choice(['Madre', 'Padre', 'Hermano/a', 'Esposo/a', 'Hijo/a', 'Amigo/a'])

        cursor.execute("""
            INSERT INTO patients (
                identification, identification_type, full_name, date_of_birth,
                gender, blood_type, phone, email, address, city, province,
                emergency_contact_name, emergency_contact_phone, emergency_contact_relationship,
                is_active
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true)
            ON CONFLICT (identification) DO NOTHING
        """, (cedula, 'cedula', full_name, fecha_nacimiento, genero, tipo_sangre,
              telefono, email, direccion, ciudad, provincia,
              emergency_name, emergency_phone, emergency_rel))

    conn.commit()
    print(f"OK {cantidad} pacientes generados")

def poblar_productos(conn):
    """Crea productos médicos"""
    print("Poblando inventario...")
    cursor = conn.cursor()

    productos = [
        ('Paracetamol 500mg', 'PAR-500', 'Tableta', 'Analgésico antipirético', 0.50, 0.30, 1000, 100, 15, True),
        ('Ibuprofeno 400mg', 'IBU-400', 'Tableta', 'Antiinflamatorio', 0.75, 0.45, 800, 80, 15, True),
        ('Amoxicilina 500mg', 'AMO-500', 'Cápsula', 'Antibiótico', 1.20, 0.80, 500, 50, 15, True),
        ('Omeprazol 20mg', 'OME-20', 'Cápsula', 'Protector gástrico', 0.90, 0.60, 600, 60, 15, True),
        ('Loratadina 10mg', 'LOR-10', 'Tableta', 'Antihistamínico', 0.60, 0.40, 400, 40, 15, False),
        ('Alcohol antiséptico 70%', 'ALC-70', 'Líquido', 'Antiséptico', 3.50, 2.00, 200, 20, 15, False),
        ('Gasas estériles', 'GAS-EST', 'Insumo', 'Material de curación', 2.00, 1.20, 300, 30, 15, False),
        ('Guantes látex (par)', 'GLO-LAT', 'Insumo', 'EPP', 0.80, 0.50, 1000, 100, 15, False),
        ('Jeringuillas 5ml', 'JER-5ML', 'Insumo', 'Inyectable', 0.40, 0.25, 500, 50, 15, False),
        ('Termómetro digital', 'TER-DIG', 'Equipo', 'Medición temperatura', 15.00, 10.00, 50, 10, 15, False),
        ('Oxímetro de pulso', 'OXI-PUL', 'Equipo', 'Saturación de oxígeno', 35.00, 25.00, 30, 5, 15, False),
        ('Tensiómetro digital', 'TEN-DIG', 'Equipo', 'Medición presión arterial', 45.00, 30.00, 25, 5, 15, False),
        ('Vitamina C 500mg', 'VIT-C500', 'Tableta', 'Suplemento vitamínico', 8.50, 5.00, 200, 20, 15, False),
        ('Vitamina D 1000 UI', 'VIT-D1K', 'Cápsula', 'Suplemento vitamínico', 12.00, 8.00, 150, 15, 15, False),
        ('Suero fisiológico 500ml', 'SUE-FIS', 'Líquido', 'Solución intravenosa', 2.50, 1.50, 300, 30, 15, True),
        ('Dipirona 1g', 'DIP-1G', 'Tableta', 'Analgésico potente', 1.50, 1.00, 400, 40, 15, True),
        ('Metformina 850mg', 'MET-850', 'Tableta', 'Antidiabético', 1.80, 1.20, 300, 30, 15, True),
        ('Enalapril 10mg', 'ENA-10', 'Tableta', 'Antihipertensivo', 2.00, 1.30, 350, 35, 15, True),
        ('Atorvastatina 20mg', 'ATO-20', 'Tableta', 'Hipolipemiante', 2.50, 1.60, 250, 25, 15, True),
        ('Salbutamol inhalador', 'SAL-INH', 'Inhalador', 'Broncodilatador', 12.00, 8.00, 100, 10, 15, True),
    ]

    for nombre, sku, tipo, descripcion, precio_venta, precio_costo, stock_actual, stock_minimo, iva, requiere_receta in productos:
        cursor.execute("""
            INSERT INTO products (
                name, sku, type, description, unit_price, cost_price,
                current_stock, minimum_stock, iva_percentage, requires_prescription,
                is_active
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true)
            ON CONFLICT (sku) DO NOTHING
        """, (nombre, sku, tipo, descripcion, precio_venta, precio_costo,
              stock_actual, stock_minimo, iva, requiere_receta))

    conn.commit()
    print(f"OK {len(productos)} productos agregados")

def poblar_tratamientos(conn):
    """Crea tratamientos con recetas médicas"""
    print("Poblando tratamientos...")
    cursor = conn.cursor()

    tratamientos = [
        ('Tratamiento Gripe Común', 'Manejo sintomático de gripe', 15.00, 0, 30, [
            ('Paracetamol 500mg', 12, 'Tomar 1 cada 8 horas por 3 días'),
            ('Vitamina C 500mg', 10, 'Tomar 1 diaria por 10 días')
        ]),
        ('Tratamiento Infección Respiratoria', 'Antibiótico + sintomático', 35.00, 0, 45, [
            ('Amoxicilina 500mg', 21, 'Tomar 1 cada 8 horas por 7 días'),
            ('Ibuprofeno 400mg', 15, 'Tomar 1 cada 12 horas si hay dolor')
        ]),
        ('Control Diabetes', 'Manejo de diabetes tipo 2', 25.00, 0, 30, [
            ('Metformina 850mg', 60, 'Tomar 1 cada 12 horas con alimentos')
        ]),
        ('Control Hipertensión', 'Manejo de presión arterial alta', 30.00, 0, 30, [
            ('Enalapril 10mg', 30, 'Tomar 1 diaria en ayunas')
        ]),
        ('Tratamiento Gastritis', 'Protección gástrica', 20.00, 0, 30, [
            ('Omeprazol 20mg', 30, 'Tomar 1 en ayunas por 30 días')
        ]),
        ('Tratamiento Alergia', 'Control de síntomas alérgicos', 12.00, 0, 15, [
            ('Loratadina 10mg', 10, 'Tomar 1 diaria por 10 días')
        ]),
        ('Cura Simple', 'Curación de herida superficial', 8.00, 0, 20, [
            ('Alcohol antiséptico 70%', 1, 'Limpiar herida'),
            ('Gasas estériles', 5, 'Cubrir herida'),
            ('Guantes látex (par)', 2, 'Uso durante curación')
        ])
    ]

    for nombre, descripcion, precio, iva, duracion, receta in tratamientos:
        cursor.execute("""
            INSERT INTO treatments (name, description, base_price, iva_percentage, duration_minutes, is_active)
            VALUES (%s, %s, %s, %s, %s, true)
            RETURNING treatment_id
        """, (nombre, descripcion, precio, iva, duracion))

        treatment_id = cursor.fetchone()['treatment_id']

        # Obtener product_id de los productos en la receta
        for producto_nombre, cantidad, instrucciones in receta:
            cursor.execute("SELECT product_id FROM products WHERE name = %s", (producto_nombre,))
            result = cursor.fetchone()
            if result:
                product_id = result['product_id']
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

    # Obtener doctores (role_id = 2)
    cursor.execute("SELECT user_id FROM users WHERE role_id = 2")
    doctores = [row['user_id'] for row in cursor.fetchall()]

    if not doctores:
        print("ADVERTENCIA: No hay doctores en el sistema")
        return

    # Obtener pacientes
    cursor.execute("SELECT patient_id FROM patients LIMIT 50")
    pacientes = [row['patient_id'] for row in cursor.fetchall()]

    if not pacientes:
        print("ADVERTENCIA: No hay pacientes en el sistema")
        return

    # Obtener tratamientos
    cursor.execute("SELECT treatment_id FROM treatments")
    tratamientos = [row['treatment_id'] for row in cursor.fetchall()]

    estados = ['PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED']
    motivos = [
        'Consulta general',
        'Control médico',
        'Dolor de cabeza',
        'Dolor abdominal',
        'Fiebre',
        'Tos y gripe',
        'Revisión de resultados',
        'Control post-operatorio',
        'Vacunación'
    ]

    for _ in range(cantidad):
        patient_id = random.choice(pacientes)
        doctor_id = random.choice(doctores)
        treatment_id = random.choice(tratamientos) if tratamientos and random.random() > 0.3 else None

        # Generar fecha aleatoria (últimos 30 días + próximos 60 días)
        dias_offset = random.randint(-30, 60)
        fecha_base = datetime.now() + timedelta(days=dias_offset)

        # Hora de inicio (8 AM a 5 PM)
        hora_inicio = random.randint(8, 16)
        minuto_inicio = random.choice([0, 30])

        start_time = fecha_base.replace(hour=hora_inicio, minute=minuto_inicio, second=0, microsecond=0)
        duracion = random.choice([30, 45, 60])
        end_time = start_time + timedelta(minutes=duracion)

        # Estado basado en la fecha
        if start_time < datetime.now() - timedelta(days=1):
            status = random.choice(['COMPLETED', 'COMPLETED', 'COMPLETED', 'CANCELLED', 'NO_SHOW'])
        elif start_time < datetime.now():
            status = random.choice(['CONFIRMED', 'PENDING'])
        else:
            status = random.choice(['PENDING', 'CONFIRMED', 'CONFIRMED'])

        motivo = random.choice(motivos)
        notas = f"Paciente refiere {motivo.lower()}" if status == 'COMPLETED' else None

        cursor.execute("""
            INSERT INTO appointments (
                patient_id, doctor_id, treatment_id, start_time, end_time,
                status, reason, notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (patient_id, doctor_id, treatment_id, start_time, end_time,
              status, motivo, notas))

    conn.commit()
    print(f"OK {cantidad} citas generadas")

def poblar_facturas(conn, cantidad=50):
    """Genera facturas"""
    print(f"Generando {cantidad} facturas...")
    cursor = conn.cursor()

    # Obtener citas completadas
    cursor.execute("""
        SELECT a.appointment_id, a.patient_id, a.doctor_id, a.treatment_id, a.start_time
        FROM appointments a
        WHERE a.status = 'COMPLETED'
        ORDER BY a.start_time DESC
        LIMIT %s
    """, (cantidad,))

    citas = cursor.fetchall()

    if not citas:
        print("ADVERTENCIA: No hay citas completadas para facturar")
        return

    # Obtener productos
    cursor.execute("SELECT product_id, name, unit_price FROM products LIMIT 20")
    productos = cursor.fetchall()

    metodos_pago = ['Efectivo', 'Tarjeta', 'Transferencia', 'Cheque']

    for cita in citas[:cantidad]:
        # Obtener precio del tratamiento
        subtotal = 0
        if cita['treatment_id']:
            cursor.execute("SELECT base_price FROM treatments WHERE treatment_id = %s", (cita['treatment_id'],))
            treatment = cursor.fetchone()
            if treatment:
                subtotal = float(treatment['base_price'])

        # Agregar productos aleatorios
        num_productos = random.randint(1, 3)
        items_factura = []

        for _ in range(num_productos):
            producto = random.choice(productos)
            cantidad = random.randint(1, 3)
            precio = float(producto['unit_price'])
            subtotal_item = precio * cantidad
            subtotal += subtotal_item

            items_factura.append({
                'product_id': producto['product_id'],
                'description': producto['name'],
                'quantity': cantidad,
                'unit_price': precio,
                'discount_percentage': 0,
                'subtotal': subtotal_item
            })

        iva_porcentaje = 15.00
        iva = subtotal * (iva_porcentaje / 100)
        total = subtotal + iva

        payment_method = random.choice(metodos_pago)
        status = random.choices(['paid', 'pending', 'cancelled'], weights=[0.85, 0.10, 0.05])[0]

        # Usar la fecha de la cita como invoice_date
        invoice_date = cita['start_time']

        cursor.execute("""
            INSERT INTO invoices (
                patient_id, subtotal, iva_percentage, iva,
                total, payment_method, status, invoice_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING invoice_id
        """, (cita['patient_id'], subtotal, iva_porcentaje,
              iva, total, payment_method, status, invoice_date))

        invoice_id = cursor.fetchone()['invoice_id']

        # Insertar items de la factura
        for item in items_factura:
            cursor.execute("""
                INSERT INTO invoice_items (
                    invoice_id, product_id, description, quantity,
                    unit_price, discount_percentage, subtotal
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (invoice_id, item['product_id'], item['description'],
                  item['quantity'], item['unit_price'],
                  item['discount_percentage'], item['subtotal']))

    conn.commit()
    print(f"OK {cantidad} facturas generadas")

def poblar_gastos(conn):
    """Genera gastos operacionales"""
    print("Generando gastos operacionales...")
    cursor = conn.cursor()

    gastos = [
        ('Servicios básicos', 'Electricidad', 'Factura eléctrica', 150.00, 'CFE Ecuador', '1234567890001'),
        ('Servicios básicos', 'Agua', 'Factura agua potable', 45.00, 'EPMAPS', '1234567890002'),
        ('Servicios básicos', 'Internet', 'Plan empresarial 100MB', 80.00, 'CNT', '1234567890003'),
        ('Mantenimiento', 'Limpieza', 'Servicio de limpieza mensual', 200.00, 'CleanPro', '0987654321001'),
        ('Suministros', 'Oficina', 'Papel, tinta, útiles', 120.00, 'PaperWorld', '0987654321002'),
        ('Personal', 'Nómina', 'Pago asistentes administrativos', 1500.00, None, None),
        ('Otros', 'Seguros', 'Seguro responsabilidad civil', 350.00, 'Seguros Unidos', '1122334455001'),
        ('Mantenimiento', 'Equipos', 'Calibración equipos médicos', 280.00, 'MedTech', '5566778899001'),
    ]

    for categoria, subcategoria, descripcion, monto, proveedor, ruc in gastos:
        # Fecha aleatoria en los últimos 30 días
        fecha = datetime.now() - timedelta(days=random.randint(1, 30))

        cursor.execute("""
            INSERT INTO expenses (
                category, subcategory, description, amount,
                supplier_name, supplier_ruc, expense_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (categoria, subcategoria, descripcion, monto, proveedor, ruc, fecha.date()))

    conn.commit()
    print(f"OK {len(gastos)} gastos registrados")

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("SISTEMA DE POBLADO DE DATOS V2 - CLINICA MEDICA ECUADOR")
    print("="*60 + "\n")

    try:
        conn = conectar_db()
        print("Conectado a la base de datos\n")

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
        print("\nEstadisticas:")
        print("  6 usuarios")
        print("  50 pacientes con cedulas validas")
        print("  20 productos medicos")
        print("  7 tratamientos con recetas")
        print("  100 citas medicas")
        print("  50 facturas")
        print("  8 gastos operacionales")
        print("\n")

    except Exception as e:
        print(f"\nERROR: {str(e)}\n")
        raise

if __name__ == '__main__':
    main()
