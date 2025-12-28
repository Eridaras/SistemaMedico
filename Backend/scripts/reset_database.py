"""
Script para limpiar completamente la base de datos
ADVERTENCIA: Esto eliminará TODOS los datos
"""
import psycopg2
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config import Config

load_dotenv()

DATABASE_URL = Config.DATABASE_URL or os.getenv('DATABASE_URL')

def reset_database():
    """Elimina todas las tablas y reinicia desde cero"""
    print("\n" + "="*60)
    print("RESET COMPLETO DE BASE DE DATOS")
    print("="*60 + "\n")

    print("ADVERTENCIA: Esto eliminara TODOS los datos")
    print("Esta operacion NO se puede deshacer\n")

    respuesta = input("Escriba 'SI ELIMINAR TODO' para continuar: ")

    if respuesta != "SI ELIMINAR TODO":
        print("\nOperacion cancelada")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()

        print("\nConectado a la base de datos")
        print("Eliminando todas las tablas...\n")

        # Eliminar todas las tablas con CASCADE para manejar foreign keys
        cursor.execute("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
        """)

        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            print(f"  Eliminando tabla: {table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")

        # Obtener todas las secuencias
        cursor.execute("""
            SELECT sequence_name FROM information_schema.sequences
            WHERE sequence_schema = 'public'
        """)

        sequences = cursor.fetchall()

        for seq in sequences:
            seq_name = seq[0]
            print(f"  Eliminando secuencia: {seq_name}")
            cursor.execute(f"DROP SEQUENCE IF EXISTS {seq_name} CASCADE")

        # Obtener todos los tipos personalizados
        cursor.execute("""
            SELECT typname FROM pg_type
            WHERE typtype = 'e' AND typnamespace = (
                SELECT oid FROM pg_namespace WHERE nspname = 'public'
            )
        """)

        types = cursor.fetchall()

        for typ in types:
            type_name = typ[0]
            print(f"  Eliminando tipo: {type_name}")
            cursor.execute(f"DROP TYPE IF EXISTS {type_name} CASCADE")

        # Eliminar vistas materializadas
        cursor.execute("""
            SELECT matviewname FROM pg_matviews
            WHERE schemaname = 'public'
        """)

        matviews = cursor.fetchall()

        for mv in matviews:
            mv_name = mv[0]
            print(f"  Eliminando vista materializada: {mv_name}")
            cursor.execute(f"DROP MATERIALIZED VIEW IF EXISTS {mv_name} CASCADE")

        print("\n" + "="*60)
        print("BASE DE DATOS LIMPIADA EXITOSAMENTE")
        print("="*60)
        print("\nProximos pasos:")
        print("  1. Ejecutar: python scripts/migrate_schema.py")
        print("  2. Ejecutar: python scripts/populate_realistic_data_v2.py")
        print("\n")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\nERROR: {str(e)}\n")
        raise

if __name__ == '__main__':
    reset_database()
