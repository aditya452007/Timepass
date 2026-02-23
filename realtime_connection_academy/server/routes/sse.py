# REFACTOR DELTA: 58 lines -> 34 lines (-24 lines, -41%)
"""
MODULE OVERVIEW:
...
"""
import asyncio
from fastapi import APIRouter, Query, Request
from sse_starlette.sse import EventSourceResponse

from server.connection_manager import manager
from shared.config import settings
from shared.models import Event
from shared.route_utils import extract_client_id, log_connection, run_event_loop

router = APIRouter()

async def queue_generator(queue: asyncio.Queue):
    while True:
        yield await queue.get()

@router.get("/sse/stream")
async def sse_endpoint(request: Request, client_id: str | None = Query(None)):
    cid = await extract_client_id(client_id)
    queue = manager.subscribe_sse(cid)
    await log_connection("sse:connect", cid)
    
    out_queue = asyncio.Queue()
    
    async def send_to_queue(event: Event) -> None:
        await out_queue.put({
            "event": event.event_type,
            "id": event.event_id,
            "data": event.model_dump_json() if event.event_type != "heartbeat" else '{"ping": "pong"}'
        })

    async def event_publisher():
        try:
            await run_event_loop(cid, "sse", send_to_queue, queue_generator(queue), settings.SSE_HEARTBEAT_INTERVAL_S, manager)
        finally:
            manager.unsubscribe_sse(cid)
            await log_connection("sse:disconnect", cid)

    asyncio.create_task(event_publisher())
    return EventSourceResponse(queue_generator(out_queue))
