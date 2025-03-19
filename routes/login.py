from fastapi import APIRouter, Form, Depends, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .security import hash_password

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def read_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.identifiant == username).first()
    if user and user.password == hash_password(password):
        response = RedirectResponse(url="/main", status_code=303)
        response.set_cookie(key="session_user", value=username, httponly=True)
        return response
    return RedirectResponse(url="/", status_code=303)

@router.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_user")
    return response
