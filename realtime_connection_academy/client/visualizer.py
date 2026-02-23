"""
MODULE OVERVIEW:
The Rich Terminal Dashboard.

WHAT IS HAPPENING HERE:
We use Rich to build a beautiful terminal dashboard.
It runs the client loop in the background and updates the Layout UI on every callback
from the client's hooks.
"""

from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from collections import deque
from datetime import datetime
import asyncio

from client.base_client import BaseConnectionClient

PROTOCOL_INFO = {
    "short-poll": "Short Polling: Constantly asking 'Are we there yet?' High overhead.",
    "long-poll": "Long Polling: Holds the HTTP TCP connection open until data arrives or timeout.",
    "sse": "Server-Sent Events: Unidirectional persistent HTTP stream.",
    "websocket": "WebSocket: Full-duplex persistent TCP connection.",
    "hybrid": "Hybrid Cascade: Negotiated protocol (WS->SSE->LP)."
}

class Visualizer:
    def __init__(self, client: BaseConnectionClient, protocol_name: str):
        self.client = client
        self.protocol_name = protocol_name
        self.recent_events = deque(maxlen=10)
        self.status = "INITIALIZING"
        self.timeline = deque(maxlen=5)

    def on_status_change(self, status: str):
        self.status = status
        ts = datetime.now().strftime("%H:%M:%S")
        self.timeline.appendleft(f"[{ts}] State: {status}")

    def on_event(self, event):
        ts = datetime.now().strftime("%H:%M:%S")
        payload_str = str(event.payload)[:40] + "..." if len(str(event.payload)) > 40 else str(event.payload)
        self.recent_events.appendleft((ts, event.event_type, payload_str, event.protocol))

    def generate_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main")
        )
        layout["main"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )
        layout["right"].split_column(
            Layout(name="stats"),
            Layout(name="timeline"),
            Layout(name="info")
        )
        
        # Header
        color = "green" if "ACTIVE" in self.status else "yellow" if "WAITING" in self.status else "red"
        layout["header"].update(Panel(f"[{color} bold]Protocol: {self.client.__class__.__name__} | Status: {self.status}[/]", style=color))
        
        # Feed Table
        table = Table(title="Live Event Feed", expand=True)
        table.add_column("Time", justify="left", style="cyan", no_wrap=True)
        table.add_column("Type", style="magenta")
        table.add_column("Payload", style="green")
        table.add_column("Transport", style="blue")
        
        for e in self.recent_events:
            table.add_row(e[0], e[1], e[2], e[3])
            
        layout["left"].update(Panel(table, title="Feed"))
        
        # Stats
        stats_text = (
            f"Events Received: {self.client.events_received}\n"
            f"Reconnects: {self.client.reconnect_count}\n"
            f"Empty Responses: {self.client.empty_responses}"
        )
        layout["stats"].update(Panel(stats_text, title="Connection Stats"))
        
        # Timeline
        timeline_text = "\n".join(self.timeline)
        layout["timeline"].update(Panel(timeline_text, title="Timeline"))
        
        # Info
        info = PROTOCOL_INFO.get(self.protocol_name, "Custom Protocol")
        layout["info"].update(Panel(info, title="Pedagogy"))
        
        return layout

    async def run(self, duration_s: float):
        # Bridge the client hooks
        async def event_hook(e): self.on_event(e)
        async def status_hook(s): self.on_status_change(s)
        
        self.client.set_callbacks(event_hook, status_hook)
        
        client_task = asyncio.create_task(self.client.run(duration_s))
        
        with Live(self.generate_layout(), refresh_per_second=4) as live:
            while not client_task.done():
                live.update(self.generate_layout())
                await asyncio.sleep(0.25)
