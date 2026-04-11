import os
import sys
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def _data_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

SALT_FILE = os.path.join(_data_dir(), "data.salt")
DATA_FILE = os.path.join(_data_dir(), "data.enc")
MASTER_KEY_LENGTH = 32
PBKDF2_ITERATIONS = 480000

# New format marker prefix
FORMAT_PREFIX = b"PM2:"


def derive_key(password: str, salt: bytes = None) -> tuple:
    """Derive 32-byte AES-256 key from master password using PBKDF2."""
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=MASTER_KEY_LENGTH,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password), salt


def save_salt(salt: bytes, filepath: str = SALT_FILE):
    """Save salt to file."""
    with open(filepath, "wb") as f:
        f.write(salt)


def load_salt(filepath: str = SALT_FILE) -> bytes:
    """Load salt from file."""
    with open(filepath, "rb") as f:
        return f.read()


def _encrypt_aes256(data: bytes, key: bytes) -> bytes:
    """Encrypt data using AES-256-GCM."""
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit nonce for GCM
    ct = aesgcm.encrypt(nonce, data, None)
    return nonce + ct  # Prepend nonce for decryption


def _decrypt_aes256(ciphertext: bytes, key: bytes) -> bytes:
    """Decrypt data using AES-256-GCM."""
    aesgcm = AESGCM(key)
    nonce = ciphertext[:12]
    ct = ciphertext[12:]
    return aesgcm.decrypt(nonce, ct, None)


def encrypt_data(data: str, password: str, salt: bytes) -> bytes:
    """Encrypt data using AES-256-GCM with derived key."""
    key, _ = derive_key(password, salt)
    ct = _encrypt_aes256(data.encode(), key)
    return FORMAT_PREFIX + ct


def decrypt_data(encrypted_data: bytes, password: str, salt: bytes) -> str:
    """Decrypt data, auto-detecting old (Fernet) or new (AES-256-GCM) format."""
    key, _ = derive_key(password, salt)

    if encrypted_data.startswith(FORMAT_PREFIX):
        ct = encrypted_data[len(FORMAT_PREFIX):]
        return _decrypt_aes256(ct, key).decode()
    else:
        # Fallback to legacy Fernet format for backward compatibility
        from cryptography.fernet import Fernet
        fernet_key = base64.urlsafe_b64encode(key)
        return Fernet(fernet_key).decrypt(encrypted_data).decode()


def verify_password(password: str, salt: bytes, encrypted_data: bytes) -> bool:
    """Verify if password can decrypt the data."""
    try:
        decrypt_data(encrypted_data, password, salt)
        return True
    except Exception:
        return False
