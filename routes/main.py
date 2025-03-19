from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import inspect, insert
from .database import get_db, engine
from .models import get_contacts_table, create_contacts_table, User, insert_contact
from .security import get_current_user
from fastapi import HTTPException
from sqlalchemy import MetaData

metadata = MetaData()

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/main", response_class=HTMLResponse)
async def read_main_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    contacts_table = get_contacts_table(user, metadata)
    inspector = inspect(engine)
    if not inspector.has_table(f"contacts_{user}"):
        create_contacts_table(user)

    query = db.execute(contacts_table.select())
    contacts = query.fetchall()

    return templates.TemplateResponse("main.html", {
        "request": request,
        "user": user,
        "contacts": contacts
    })
@router.get("/search/{query}")
async def search_user(query: str, request: Request, db: Session = Depends(get_db)):
    username = request.cookies.get("session_user")
    if not username:
        raise HTTPException(status_code=401, detail="User not authenticated")
    # Vérifier si l'utilisateur recherché existe dans la base de données
    user = db.query(User).filter(User.identifiant == query).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if username == query:
        raise HTTPException(status_code=404, detail="Impossible de s'ajouter soi-même en ami")
    insert_contact(query, username)
    insert_contact(username, query)
    return {"status": "success", "found": True, "query": query}
