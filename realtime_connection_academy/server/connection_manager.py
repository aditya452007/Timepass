"""
MODULE OVERVIEW:
The central state registry and pub/sub implementation.
This file is the heartbeat of the architecture. It maps protocol types to the
native OS/async primitives needed to hold connections open or track data.

WHAT IS HAPPENING HERE:
This single object holds references to every active WebSocket, every waiting Long Poll
request, and every open SSE stream. When `push_event()` is called (by the generators),
it fans out the event to all active storage mechanisms simultaneously.
Real-world application: Slack's "Flannel" edge service or GitHub's live update router.
"""

import asyncio
from typing import Dict, List
from datetime import datetime, timezone
from fastapi.websockets import WebSocket
from loguru import logger
from collections import deque

from shared.models import Event, ConnectionStats

class ConnectionManager:
    def __init__(self):
        # 🟢 WebSockets: Direct TCP connections. We hold the WebSocket object.
        self.active_websockets: Dict[str, WebSocket] = {}
        
        # 🔵 SSE: Unidirectional streams. We hold an asyncio.Queue for each client.
        self.sse_queues: Dict[str, asyncio.Queue[Event]] = {}
        
        # 🟡 Long Polling: Waiting HTTP requests. We hold an asyncio.Event that 
        # gets `.set()` when new data arrives.
        self.long_poll_waiters: Dict[str, asyncio.Event] = {}
        
        # 🟠 Short Polling / General State Buffer. 
        # Since Short Polling clients come and go statelessly, the server must keep
        # a rolling buffer of recent events. We keep the last 200 events.
        self.recent_events_buffer: deque[Event] = deque(maxlen=200)
        
        self.total_events_dispatched = 0
        self.startup_time = datetime.now(timezone.utc)

    # ==========================
    # WEBSOCKET MANAGEMENT
    # ==========================
    async def connect_ws(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_websockets[client_id] = websocket
        logger.info(f"client_id={client_id} protocol=websocket event=connect reason=accepted")

    def disconnect_ws(self, client_id: str):
        if client_id in self.active_websockets:
            del self.active_websockets[client_id]
            logger.info(f"client_id={client_id} protocol=websocket event=disconnect reason=cleanup")

    async def broadcast_ws(self, original_event: Event):
        # We must create a copy since we mutate protocol field and dict might change
        disconnected = []
        
        # We model_copy() so we can mutate the protocol string without affecting other transports
        event_dict = original_event.model_dump()
        event_dict["protocol"] = "websocket"
        serialized_json = Event(**event_dict).model_dump_json()
        
        for client_id, ws in self.active_websockets.items():
            try:
                await ws.send_text(serialized_json)
            except Exception as e:
                logger.warning(f"client_id={client_id} protocol=websocket event=error reason='{e}'")
                disconnected.append(client_id)
                
        for client_id in disconnected:
            self.disconnect_ws(client_id)

    # ==========================
    # SSE MANAGEMENT
    # ==========================
    def subscribe_sse(self, client_id: str) -> asyncio.Queue[Event]:
        # Give the client a dedicated queue. Size 100 prevents memory leaks if client is slow.
        queue: asyncio.Queue[Event] = asyncio.Queue(maxsize=100)
        self.sse_queues[client_id] = queue
        logger.info(f"client_id={client_id} protocol=sse event=connect reason=subscribed")
        return queue

    def unsubscribe_sse(self, client_id: str):
        if client_id in self.sse_queues:
            del self.sse_queues[client_id]
            logger.info(f"client_id={client_id} protocol=sse event=disconnect reason=cleanup")

    def _broadcast_sse(self, original_event: Event):
        event_dict = original_event.model_dump()
        event_dict["protocol"] = "sse"
        event = Event(**event_dict)
        
        for client_id, queue in self.sse_queues.items():
            try:
                # put_nowait avoids blocking the central fan-out loop
                queue.put_nowait(event)
            except asyncio.QueueFull:
                logger.warning(f"client_id={client_id} protocol=sse event=dropped reason=queue_full")

    # ==========================
    # LONG POLL MANAGEMENT
    # ==========================
    def register_long_poll(self, client_id: str) -> asyncio.Event:
        event = asyncio.Event()
        self.long_poll_waiters[client_id] = event
        logger.debug(f"client_id={client_id} protocol=long_poll event=wait reason=registered")
        return event

    def unregister_long_poll(self, client_id: str):
        if client_id in self.long_poll_waiters:
            del self.long_poll_waiters[client_id]

    def _notify_long_polls(self):
        """Wake up all sleeping long poll requests."""
        # When we set() the event, the waiting requests resume execution in routes/long_polling.py
        for client_id, event in self.long_poll_waiters.items():
            event.set()
        # We don't delete them here; the route handler deletes them after waking up

    # ==========================
    # CENTRAL FAN-OUT
    # ==========================
    async def push_event(self, event: Event):
        """
        WHAT IS HAPPENING HERE:
        This is the fan-out mechanism. One event comes in from a generator,
        and we distribute it to ALL storage mechanisms simultaneously.
        """
        self.total_events_dispatched += 1
        
        # 1. Store in historical buffer (for short polls to grab)
        self.recent_events_buffer.append(event)
        
        # 2. Wake up Long Pollers
        self._notify_long_polls()
        
        # 3. Queue for SSE streams
        self._broadcast_sse(event)
        
        # 4. Push directly to open WebSockets
        await self.broadcast_ws(event)

    # ==========================
    # METRICS
    # ==========================
    def get_stats(self) -> ConnectionStats:
        return ConnectionStats(
            active_ws=len(self.active_websockets),
            active_sse=len(self.sse_queues),
            pending_long_polls=len(self.long_poll_waiters),
            total_events_dispatched=self.total_events_dispatched,
            uptime_s=(datetime.now(timezone.utc) - self.startup_time).total_seconds(),
            server_time=datetime.now(timezone.utc)
        )

# Global singleton instance
manager = ConnectionManager()
