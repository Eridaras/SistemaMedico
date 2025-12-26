"""
Script para generar par de claves RSA para JWT
Sistema Médico - Seguridad
"""
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import os

def generate_rsa_keypair():
    """Genera par de claves RSA (privada/pública)"""

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    keys_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'keys')
    os.makedirs(keys_dir, exist_ok=True)

    private_key_path = os.path.join(keys_dir, 'jwt_private.pem')
    public_key_path = os.path.join(keys_dir, 'jwt_public.pem')

    with open(private_key_path, 'wb') as f:
        f.write(private_pem)

    with open(public_key_path, 'wb') as f:
        f.write(public_pem)

    os.chmod(private_key_path, 0o600)
    os.chmod(public_key_path, 0o644)

    print("="*60)
    print("CLAVES RSA GENERADAS EXITOSAMENTE")
    print("="*60)
    print(f"\nClave privada: {private_key_path}")
    print(f"Clave publica:  {public_key_path}")
    print("\nIMPORTANTE:")
    print("  - Clave privada (600): Solo lectura/escritura para owner")
    print("  - Clave publica (644): Lectura para todos")
    print("  - NUNCA commitear la clave privada a Git")
    print("  - Rotar claves cada 90 dias")
    print("\n")

if __name__ == '__main__':
    generate_rsa_keypair()
