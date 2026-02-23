# REFACTOR DELTA: 60 lines -> 40 lines (-20 lines, -33%)
"""
MODULE OVERVIEW:
...
"""
import asyncio
from fastapi import APIRouter, Query, Response
from datetime import datetime, timezone
import copy

from server.connection_manager import manager
from shared.models import PollResponse
from shared.config import settings
from shared.route_utils import extract_client_id, log_connection

router = APIRouter()

@router.get("/poll/long", response_model=PollResponse)
async def long_poll(
    response: Response,
    client_id: str | None = Query(None, description="Unique client identifier"),
    timeout_s: float = Query(settings.LONG_POLL_TIMEOUT_S, description="Wait duration before timing out")
):
    cid = await extract_client_id(client_id)
    await log_connection("long_poll:connect", cid)
    wait_event = manager.register_long_poll(cid)
    
    try:
        await asyncio.wait_for(wait_event.wait(), timeout=timeout_s)
        
        if manager.recent_events_buffer:
            latest_event = manager.recent_events_buffer[-1]
            e = copy.deepcopy(latest_event)
            e.protocol = "long_poll"
        else:
            e = None
        
        return PollResponse(
            events=[e] if e else [],
            status="ok", next_poll_ms=50, server_time=datetime.now(timezone.utc)
        )
    except asyncio.TimeoutError:
        return PollResponse(events=[], status="timeout", next_poll_ms=500, server_time=datetime.now(timezone.utc))
    finally:
        manager.unregister_long_poll(cid)
        await log_connection("long_poll:disconnect", cid)
