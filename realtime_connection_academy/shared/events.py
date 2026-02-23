"""
MODULE OVERVIEW:
This module provides the core primitives for the internal event bus. 

WHAT IS HAPPENING HERE:
In a real distributed system (e.g., multi-worker Gunicorn or horizontal scaling),
this would be replaced by Redis Pub/Sub, Kafka, or RabbitMQ.
Because we run on an isolated event loop (single uvicorn worker) for this teaching project,
we use a simple in-memory GlobalInternalBus to decouple data generators from the ConnectionManager.

The dummy generators publish here -> ConnectionManager subscribes here.
"""

from typing import Callable, Awaitable, List
from loguru import logger
from .models import Event

class GlobalInternalBus:
    """
    A minimal singleton pub/sub bus to decouple publishers (generators) from subscribers (manager).
    """
    def __init__(self):
        self._subscribers: List[Callable[[Event], Awaitable[None]]] = []
        
    def subscribe(self, callback: Callable[[Event], Awaitable[None]]):
        self._subscribers.append(callback)
        
    async def publish(self, event: Event):
        for sub in self._subscribers:
            try:
                await sub(event)
            except Exception as e:
                logger.error(f"Error in subscriber during publish: {e}")

# The singleton instance used system-wide
global_bus = GlobalInternalBus()
