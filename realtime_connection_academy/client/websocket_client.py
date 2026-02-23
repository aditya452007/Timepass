# REFACTOR DELTA: 61 lines -> 43 lines (-18 lines, -30%)
"""
MODULE OVERVIEW:
The WebSocket client implementation.

WHAT IS HAPPENING HERE:
We use the `websockets` library. A WebSocket connection requires two separate async loops
running over the same socket: one to read incoming data, one to send outgoing data.
We also implement application-level ping/pong to detect zombies.
"""

import json
import websockets

from client.base_client import BaseConnectionClient
from shared.models import Event

class WebSocketClient(BaseConnectionClient):
    protocol_name: str = "websocket"

    def __init__(self, client_id: str, server_base_url: str):
        super().__init__(client_id, server_base_url)
        self.ws_url = f"{self.server_base_url.replace('http://', 'ws://').replace('https://', 'wss://')}/ws/connect?client_id={self.client_id}"

    async def disconnect(self) -> None:
        pass

    async def connect(self) -> None:
        async with websockets.connect(self.ws_url, ping_interval=None) as ws:
            await self._emit_status("ACTIVE")
            await ws.send(json.dumps({"action": "subscribe", "channel": "all"}))

            while True:
                message = await ws.recv()
                try:
                    data = json.loads(message)
                    if data.get("type") == "ping":
                        await ws.send(json.dumps({"type": "pong"}))
                    else:
                        await self.on_event(Event.model_validate(data))
                except json.JSONDecodeError:
                    pass
