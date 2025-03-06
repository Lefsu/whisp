from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
from fastapi.responses import HTMLResponse

app = FastAPI()

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

@app.get("/", response_class=HTMLResponse)
def get_chat_page():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Chat WebSocket</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    padding: 20px;
                    background-color: #f7f7f7;
                }
                #chat {
                    width: 100%;
                    height: 300px;
                    border: 1px solid #ccc;
                    padding: 10px;
                    background-color: #fff;
                    overflow-y: scroll;
                    margin-bottom: 10px;
                }
                input[type="text"] {
                    width: 80%;
                    padding: 10px;
                }
                button {
                    padding: 10px;
                }
            </style>
        </head>
        <body>
            <h2>Chat WebSocket</h2>
            <div id="chat"></div>
            <input id="messageInput" type="text" placeholder="Écrire un message..." />
            <button onclick="sendMessage()">Envoyer</button>
            <script>
                let socket = new WebSocket("ws://localhost:50000/ws");
                let chatDiv = document.getElementById("chat");
                let messageInput = document.getElementById("messageInput");

                socket.onmessage = function(event) {
                    let message = event.data;
                    let messageDiv = document.createElement("div");
                    messageDiv.textContent = message;
                    chatDiv.appendChild(messageDiv);
                    chatDiv.scrollTop = chatDiv.scrollHeight; // Scroll down to the latest message
                };

                function sendMessage() {
                    let message = messageInput.value;
                    if (message.trim() !== "") {
                        socket.send(message);
                        messageInput.value = "";
                    }
                }

                messageInput.addEventListener("keypress", function(event) {
                    if (event.key === "Enter") {
                        sendMessage();
                    }
                });
            </script>
        </body>
    </html>
    """
