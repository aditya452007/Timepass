# REFACTOR DELTA: 67 lines -> 25 lines (-42 lines, -62%)
"""
MODULE OVERVIEW:
SSE with Long Poll fallback.
"""
from fastapi import APIRouter, Request, Query, Response
from server.routes.sse import sse_endpoint
from server.routes.long_polling import long_poll

router = APIRouter()

@router.get("/hybrid/sse-lp/stream")
async def hybrid_stream(
    request: Request,
    response: Response,
    client_id: str | None = Query(None)
):
    """
    WHAT IS HAPPENING HERE:
    We detect capabilities via the Accept header. 
    If the client advertises `text/event-stream`, we return the infinite SSE stream.
    If not, we return a single Long Poll waiting query.
    """
    supports_sse = request.headers.get("Accept") == "text/event-stream"
    
    if supports_sse:
        return await sse_endpoint(request, client_id)
    else:
        return await long_poll(response, client_id)
