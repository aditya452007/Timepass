# REFACTOR DELTA: 55 lines -> 37 lines (-18 lines, -33%)
"""
MODULE OVERVIEW:
The Long Polling HTTP client implementation.

WHAT IS HAPPENING HERE:
Similar to Short Polling, but notice our HTTpx timeout is explicitly set HIGHER
than the server's timeout (Server=30s, Client=35s). 
If the server times out internally, it returns a {"status": "timeout"} JSON softly,
and we instantly reconnect. If the TCP connection actually drops before 35s, it raises
a network error, triggering exponential backoff.
"""
import asyncio
import httpx
from json import JSONDecodeError

from client.base_client import BaseConnectionClient
from shared.models import PollResponse

class LongPollClient(BaseConnectionClient):
    protocol_name: str = "long-poll"

    def __init__(self, client_id: str, server_base_url: str):
        super().__init__(client_id, server_base_url)
        self.client = httpx.AsyncClient(timeout=35.0)

    async def disconnect(self) -> None:
        await self.client.aclose()

    async def connect(self) -> None:
        await self._emit_status("WAITING")
        url = f"{self.server_base_url}/poll/long?client_id={self.client_id}"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            poll_resp = PollResponse.model_validate(response.json())
        except (httpx.ReadTimeout, JSONDecodeError) as e:
            raise httpx.RequestError(str(e), request=getattr(e, 'request', None))
            
        if poll_resp.status == "timeout":
            self.empty_responses += 1
            await self._emit_status("ACTIVE (timeout)")
            await asyncio.sleep(poll_resp.next_poll_ms / 1000.0)
        else:
            await self._emit_status("ACTIVE (data)")
            for e in poll_resp.events:
                await self.on_event(e)
            await asyncio.sleep(0.05)
