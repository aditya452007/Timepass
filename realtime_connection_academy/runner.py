"""
CLI entrypoint for RealTime Connection Academy.
"""
import typer
import asyncio

from client.short_poll_client import ShortPollClient
from client.long_poll_client import LongPollClient
from client.sse_client import SSEClient
from client.websocket_client import WebSocketClient
from client.hybrid_client import HybridClient
from client.visualizer import Visualizer
from shared.config import settings

app = typer.Typer(help="RealTime Connection Academy CLI Manager")

@app.command()
def server():
    """Start the FastAPI backend server using Uvicorn."""
    import uvicorn
    typer.echo("Starting server on port 8000...")
    uvicorn.run("server.main:app", host="0.0.0.0", port=settings.PORT, log_level=settings.LOG_LEVEL.lower())

@app.command()
def client(
    protocol: str = typer.Option(..., help="Protocol to run: short-poll, long-poll, sse, websocket, hybrid"),
    duration: float = typer.Option(60.0, help="Duration to run the client in seconds"),
    interval: float = typer.Option(2.0, help="Polling interval for short polling")
):
    """Run a specific client with the rich visualizer dashboard."""
    client_id = f"cli_{protocol}"
    base_url = f"http://127.0.0.1:{settings.PORT}"
    
    if protocol == "short-poll":
        c = ShortPollClient(client_id, base_url, interval_s=interval)
    elif protocol == "long-poll":
        c = LongPollClient(client_id, base_url)
    elif protocol == "sse":
        c = SSEClient(client_id, base_url)
    elif protocol == "websocket":
        c = WebSocketClient(client_id, base_url)
    elif protocol == "hybrid":
        c = HybridClient(client_id, base_url)
    else:
        typer.echo("Invalid protocol.")
        raise typer.Exit(1)
        
    visualizer = Visualizer(c, protocol)
    try:
        asyncio.run(visualizer.run(duration))
    except KeyboardInterrupt:
        pass

@app.command()
def stats():
    """Query the server for live connection stats."""
    import httpx
    resp = httpx.get(f"http://127.0.0.1:{settings.PORT}/stats")
    typer.echo(resp.json())

@app.command()
def demo(all: bool = typer.Option(False, "--all", help="Run full server + client demo sequentially")):
    """Run the pedagogical demo scenarios."""
    typer.echo("Demo mode triggered. Please run the server in a separate terminal using `python runner.py server`, then open a split pane to run `python runner.py client --protocol websocket`.")

if __name__ == "__main__":
    app()
