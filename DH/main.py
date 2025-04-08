from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

clients = []

@app.get("/")
async def get():
    return FileResponse("static/index.html", media_type='text/html')


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    try:
        while True:
            data = await websocket.receive_json()

            # Transmet à l'autre client
            for client in clients:
                if client != websocket:
                    await client.send_json(data)

    except Exception as e:
        print(f"[Serveur] Erreur ou déconnexion : {e}")
    finally:
        if websocket in clients:
            clients.remove(websocket)
