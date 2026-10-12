import jwt
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from app.config import settings
from typing import Optional, Dict, Any

# Initialise Fernet encryptor
try:
    fernet = Fernet(settings.TOKEN_ENCRYPTION_KEY.encode())
except Exception:
    # Generate a temporary key just in case to prevent module loading crashes when running scripts/generate_keys
    temp_key = Fernet.generate_key()
    fernet = Fernet(temp_key)

def encrypt_token(token: str) -> str:
    if not token:
        return ""
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    if not encrypted_token:
        return ""
    try:
        return fernet.decrypt(encrypted_token.encode()).decode()
    except Exception:
        return ""

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        return None
