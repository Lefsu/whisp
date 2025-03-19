from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import get_db
from .models import User, create_contacts_table
from .security import hash_password

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/register", response_class=HTMLResponse)
async def read_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.identifiant == username).first()
    if not user:
        new_user = User(identifiant=username, password=hash_password(password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        create_contacts_table(username)
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url="/register", status_code=303)
