# REFACTOR DELTA: 49 lines -> 35 lines (-14 lines, -29%)
"""
MODULE OVERVIEW:
The Short Polling HTTP client implementation.

WHAT IS HAPPENING HERE:
We use HTTPX to make constant, repeated GET requests.
Notice the classic "wait-and-retry" loop containing exponential backoff for network errors.
"""
import asyncio
import httpx
from json import JSONDecodeError

from client.base_client import BaseConnectionClient
from shared.models import PollResponse

class ShortPollClient(BaseConnectionClient):
    protocol_name: str = "short-poll"

    def __init__(self, client_id: str, server_base_url: str, interval_s: float = 2.0):
        super().__init__(client_id, server_base_url)
        self.interval_s = interval_s
        self.last_seen_id: str | None = None
        self.client = httpx.AsyncClient(timeout=10.0)

    async def disconnect(self) -> None:
        await self.client.aclose()

    async def connect(self) -> None:
        await self._emit_status("ACTIVE")
        url = f"{self.server_base_url}/poll/short?client_id={self.client_id}"
        if self.last_seen_id:
            url += f"&last_seen_id={self.last_seen_id}"
            
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            poll_resp = PollResponse.model_validate(response.json())
        except JSONDecodeError as e:
            raise httpx.HTTPError(str(e))
            
        if poll_resp.events:
            for e in poll_resp.events:
                self.last_seen_id = e.event_id
                await self.on_event(e)
        else:
            self.empty_responses += 1
            
        wait_time = max(0.1, poll_resp.next_poll_ms / 1000.0)
        await asyncio.sleep(wait_time)
