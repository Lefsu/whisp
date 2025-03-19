import hashlib
from fastapi import Request

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user(request: Request):
    return request.cookies.get("session_user")
