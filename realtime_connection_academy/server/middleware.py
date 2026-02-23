"""
MODULE OVERVIEW:
FastAPI middleware to track request timings and inject CORS.
Where it fits: Middleware runs on *every* HTTP request, wrapping our endpoints.

WHAT IS HAPPENING HERE:
We add an `X-Process-Time-Ms` header so clients can observe the server-side
overhead of each polling request versus long-held connections.
This teaches students how to measure backend latency vs network latency.
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        # Pass the request to the route handler
        response = await call_next(request)
        
        process_time_ms = (time.perf_counter() - start_time) * 1000
        
        # WHAT IS HAPPENING HERE:
        # We inject a custom header so the visualizer client can see the exact
        # time spent inside FastAPI logic. If you see high times here, the server is slow.
        response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"
        
        # Log only if not excessive polling, to keep our logs clean
        if "/poll/" not in request.url.path:
            logger.debug(f"{request.method} {request.url.path} completed in {process_time_ms:.2f}ms")
            
        return response
