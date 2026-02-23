# RealTime Connection Academy 🎓

A visual, production-grade study of web connection protocols. Learn how real-time communication works under the hood by observing how different transports behave concurrently.

## Learning Objectives
After running this demonstration suite, you will understand:
1. Why **Short Polling** wastes server resources but is bulletproof.
2. How **Long Polling** achieves near-WebSocket latency using HTTP and TCP connection holding.
3. The exact plain-text wire format of **Server-Sent Events (SSE)** chunked streams.
4. How **WebSockets** perform full-duplex binary framing over a persistent TCP socket.
5. Why production systems (like Slack or Socket.IO) use **Hybrid Negotiation Cascades**.

## Setup Instructions
This project requires Python 3.12+.

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy the environment variables:
   ```bash
   cp .env.example .env
   ```

## Getting Started
Run the full showcase. In terminal 1, start the server:
```bash
python runner.py server
```
In terminal 2, explore the demo scenarios (see `demo_scenarios.md` for full commands), for example:
```bash
python runner.py client --protocol websocket
```

## The Protocols

### 1. Short Polling (`--protocol short-poll`)
The browser repeatedly asks "Do you have data?" every N seconds.
- **When to use:** Legacy systems, systems lacking async infrastructure.
- **Why it hurts:** Massive HTTP overhead, high latency, battery drain on mobile.

### 2. Long Polling (`--protocol long-poll`)
The browser asks "Do you have data?" The server *holds the connection open* until data arrives or a timeout occurs, then responds. The client instantly asks again.
- **When to use:** When true WebSockets are blocked by restrictive enterprise proxies.
- **Why it hurts:** High server memory overhead to hold connections open in synchronous languages.

### 3. Server-Sent Events/SSE (`--protocol sse`)
The client opens an HTTP GET request, and the server leaves the response body open, streaming chunks of text data indefinitely.
- **When to use:** One-way data feeds (Stock tickers, LLM text streaming, Notifications).
- **Why it hurts:** Unidirectional only. Cannot easily send high-frequency data *back* to the server on the same socket.

### 4. WebSockets (`--protocol websocket`)
The client "upgrades" an HTTP request into a raw TCP socket. Both sides can read and write frames at any time.
- **When to use:** Multiplayer games, chat, collaborative editing.
- **Why it hurts:** Requires complex load balancing (Redis pub/sub) and zombie-connection culling at scale.
