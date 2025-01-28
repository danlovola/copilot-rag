import logging
import time

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from llm import get_llm_response  #

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def get():
    with open("chat.html", "r") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data.lower() == "close":
                manager.disconnect(websocket)
                break

            for token in get_llm_response(data):
                await manager.send_personal_message(token, websocket)
                await websocket.send_text("")

            await manager.send_personal_message(".", websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    finally:
        logging.info(f"Client #{client_id} disconnected")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
