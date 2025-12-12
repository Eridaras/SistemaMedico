
import psycopg2
import os
import sys

# URL modificada sin channel_binding
url = "postgresql://neondb_owner:npg_jRyizbnEYQ18@ep-wandering-tooth-a4bc9k9a-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

print(f"Intentando conectar a (SIN channel_binding): {url.split('@')[1]}")

try:
    conn = psycopg2.connect(url, connect_timeout=10)
    print("¡CONEXIÓN EXITOSA!")
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
