from fastapi import FastAPI, Form, HTTPException, Depends, Request
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

# Créer la base de données et la session SQLAlchemy
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

@app.get("/", response_class=HTMLResponse)
async def read_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Vérifier si l'utilisateur existe et si le mot de passe est correct
    user = db.query(User).filter(User.identifiant == username).first()
    if user and user.password == hash_password(password):
        # Rediriger vers main.html si la connexion est réussie
        return RedirectResponse(url="/main", status_code=303)
    
    # Rediriger vers la page de connexion en cas d'échec
    return RedirectResponse(url="/", status_code=303)

@app.get("/main", response_class=HTMLResponse)
async def read_main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def read_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Vérifier si l'utilisateur existe déjà
    user = db.query(User).filter(User.identifiant == username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Ajouter le nouvel utilisateur
    new_user = User(identifiant=username, password=hash_password(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Rediriger vers la page de connexion après l'inscription
    return RedirectResponse(url="/", status_code=303)

# Lancer le serveur avec uvicorn
# Pour lancer le serveur, utilisez la commande suivante :
# uvicorn backend:app --reload



