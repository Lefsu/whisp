from fastapi import FastAPI, Form, HTTPException, Depends, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import hashlib

# Créer l'application FastAPI
app = FastAPI()

# Initialisation du moteur de templates (pour servir le HTML)
templates = Jinja2Templates(directory="templates")

# Configuration de la base de données
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modèle pour la table 'users'
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    identifiant = Column(String, unique=True, index=True)
    password = Column(String)

# Créer la base de données
Base.metadata.create_all(bind=engine)

# Fonction pour hasher les mots de passe
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Fonction pour obtenir la session de la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Middleware pour récupérer l'utilisateur à partir des cookies
def get_current_user(request: Request):
    username = request.cookies.get("session_user")
    return username

# Route d'affichage du login
@app.get("/", response_class=HTMLResponse)
async def read_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Route de connexion
@app.post("/login")
async def login(
    response: Response, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.identifiant == username).first()
    if user and user.password == hash_password(password):
        # Créer un cookie de session
        response = RedirectResponse(url="/main", status_code=303)
        response.set_cookie(key="session_user", value=username, httponly=True)
        return response
    
    return RedirectResponse(url="/", status_code=303)

# Page principale nécessitant une connexion
@app.get("/main", response_class=HTMLResponse)
async def read_main_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)
    
    print(f"Utilisateur connecté : {user}")  # Affichage dans la console

    return templates.TemplateResponse("main.html", {"request": request, "user": user})

# Route pour se déconnecter
@app.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_user")
    return response

# Route d'affichage du formulaire d'inscription
@app.get("/register", response_class=HTMLResponse)
async def read_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Route d'inscription
@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.identifiant == username).first()
    if not user:
        new_user = User(identifiant=username, password=hash_password(password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url="/register", status_code=303)
