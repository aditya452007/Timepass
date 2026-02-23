# REFACTOR DELTA: 0 lines -> 46 lines (+46 lines)
import asyncio
import random
from typing import Callable, Awaitable
from loguru import logger
from datetime import datetime, timezone

def make_client_stats() -> dict:
    """
    Returns a fresh stats dictionary with zeroed counters.
    Every client calls this once in __init__.
    Keys: events_received, empty_responses, reconnect_count,
          bytes_received, last_event_at, connected_at.
    """
    return {
        "events_received": 0,
        "empty_responses": 0,
        "reconnect_count": 0,
        "bytes_received": 0,
        "last_event_at": None,
        "connected_at": datetime.now(timezone.utc).isoformat()
    }

async def with_reconnect(
    connect_fn: Callable[[], Awaitable[None]],
    stats: dict,
    duration_s: float,
    base_delay_s: float = 1.0,
    max_delay_s: float = 32.0,
    protocol: str = "unknown",
    client_id: str = "unknown",
) -> None:
    """
    Wraps any async connect function with automatic reconnection.
    """
    import httpx
    import websockets
    attempt = 0
    start_time = asyncio.get_event_loop().time()
    
    while True:
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed >= duration_s:
            break
            
        try:
            # We want to wait for connect_fn, but cap it at the remaining duration
            remaining = duration_s - elapsed
            await asyncio.wait_for(connect_fn(), timeout=remaining)
            attempt = 0
        except asyncio.TimeoutError:
            # Reached max duration normally
            break
        except (ConnectionError, OSError, websockets.WebSocketException, httpx.HTTPError) as e:
            attempt += 1
            delay = min(base_delay_s * (2 ** attempt), max_delay_s)
            delay += random.uniform(0, delay * 0.1)
            stats["reconnect_count"] += 1
            logger.warning(
                f"Protocol {protocol} Client {client_id} Attempt {attempt} "
                f"Delay {delay:.2f}s Error {e}"
            )
            elapsed = asyncio.get_event_loop().time() - start_time
            remaining = duration_s - elapsed
            if remaining > 0:
                try:
                    await asyncio.wait_for(asyncio.sleep(delay), timeout=remaining)
                except asyncio.TimeoutError:
                    break
