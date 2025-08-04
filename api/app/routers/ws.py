import asyncio, json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..services.cache import snapshot

router = APIRouter()

@router.websocket("/ws")
async def greefs_ws(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            await ws.send_text(json.dumps(snapshot()))
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        # client closed the socket – just exit the loop silently
        return