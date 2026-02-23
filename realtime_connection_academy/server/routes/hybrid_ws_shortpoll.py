# REFACTOR DELTA: 33 lines -> 23 lines (-10 lines, -30%)
"""
MODULE OVERVIEW:
WebSocket for data, Short Poll for health checks.
"""
from fastapi import APIRouter, WebSocket, Query
from server.routes.websocket import websocket_endpoint
from server.connection_manager import manager

router = APIRouter()

@router.websocket("/hybrid/ws-health/ws")
async def hybrid_health_ws(websocket: WebSocket, client_id: str | None = Query(None)):
    await websocket_endpoint(websocket, client_id)

@router.get("/hybrid/ws-health/check")
async def health_check():
    """Simple REST health check used by the client's secondary loop."""
    stats = manager.get_stats()
    return {
        "status": "healthy",
        "active_connections": stats.active_ws,
        "is_alive": True
    }
