import bcrypt
import re
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError

from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

# =============================
# PASSWORD HASHING
# =============================
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


# =============================
# PASSWORD POLICY
# =============================
def validate_password(password: str) -> bool:
    """
    Rules:
    - Min length: 8
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character (!@#$%^&*)
    """
    return (
        len(password) >= 8
        and re.search(r"[A-Z]", password)  # Uppercase
        and re.search(r"[a-z]", password)  # Lowercase
        and re.search(r"\d", password)  # Digit
        and re.search(r"[!@#$%^&*]", password)  # Special char
    )


# =============================
# JWT TOKENS
# =============================
def create_access_token(subject: str) -> str:
    payload = {
        "sub": subject,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except Exception:
        return None


# =============================
# PASSWORD RESET TOKENS (1-hour TTL)
# =============================
def create_reset_token(email: str) -> str:
    """Generate a password reset token with 1-hour expiration."""
    payload = {
        "sub": email,
        "type": "reset",
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_reset_token(token: str) -> Optional[str]:
    """Verify reset token and return email if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "reset":
            return None
        return payload.get("sub")
    except Exception:
        return None
