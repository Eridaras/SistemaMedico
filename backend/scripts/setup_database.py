"""
Script para inicializar la base de datos
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Configurar encoding UTF-8 para la consola
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Cargar variables de entorno
load_dotenv()

def init_database():
    """Inicializar base de datos con el script SQL"""
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("ERROR: DATABASE_URL no encontrada en .env")
        return False

    try:
        # Conectar a la base de datos
        print("Conectando a la base de datos...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Leer y ejecutar el script SQL
        print("Leyendo script SQL...")
        with open('init_database.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()

        print("Ejecutando script de inicializacion...")
        cursor.execute(sql_script)
        conn.commit()

        # Verificar que las tablas fueron creadas
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()

        print("\nBase de datos inicializada correctamente!")
        print(f"\nTablas creadas ({len(tables)}):")
        for table in tables:
            print(f"   - {table[0]}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"\nError al inicializar la base de datos: {e}")
        return False

if __name__ == '__main__':
    success = init_database()
    exit(0 if success else 1)
