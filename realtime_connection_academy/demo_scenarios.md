# Demonstration Scenarios

This repository provides an interactive terminal UI to observe network behaviors. To run these, you must always have the server running in its own terminal:
```bash
python runner.py server
```

## Scenario 1: Short Poll Overhead
**Command:** `python runner.py client --protocol short-poll --interval 1.0`
**What to observe:** Watch the "Empty Responses" counter in the stats panel climb rapidly. Because the server only has new data a fraction of the time, the client is wasting 80% of its requests getting `{"events": [], "status": "empty"}`. This demonstrates the horrific HTTP overhead inherent in Short Polling.

## Scenario 2: Long Poll Efficiency
**Command:** `python runner.py client --protocol long-poll`
**What to observe:** Observe how "Empty Responses" only ticks up once every 30 seconds (when the server intentionally releases the held connection). Notice how events arrive with 0 latency the EXACT millisecond the server generates them.

## Scenario 3: SSE Heartbeats and Streams
**Command:** `python runner.py client --protocol sse`
**What to observe:** Watch the "Timeline" panel. You will see regular `heartbeat` events arrive. This is the server sending tiny ping frames to ensure transparent proxies (like Nginx) don't aggressively kill what looks like an idle, hanging HTTP connection.

## Scenario 4: WS Duplex Nature
**Command:** `python runner.py client --protocol websocket`
**What to observe:** In the timeline, note that the connection is opened and stays strictly in `ACTIVE` state. The rich frame exchange occurs without the overhead of HTTP headers.

## Scenario 5: Hybrid Cascade Resilience
**Command:** `python runner.py client --protocol hybrid`
**What to observe:** The client first hits the `/negotiate` HTTP API to discover what the server supports. It learns the server prefers WebSockets but offers SSE. It then seamlessly connects to the WebSocket stream.

## Scenario 6: The Zombie Connection Reconnect Loop
**Command:** `python runner.py client --protocol websocket`
**Action:** While the client is active, hit `CTRL+C` in the SERVER terminal to kill it.
**What to observe:** Watch the client instantly fall into an exponential backoff state `RECONNECTING (backoff=1.0s)`. Now start the server again. Watch the client successfully re-establish the socket.
