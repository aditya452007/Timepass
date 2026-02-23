# REFACTOR DELTA: 61 lines -> 47 lines (-14 lines, -23%)
"""
MODULE OVERVIEW:
...
"""
from fastapi import APIRouter, Query, Response
from datetime import datetime, timezone
import copy

from server.connection_manager import manager
from shared.models import PollResponse
from shared.config import settings
from shared.route_utils import extract_client_id, log_connection

router = APIRouter()

@router.get("/poll/short", response_model=PollResponse)
async def short_poll(
    response: Response,
    client_id: str | None = Query(None),
    last_seen_id: str | None = Query(None)
):
    cid = await extract_client_id(client_id)
    await log_connection("short_poll:connect", cid)
    
    events_snapshot = list(manager.recent_events_buffer)
    new_events = []
    
    if not last_seen_id:
        new_events = events_snapshot[-10:] if len(events_snapshot) > 10 else events_snapshot
    else:
        found_idx = -1
        for i, event in enumerate(events_snapshot):
            if event.event_id == last_seen_id:
                found_idx = i
                break
        
        if found_idx != -1 and found_idx < len(events_snapshot) - 1:
            new_events = events_snapshot[found_idx + 1:]
    
    events_to_return = []
    for event in new_events:
        e = copy.deepcopy(event)
        e.protocol = "short_poll"
        events_to_return.append(e)
    
    response.headers["X-Poll-Interval"] = str(settings.SHORT_POLL_INTERVAL_MS)
    
    return PollResponse(
        events=events_to_return,
        status="ok" if new_events else "empty",
        next_poll_ms=settings.SHORT_POLL_INTERVAL_MS,
        server_time=datetime.now(timezone.utc)
    )
