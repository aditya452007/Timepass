# REFACTOR DELTA: 57 lines -> 38 lines (-19 lines, -33%)
"""
MODULE OVERVIEW:
The WebSocket route implementation.

WHAT IS HAPPENING HERE:
Upgrades the HTTP request to a stateful WebSocket TCP connection.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from loguru import logger
import asyncio

from server.connection_manager import manager
from shared.config import settings
from shared.models import Event
from shared.route_utils import extract_client_id, log_connection, run_event_loop

router = APIRouter()

async def empty_generator():
    """Dummy generator since ConnectionManager broadcasts WS directly."""
    while True:
        await asyncio.sleep(86400)
        yield None

@router.websocket("/ws/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str | None = Query(None)
):
    cid = await extract_client_id(client_id)
    await manager.connect_ws(cid, websocket)
    await log_connection("websocket:connect", cid)
    
    async def send_to_ws(event: Event) -> None:
        await websocket.send_text(event.model_dump_json())

    loop_task = asyncio.create_task(
        run_event_loop(cid, "websocket", send_to_ws, empty_generator(), settings.WS_HEARTBEAT_INTERVAL_S, manager)
    )

    try:
        while True:
            text_data = await websocket.receive_text()
            logger.debug(f"WS client {cid} sent: {text_data}")
    except WebSocketDisconnect:
        pass
    finally:
        loop_task.cancel()
        manager.disconnect_ws(cid)
        await log_connection("websocket:disconnect", cid)
