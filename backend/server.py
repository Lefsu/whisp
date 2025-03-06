from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
from itsdangerous import URLSafeTimedSerializer, BadSignature
from fastapi import WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()

# Configuration pour le cookie de session
SECRET_KEY = "supersecretkey"  # Change-le pour un secret plus sûr
serializer = URLSafeTimedSerializer(SECRET_KEY)

# Servir les fichiers statiques dans le dossier ../frontend, à l'exception de chat.html
app.mount("/frontend", StaticFiles(directory=os.path.join(os.getcwd(), "frontend"), html=True), name="frontend")

# Exemple d'utilisateur
USERS_DB = {"user": "user", "root": "root"}

# Fonction pour vérifier si l'utilisateur est authentifié
def get_user_session(request: Request):
    session_token = request.cookies.get("session_token")
    if session_token:
        try:
            username = serializer.loads(session_token, max_age=60)  # valable 1 min
            return username
        except BadSignature:
            return None
    return None

@app.get("/", response_class=HTMLResponse)
async def login_page():
    with open(os.path.join(os.getcwd(), 'frontend', 'login.html')) as f:
        return f.read()

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username in USERS_DB and USERS_DB[username] == password:
        # Générer un token de session
        session_token = serializer.dumps(username)
        response = RedirectResponse(url="/chat", status_code=303)
        response.set_cookie(key="session_token", value=session_token, httponly=True)
        return response
    else:
        return RedirectResponse(url="/login", status_code=303)  # Correction ici

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    # Vérifier la session avant de donner accès à la page de chat
    username = get_user_session(request)
    if username:
        # Charger et afficher la page de chat uniquement si l'utilisateur est authentifié
        with open(os.path.join(os.getcwd(), 'frontend', 'chat.html')) as f:
            return f.read()
    else:
        # Si l'utilisateur n'est pas authentifié, rediriger vers la page de connexion
        return RedirectResponse(url="/")







### WebSocket pour le chat
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
