# REFACTOR DELTA: 59 lines -> 27 lines (-32 lines, -54%)
"""
MODULE OVERVIEW:
Hybrid WebSocket + SSE routing.
"""
from fastapi import APIRouter, Request, Query, WebSocket

router = APIRouter()

from server.routes.sse import sse_endpoint as base_sse_endpoint
from server.routes.websocket import websocket_endpoint as base_websocket_endpoint

@router.get("/hybrid/ws-sse/negotiate")
async def negotiate():
    return {
        "status": "ok",
        "primary": "websocket",
        "fallback": "sse",
        "ws_url": "/hybrid/ws-sse/ws",
        "sse_url": "/hybrid/ws-sse/stream"
    }

@router.websocket("/hybrid/ws-sse/ws")
async def hybrid_ws(websocket: WebSocket, client_id: str | None = Query(None)):
    await base_websocket_endpoint(websocket, client_id)

@router.get("/hybrid/ws-sse/stream")
async def hybrid_sse(request: Request, client_id: str | None = Query(None)):
    return await base_sse_endpoint(request, client_id)
