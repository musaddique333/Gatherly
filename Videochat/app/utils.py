from cryptography.fernet import Fernet
from app.core.config import settings

# Retrieve the key securely from an environment variable or secrets manager
SECRET_KEY = settings.ENCRYPTION_KEY
fernet = Fernet(SECRET_KEY)

def encrypt_message(message: str) -> str:
    """Encrypt a message using Fernet symmetric encryption."""
    return fernet.encrypt(message.encode()).decode()

def decrypt_message(encrypted_message: str) -> str:
    """Decrypt a message using Fernet symmetric encryption."""
    return fernet.decrypt(encrypted_message.encode()).decode()
