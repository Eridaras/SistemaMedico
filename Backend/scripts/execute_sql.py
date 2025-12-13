"""
Script para ejecutar archivos SQL
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Configurar encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

def execute_sql_file(file_path):
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL no configurada")
        return False

    try:
        print(f"Ejecutando {file_path}...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            sql = f.read()
            
        cursor.execute(sql)
        conn.commit()
        
        print("✅ SQL ejecutado correctamente")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error ejecutando SQL: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python execute_sql.py <archivo.sql>")
        sys.exit(1)
        
    success = execute_sql_file(sys.argv[1])
    sys.exit(0 if success else 1)
