"""
MODULE OVERVIEW:
This module defines the strictly typed data structures used across both the Server
and Client in RealTime Connection Academy, powered by Pydantic v2.

WHAT IS HAPPENING HERE:
By defining our models centrally, we ensure our API contracts are strictly enforced.
Any event dispatched by the dummy data generators must conform to `Event`. Any response
sent to a Short Poll or Long Poll client must conform to `PollResponse`.
This mimics a monorepo setup where frontend and backend share type definitions.
"""
from typing import Any, Literal
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel, Field

# WHAT IS HAPPENING HERE:
# This is the universal wrapper for a piece of data in our system.
# The `protocol` field allows clients to know exactly which transport delivered the message,
# proving that multiple protocols can carry the exact same underlying payload.
class Event(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: Literal[
        "stock_tick", "score_update", "metric", "notification", 
        "weather", "heartbeat", "ping", "pong", "error", "control"
    ]
    payload: dict[str, Any]
    generated_at: datetime
    source: str
    protocol: str = "internal"

# WHAT IS HAPPENING HERE:
# Short and Long Polling endpoints return batches of events.
# We include `next_poll_ms` and `server_time` to gracefully handle backpressure.
class PollResponse(BaseModel):
    events: list[Event]
    status: Literal["ok", "timeout", "empty"]
    next_poll_ms: int
    server_time: datetime

# WHAT IS HAPPENING HERE:
# The hybrid negotiation response. The server evaluates user-agent or simulated capability,
# and prescribes an ordered list of fallback protocols.
class NegotiationResponse(BaseModel):
    preferred: Literal["websocket", "sse", "long_poll", "short_poll"]
    fallback: list[Literal["websocket", "sse", "long_poll", "short_poll"]]
    ws_url: str | None
    sse_url: str | None
    long_poll_url: str | None
    short_poll_url: str | None
    reason: str

class ConnectionStats(BaseModel):
    active_ws: int
    active_sse: int
    pending_long_polls: int
    total_events_dispatched: int
    uptime_s: float
    server_time: datetime
