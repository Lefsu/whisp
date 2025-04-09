from fastapi import APIRouter, Depends, Request, HTTPException, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import inspect, MetaData
from typing import Dict, List
from .database import get_db, engine
from .models import get_contacts_table, create_contacts_table, User, insert_contact, delete_contact, update_pubkey
from .security import get_current_user

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

@router.delete("/remove/{query}")
async def remove_user(query: str, request: Request, db: Session = Depends(get_db)):
    username = request.cookies.get("session_user")
    if not username:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    # Vérifier si l'utilisateur à supprimer existe dans la base de données
    user = db.query(User).filter(User.identifiant == query).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    if username == query:
        raise HTTPException(status_code=400, detail="Impossible de se supprimer soi-même de sa liste d'amis")
    
    delete_contact(query, username)
    delete_contact(username, query)
    
    return {"status": "success", "removed": True, "query": query}


@router.get("/get_pubkey/{user_to_get}")
async def get_pubkey(user_to_get: str, db: Session = Depends(get_db)):
    # Vérifier si l'utilisateur recherché existe dans la base de données
    user = db.query(User).filter(User.identifiant == user_to_get).first()
    
    # Si l'utilisateur n'existe pas, lever une erreur HTTP 404
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Récupérer la clé publique de l'utilisateur
    pubkey = user.pubkey
    
    # Si la clé publique n'existe pas (si elle est None), lever une erreur HTTP 404
    if not pubkey:
        raise HTTPException(status_code=404, detail="Clé publique non trouvée")
    
    return {"pubkey": pubkey}


# Dictionnaire pour stocker les connexions WebSocket actives
active_chats = {}

def get_chat_id(user1: str, user2: str) -> str:
    """Génère un ID de chat unique basé sur deux utilisateurs"""
    return "_".join(sorted([user1, user2]))

@router.websocket("/ws/{receiver}")
async def websocket_endpoint(websocket: WebSocket, receiver: str):
    await websocket.accept()

    # Récupérer le cookie de session depuis les en-têtes
    cookie_header = websocket.headers.get("cookie")
    sender = None
    if cookie_header:
        cookies = {k: v for k, v in (cookie.split("=") for cookie in cookie_header.split("; "))}
        sender = cookies.get("session_user")

    if not sender:
        await websocket.close()
        return
    
    chat_id = get_chat_id(sender, receiver)
    
    if chat_id not in active_chats:
        active_chats[chat_id] = []
    active_chats[chat_id].append(websocket)
    
    try:
        while True:
            message = await websocket.receive_text()
            for ws in active_chats[chat_id]:
                if ws != websocket:
                    await ws.send_text(f"{sender}: {message}")
    except WebSocketDisconnect:
        active_chats[chat_id].remove(websocket)
        if not active_chats[chat_id]:
            del active_chats[chat_id]
