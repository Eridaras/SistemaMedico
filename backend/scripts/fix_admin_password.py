"""
Script para actualizar la contraseña del admin
"""
import os
import sys
import psycopg2
import bcrypt
from dotenv import load_dotenv

# Configurar encoding UTF-8 para la consola
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Cargar variables de entorno
load_dotenv()

def fix_admin_password():
    """Actualizar la contraseña del admin"""
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("ERROR: DATABASE_URL no encontrada en .env")
        return False

    try:
        # Conectar a la base de datos
        print("Conectando a la base de datos...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Generar hash de la contraseña
        password = "admin123"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Actualizar la contraseña del admin
        cursor.execute("""
            UPDATE users
            SET password_hash = %s
            WHERE email = 'admin@clinica.com'
            RETURNING user_id, email, full_name
        """, (password_hash,))

        user = cursor.fetchone()
        conn.commit()

        if user:
            print(f"\nContrasena del admin actualizada correctamente!")
            print(f"User ID: {user[0]}")
            print(f"Email: {user[1]}")
            print(f"Nombre: {user[2]}")
            print(f"\nCredenciales de acceso:")
            print(f"  Email: admin@clinica.com")
            print(f"  Password: admin123")
        else:
            print("Usuario admin no encontrado")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"\nError al actualizar la contrasena: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_admin_password()
    exit(0 if success else 1)
