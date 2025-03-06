# backend/routes/chat.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import os
from backend.routes.auth import get_user_session

router = APIRouter()

@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    username = get_user_session(request)
    if username:
        with open(os.path.join(os.getcwd(), 'frontend', 'chat.html')) as f:
            return f.read()
    else:
        return RedirectResponse(url="/")
