# backend/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from backend.routes.auth import router as auth_router
from backend.routes.chat import router as chat_router
from backend.core.websocket_manager import manager

app = FastAPI()

# Servir les fichiers statiques
app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

# Ajouter les routes
app.include_router(auth_router)
app.include_router(chat_router)

# WebSocket pour le chat
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
