from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import APIRouter, WebSocketDisconnect

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get():
    return FileResponse("static/index.html", media_type='text/html')


router = APIRouter()
active_chats = {}

def get_chat_id(user1: str, user2: str) -> str:
    return "_".join(sorted([user1, user2]))

@router.websocket("/ws/exchange/{receiver}")
async def websocket_endpoint(websocket: WebSocket, receiver: str):
    await websocket.accept()

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
            data = await websocket.receive_json()
            for ws in active_chats[chat_id]:
                if ws != websocket:
                    await ws.send_json(data)
    except WebSocketDisconnect:
        print(f"{sender} disconnected from chat with {receiver}")
    finally:
        active_chats[chat_id].remove(websocket)
        if not active_chats[chat_id]:
            del active_chats[chat_id]
