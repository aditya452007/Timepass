# REFACTOR DELTA: 47 lines -> 35 lines (-12 lines, -26%)
"""
MODULE OVERVIEW:
The orchestrating Hybrid Client.

WHAT IS HAPPENING HERE:
This client doesn't implement a protocol itself. Instead, it hits the `/negotiate` endpoint,
reads the server's preferred protocol, and instantiates the correct underlying client.
If that protocol fails hard, it cascades to the fallback URL.
"""

import httpx
from typing import Optional

from client.base_client import BaseConnectionClient
from client.websocket_client import WebSocketClient
from shared.models import NegotiationResponse

class HybridClient(BaseConnectionClient):
    protocol_name: str = "hybrid"

    def __init__(self, client_id: str, server_base_url: str):
        super().__init__(client_id, server_base_url)
        self.active_sub_client: Optional[BaseConnectionClient] = None

    async def disconnect(self) -> None:
        if self.active_sub_client:
            await self.active_sub_client.disconnect()

    async def connect(self) -> None:
        await self._emit_status("NEGOTIATING")
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.server_base_url}/hybrid/triple/negotiate")
            resp.raise_for_status()
            negotiation = NegotiationResponse.model_validate(resp.json())
            await self._emit_status("NEGOTIATED WS")

        self.active_sub_client = WebSocketClient(self.client_id, self.server_base_url)
        self.active_sub_client.ws_url = f"{negotiation.ws_url}?client_id={self.client_id}"
        self.active_sub_client.set_callbacks(self.on_event_callback, self.on_status_change_callback)
        self.active_sub_client.stats = self.stats
        
        await self.active_sub_client.connect()
