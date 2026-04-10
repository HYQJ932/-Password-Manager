import pyotp
import time
import base64
import struct
import hashlib


def generate_totp_secret(length: int = 32) -> str:
    """Generate a random TOTP secret (base32)."""
    return pyotp.random_base32(length=length)


def generate_hotp_secret(length: int = 32) -> str:
    """Generate a random HOTP secret (base32)."""
    return pyotp.random_base32(length=length)


def get_totp_code(secret: str) -> tuple:
    """Get current TOTP code and remaining seconds.

    Returns: (code: str, remaining_seconds: int)
    """
    if not secret:
        return ("", 0)
    try:
        secret = secret.replace(" ", "").replace("-", "").upper()
        totp = pyotp.TOTP(secret)
        code = totp.now()
        remaining = totp.interval - int(time.time()) % totp.interval
        return (code, remaining)
    except Exception:
        return ("", 0)


def get_hotp_code(secret: str, counter: int) -> str:
    """Get HOTP code for a specific counter.

    Returns: (code: str, counter: int)
    """
    if not secret or counter < 0:
        return ("", counter)
    try:
        secret = secret.replace(" ", "").replace("-", "").upper()
        hotp = pyotp.HOTP(secret)
        code = hotp.at(counter)
        return (code, counter)
    except Exception:
        return ("", counter)


def get_totp_uri(secret: str, account_name: str, issuer: str = "PasswordManager") -> str:
    """Generate otpauth:// URI for TOTP."""
    secret = secret.replace(" ", "").replace("-", "").upper()
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=account_name, issuer_name=issuer
    )


def get_hotp_uri(secret: str, account_name: str, issuer: str = "PasswordManager",
                 counter: int = 0) -> str:
    """Generate otpauth:// URI for HOTP."""
    secret = secret.replace(" ", "").replace("-", "").upper()
    hotp = pyotp.HOTP(secret)
    return hotp.provisioning_uri(
        name=account_name, issuer_name=issuer, initial_count=counter
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


def verify_hotp(secret: str, code: str, counter: int, window: int = 5) -> int:
    """Verify an HOTP code and return the synced counter, or -1 if failed."""
    if not secret or not code:
        return -1
    try:
        secret = secret.replace(" ", "").replace("-", "").upper()
        hotp = pyotp.HOTP(secret)
        # Check counter ± window
        for offset in range(-window, window + 1):
            c = counter + offset
            if c < 0:
                continue
            if hotp.verify(code, c):
                return c
        return -1
    except Exception:
        return -1
