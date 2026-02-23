# REFACTOR DELTA: 65 lines -> 54 lines (-11 lines, -17%)
from abc import ABC, abstractmethod
import asyncio
from typing import Callable, Awaitable
from shared.models import Event
from shared.client_utils import make_client_stats, with_reconnect

class BaseConnectionClient(ABC):
    protocol_name: str = "unknown"

    def __init__(self, client_id: str, server_base_url: str):
        self.client_id = client_id
        self.server_base_url = server_base_url.rstrip('/')
        
        self.on_event_callback: Callable[[Event], Awaitable[None]] | None = None
        self.on_status_change_callback: Callable[[str], Awaitable[None]] | None = None
        
        self.stats = make_client_stats()
        self._is_running = False

    @property
    def events_received(self): return self.stats["events_received"]
    @events_received.setter
    def events_received(self, value): self.stats["events_received"] = value
    
    @property
    def reconnect_count(self): return self.stats["reconnect_count"]
    @reconnect_count.setter
    def reconnect_count(self, value): self.stats["reconnect_count"] = value
    
    @property
    def empty_responses(self): return self.stats["empty_responses"]
    @empty_responses.setter
    def empty_responses(self, value): self.stats["empty_responses"] = value

    def set_callbacks(self, on_event, on_status_change):
        self.on_event_callback = on_event
        self.on_status_change_callback = on_status_change

    async def _emit_status(self, status: str):
        if self.on_status_change_callback:
            await self.on_status_change_callback(status)

    async def push_to_visualizer(self, event: Event):
        self.stats["events_received"] += 1
        if self.on_event_callback:
            await self.on_event_callback(event)

    async def on_event(self, event: Event):
        await self.push_to_visualizer(event)

    @abstractmethod
    async def connect(self) -> None:
        """The actual protocol implementation loop runs here."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass

    async def run(self, duration_s: float = 60.0) -> None:
        self._is_running = True
        try:
            await with_reconnect(
                self.connect, 
                self.stats, 
                duration_s, 
                protocol=self.protocol_name, 
                client_id=self.client_id
            )
        except asyncio.CancelledError:
            pass
        finally:
            self._is_running = False
            await self.disconnect()
            await self._emit_status("CLOSED")
