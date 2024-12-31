from cryptography.fernet import Fernet
from app.core.config import settings

# Retrieve the key securely from an environment variable or secrets manager
SECRET_KEY = settings.ENCRYPTION_KEY
fernet = Fernet(SECRET_KEY)

def encrypt_message(message: str) -> str:
    """
    Encrypt a message using Fernet symmetric encryption.

    Args:
        message (str): The message to encrypt.

    Returns:
        str: The encrypted message, encoded as a string.

    Raises:
        ValueError: If the message cannot be encoded or encrypted.
    """
    try:
        # Encrypt the message and return the encoded string
        return fernet.encrypt(message.encode()).decode()
    except Exception as e:
        # Handle any exceptions that may arise during encryption
        raise ValueError(f"Error encrypting the message: {e}")

def decrypt_message(encrypted_message: str) -> str:
    """
    Decrypt a message using Fernet symmetric encryption.

    Args:
        encrypted_message (str): The encrypted message to decrypt.

    Returns:
        str: The decrypted message.

    Raises:
        ValueError: If the decryption fails (e.g., incorrect key or tampered data).
    """
    try:
        # Decrypt the message and return the decoded string
        return fernet.decrypt(encrypted_message.encode()).decode()
    except Exception as e:
        # Handle any exceptions that may arise during decryption
        raise ValueError(f"Error decrypting the message: {e}")
