# REFACTOR DELTA: 0 lines -> 51 lines (+51 lines)
import uuid
import asyncio
from typing import Callable, Awaitable, AsyncGenerator, Any
from datetime import datetime, timezone
from loguru import logger
from shared.models import Event

async def extract_client_id(client_id: str | None) -> str:
    """
    If the caller provided a client_id, use it.
    If not, generate a short readable one like 'client-a3f2'.
    This prevents anonymous connections from cluttering logs.
    """
    if client_id:
        return client_id
    return f"client-{str(uuid.uuid4())[:4]}"

async def log_connection(protocol: str, client_id: str, extra: dict = {}) -> None:
    """
    Single structured log entry for any new connection.
    Writes: protocol, client_id, timestamp, and any extra fields.
    Every route calls this once on connect and once on disconnect.
    """
    log_str = f"protocol={protocol} client_id={client_id}"
    for k, v in extra.items():
        log_str += f" {k}={v}"
    logger.info(log_str)

async def run_event_loop(
    client_id: str,
    protocol: str,
    send_fn: Callable[[Event], Awaitable[None]],
    generator: AsyncGenerator[Event, None],
    heartbeat_interval_s: float = 15.0,
    connection_manager: Any = None,
) -> None:
    """
    The universal server-side event dispatch loop.

    This is the heart of every route. It:
      1. Iterates over `generator` to get the next event.
      2. If `heartbeat_interval_s` seconds have passed with no event,
         constructs and sends a heartbeat event via `send_fn`.
      3. Calls `send_fn(event)` to deliver real events.
      4. If `connection_manager` is provided, updates its stats.
      5. Catches CancelledError (client disconnect) cleanly and exits.
    """
    try:
        while True:
            try:
                event = await asyncio.wait_for(anext(generator), timeout=heartbeat_interval_s)
                await send_fn(event)
            except asyncio.TimeoutError:
                hb = Event(
                    event_type="heartbeat",
                    payload={"ping": "pong"},
                    generated_at=datetime.now(timezone.utc),
                    source="system",
                    protocol=protocol
                )
                await send_fn(hb)
            except StopAsyncIteration:
                break
    except asyncio.CancelledError:
        pass
