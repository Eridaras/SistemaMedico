"""
Script de migración para aplicar esquema optimizado
Sistema Médico - Alta Escalabilidad
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config import Config

load_dotenv()

DATABASE_URL = Config.DATABASE_URL or os.getenv('DATABASE_URL')

def run_migration():
    """Ejecuta la migración del esquema"""
    print("\n" + "="*60)
    print("MIGRACION DE ESQUEMA - ALTA ESCALABILIDAD")
    print("="*60 + "\n")

    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        cursor = conn.cursor()

        print("Conectado a la base de datos\n")

        # Leer el archivo SQL
        schema_file = os.path.join(os.path.dirname(__file__), 'schema_optimized.sql')

        if not os.path.exists(schema_file):
            raise FileNotFoundError(f"No se encuentra el archivo: {schema_file}")

        print(f"Leyendo esquema desde: {schema_file}\n")

        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Ejecutar el esquema
        print("Ejecutando migracion del esquema...")
        print("ADVERTENCIA: Esto puede tomar varios minutos...\n")

        cursor.execute(schema_sql)
        conn.commit()

        print("\n" + "="*60)
        print("MIGRACION COMPLETADA EXITOSAMENTE")
        print("="*60)
        print("\nCaracteristicas del nuevo esquema:")
        print("  - Particionamiento por fecha (appointments, invoices, logs)")
        print("  - Indices optimizados para millones de registros")
        print("  - Busqueda fuzzy en pacientes y productos (pg_trgm)")
        print("  - Triggers para updated_at automatico")
        print("  - Vistas materializadas para reportes rapidos")
        print("  - Constraints de integridad referencial")
        print("  - Audit logs con JSONB")
        print("\nProximos pasos:")
        print("  1. Ejecutar: python scripts/populate_realistic_data_v2.py")
        print("  2. Verificar datos: SELECT COUNT(*) FROM patients;")
        print("  3. Probar la aplicacion")
        print("\n")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\nERROR: {str(e)}\n")
        if conn:
            conn.rollback()
            conn.close()
        raise

if __name__ == '__main__':
    run_migration()
