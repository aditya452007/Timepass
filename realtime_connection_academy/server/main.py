"""
MODULE OVERVIEW:
The FastAPI application Factory.

WHAT IS HAPPENING HERE:
We use a `lifespan` context manager. When Uvicorn starts the server, we enter the lifespan,
where we spawn all our Dummy Data generators as `asyncio.create_task` background loops.
When the server shuts down, the lifespan executes its `finally` block, cleanly
cancelling all generators and closing connections. No memory leaks.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager
from loguru import logger

from server.connection_manager import manager
from server.dummy_data import get_all_generators
from server.middleware import TimingMiddleware

from server.routes import (
    short_polling,
    long_polling,
    sse,
    websocket,
    hybrid_ws_sse,
    hybrid_sse_longpoll,
    hybrid_ws_shortpoll,
    hybrid_triple
)

# We store our background tasks here so we can cancel them on shutdown.
background_tasks = set()

async def generator_runner(generator_func):
    """Consumes a dummy data generator and pushes events to our global ConnectionManager."""
    try:
        async for event in generator_func:
            # Broadcast the event to all connected clients natively
            await manager.push_event(event)
    except asyncio.CancelledError:
        logger.debug(f"Generator cancelled: {generator_func.__name__}")
    except Exception as e:
        logger.error(f"Generator error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logger.info("RealTime Connection Academy server starting up...")
    
    # Start all dummy data generators
    for gen in get_all_generators():
        task = asyncio.create_task(generator_runner(gen))
        background_tasks.add(task)
        
    logger.info(f"Started {len(background_tasks)} background generators.")
    
    yield
    
    # SHUTDOWN
    logger.info("Server shutting down. Cancelling background tasks...")
    for task in background_tasks:
        task.cancel()
    
    # Wait for them to exit cleanly
    if background_tasks:
        await asyncio.gather(*background_tasks, return_exceptions=True)
    logger.info("Shutdown complete.")


app = FastAPI(
    title="RealTime Connection Academy",
    description="A visual study of web connection protocols",
    version="1.0.0",
    lifespan=lifespan
)

# Add Middlewares
app.add_middleware(TimingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route registrations
app.include_router(short_polling.router, tags=["Protocols"])
app.include_router(long_polling.router, tags=["Protocols"])
app.include_router(sse.router, tags=["Protocols"])
app.include_router(websocket.router, tags=["Protocols"])

app.include_router(hybrid_ws_sse.router, tags=["Hybrid Advanced"])
app.include_router(hybrid_sse_longpoll.router, tags=["Hybrid Advanced"])
app.include_router(hybrid_ws_shortpoll.router, tags=["Hybrid Advanced"])
app.include_router(hybrid_triple.router, tags=["Hybrid Advanced"])

@app.get("/healthz", tags=["Ops"])
async def health_check():
    return {"status": "ok"}

@app.get("/stats", tags=["Ops"])
async def get_stats():
    return manager.get_stats()
