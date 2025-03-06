# backend/routes/auth.py
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from itsdangerous import URLSafeTimedSerializer, BadSignature
import os
from backend.core.config import SECRET_KEY, SESSION_MAX_AGE

# Serializer pour la gestion des sessions
serializer = URLSafeTimedSerializer(SECRET_KEY)

# Simuler une base de données utilisateur
USERS_DB = {"user": "user", "root": "root"}

router = APIRouter()

def get_user_session(request: Request):
    session_token = request.cookies.get("session_token")
    if session_token:
        try:
            username = serializer.loads(session_token, max_age=SESSION_MAX_AGE)
            return username
        except BadSignature:
            return None
    return None

@router.get("/", response_class=HTMLResponse)
async def login_page():
    with open(os.path.join(os.getcwd(), 'frontend', 'login.html')) as f:
        return f.read()

@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username in USERS_DB and USERS_DB[username] == password:
        session_token = serializer.dumps(username)
        response = RedirectResponse(url="/chat", status_code=303)
        response.set_cookie(key="session_token", value=session_token, httponly=True, secure=True)
        return response
    else:
        return RedirectResponse(url="/", status_code=303)
