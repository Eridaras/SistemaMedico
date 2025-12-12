
import psycopg2
import os
import sys

url = "postgresql://neondb_owner:npg_jRyizbnEYQ18@ep-wandering-tooth-a4bc9k9a-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

print(f"Intentando conectar a: {url.split('@')[1]}")

try:
    # Timeout de 5 segundos
    conn = psycopg2.connect(url, connect_timeout=5)
    print("¡CONEXIÓN EXITOSA!")
    conn.close()
    sys.exit(0)
except psycopg2.OperationalError as e:
    print(f"FALLO DE CONEXIÓN: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
