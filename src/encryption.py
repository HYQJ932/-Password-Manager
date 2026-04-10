import os
import sys
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESSIV
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

def _data_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

SALT_FILE = os.path.join(_data_dir(), "data.salt")
DATA_FILE = os.path.join(_data_dir(), "data.enc")
MASTER_KEY_LENGTH = 32
PBKDF2_ITERATIONS = 480000


def derive_key(password: str, salt: bytes = None) -> tuple:
    """Derive encryption key from master password using PBKDF2."""
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=MASTER_KEY_LENGTH,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt


def save_salt(salt: bytes, filepath: str = SALT_FILE):
    """Save salt to file."""
    with open(filepath, "wb") as f:
        f.write(salt)


def load_salt(filepath: str = SALT_FILE) -> bytes:
    """Load salt from file."""
    with open(filepath, "rb") as f:
        return f.read()


def create_fernet_key(password: str) -> tuple:
    """Create a Fernet key from password. Returns (key_bytes, salt)."""
    key, salt = derive_key(password)
    return key, salt


def encrypt_data(data: str, password: str, salt: bytes) -> bytes:
    """Encrypt data string using Fernet with derived key."""
    key, _ = derive_key(password, salt)
    fernet = Fernet(key)
    return fernet.encrypt(data.encode())


def decrypt_data(encrypted_data: bytes, password: str, salt: bytes) -> str:
    """Decrypt data string using Fernet with derived key."""
    key, _ = derive_key(password, salt)
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data).decode()


def verify_password(password: str, salt: bytes, encrypted_data: bytes) -> bool:
    """Verify if password can decrypt the data."""
    try:
        decrypt_data(encrypted_data, password, salt)
        return True
    except Exception:
        return False
