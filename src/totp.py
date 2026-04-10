import pyotp
import time
import base64
import struct
import hashlib


def generate_totp_secret(length: int = 32) -> str:
    """Generate a random TOTP secret (base32)."""
    return pyotp.random_base32(length=length)


def get_totp_code(secret: str) -> tuple:
    """Get current TOTP code and remaining seconds.

    Returns: (code: str, remaining_seconds: int)
    """
    if not secret:
        return ("", 0)
    try:
        # Clean up secret (remove spaces, dashes)
        secret = secret.replace(" ", "").replace("-", "").upper()
        totp = pyotp.TOTP(secret)
        code = totp.now()
        remaining = totp.interval - int(time.time()) % totp.interval
        return (code, remaining)
    except Exception:
        return ("", 0)


def get_totp_uri(secret: str, account_name: str, issuer: str = "PasswordManager") -> str:
    """Generate otpauth:// URI for QR code or manual entry."""
    secret = secret.replace(" ", "").replace("-", "").upper()
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=account_name, issuer_name=issuer
    )


def verify_totp(secret: str, code: str) -> bool:
    """Verify a TOTP code against the secret."""
    if not secret or not code:
        return False
    try:
        secret = secret.replace(" ", "").replace("-", "").upper()
        totp = pyotp.TOTP(secret)
        return totp.verify(code)
    except Exception:
        return False
