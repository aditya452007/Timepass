# REFACTOR DELTA: 61 lines -> 46 lines (-15 lines, -25%)
"""
MODULE OVERVIEW:
The Server-Sent Events HTTP client implementation.

WHAT IS HAPPENING HERE:
We use HTTPX `stream()` context manager to keep the body open.
We manually parse the `event: ` and `data: ` chunks to demonstrate the RAW text protocol.
We don't use a library here so students can see exactly what the browser EventSource API does under the hood.
"""
import httpx
import json

from client.base_client import BaseConnectionClient
from shared.models import Event

class SSEClient(BaseConnectionClient):
    protocol_name: str = "sse"

    def __init__(self, client_id: str, server_base_url: str):
        super().__init__(client_id, server_base_url)
        self.client = httpx.AsyncClient(timeout=60.0)

    async def disconnect(self) -> None:
        await self.client.aclose()

    async def connect(self) -> None:
        url = f"{self.server_base_url}/sse/stream?client_id={self.client_id}"
        
        async with self.client.stream("GET", url, headers={"Accept": "text/event-stream", "Cache-Control": "no-cache"}) as response:
            response.raise_for_status()
            await self._emit_status("ACTIVE")
            
            buffer = ""
            async for chunk in response.aiter_text():
                buffer += chunk
                while "\n\n" in buffer:
                    block, buffer = buffer.split("\n\n", 1)
                    await self._parse_sse_block(block)

    async def _parse_sse_block(self, block: str):
        lines = block.strip().split("\n")
        event_type = "message"
        data_str = ""
        
        for line in lines:
            if line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                data_str += line.split(":", 1)[1].strip() + "\n"
                
        data_str = data_str.strip()
        
        if event_type != "heartbeat" and data_str:
            try:
                event = Event.model_validate(json.loads(data_str))
                await self.on_event(event)
            except json.JSONDecodeError:
                pass
