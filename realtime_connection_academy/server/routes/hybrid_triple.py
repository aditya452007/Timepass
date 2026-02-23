# REFACTOR DELTA: 81 lines -> 32 lines (-49 lines, -60%)
"""
MODULE OVERVIEW:
The Triple Threat: WS -> SSE -> Long Poll cascade.
"""
from fastapi import APIRouter, Request, Response, WebSocket, Query
from server.routes.websocket import websocket_endpoint
from server.routes.sse import sse_endpoint
from server.routes.long_polling import long_poll
from shared.models import NegotiationResponse

router = APIRouter()

@router.get("/hybrid/triple/negotiate", response_model=NegotiationResponse)
async def triple_negotiate():
    return NegotiationResponse(
        status="ok",
        primary="websocket",
        ws_url="/hybrid/triple/ws",
        sse_url="/hybrid/triple/stream",
        long_poll_url="/hybrid/triple/poll",
        interval_ms=5000,
        server_time="now"
    )

@router.websocket("/hybrid/triple/ws")
async def triple_ws(websocket: WebSocket, client_id: str | None = Query(None)):
    await websocket_endpoint(websocket, client_id)

@router.get("/hybrid/triple/stream")
async def triple_sse(request: Request, client_id: str | None = Query(None)):
    return await sse_endpoint(request, client_id)

@router.get("/hybrid/triple/poll")
async def triple_poll(response: Response, client_id: str | None = Query(None)):
    return await long_poll(response, client_id)
