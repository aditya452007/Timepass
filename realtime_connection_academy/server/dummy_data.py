"""
MODULE OVERVIEW:
This module contains infinite background async generators that produce realistic fake data.

WHAT IS HAPPENING HERE:
In a real system, these would represent external Webhook handlers, database CDC (Change Data Capture)
streams (like PostgreSQL logical replication), or message queues like Kafka consumers.
Here, we simulate them so we have constant, predictable traffic to test our protocols.
"""

import asyncio
import random
from datetime import datetime, timezone
from shared.models import Event

async def stock_ticker_generator(source: str = "stocks"):
    """Emits fake ticker symbols with price deltas every 0.5s - 2s."""
    symbols = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN"]
    prices = {s: random.uniform(100.0, 900.0) for s in symbols}
    
    while True:
        symbol = random.choice(symbols)
        delta = random.uniform(-2.5, 2.5)
        prices[symbol] += delta
        
        event = Event(
            event_type="stock_tick",
            payload={
                "ticker": symbol,
                "price": round(prices[symbol], 2),
                "delta": round(delta, 2),
                "volume": random.randint(100, 15000),
                "market": "NASDAQ"
            },
            generated_at=datetime.now(timezone.utc),
            source=source
        )
        yield event
        await asyncio.sleep(random.uniform(0.5, 2.0))

async def live_score_generator(source: str = "sports"):
    """Emits fake sports events irregularly (goals, subs)."""
    teams = [("Manchester", "Arsenal"), ("Lakers", "Warriors"), ("Madrid", "Barcelona")]
    
    while True:
        match = random.choice(teams)
        event_types = ["GOAL", "SUBSTITUTION", "FOUL", "TIMEOUT"]
        action = random.choice(event_types)
        
        event = Event(
            event_type="score_update",
            payload={
                "match": f"{match[0]} vs {match[1]}",
                "action": action,
                "team": random.choice(match),
                "minute": random.randint(1, 90)
            },
            generated_at=datetime.now(timezone.utc),
            source=source
        )
        yield event
        # Irregular intervals (simulating bursty events)
        await asyncio.sleep(random.uniform(1.0, 5.0))

async def system_metrics_generator(source: str = "metrics"):
    """Emits CPU/Memory metrics consistently every 1s."""
    cpu = 40.0
    mem = 60.0
    
    while True:
        cpu = max(0.0, min(100.0, cpu + random.uniform(-5.0, 5.0)))
        mem = max(0.0, min(100.0, mem + random.uniform(-2.0, 2.0)))
        
        event = Event(
            event_type="metric",
            payload={
                "cpu_percent": round(cpu, 1),
                "memory_percent": round(mem, 1),
                "disk_io": random.randint(0, 1000)
            },
            generated_at=datetime.now(timezone.utc),
            source=source
        )
        yield event
        await asyncio.sleep(1.0)

async def notification_generator(source: str = "social"):
    """Emits user notifications randomly."""
    users = ["@alice", "@bob", "@charlie", "@dave"]
    actions = ["liked your post", "mentioned you", "sent a friend request", "placed order #4821"]
    
    while True:
        event = Event(
            event_type="notification",
            payload={
                "user": random.choice(users),
                "action": random.choice(actions)
            },
            generated_at=datetime.now(timezone.utc),
            source=source
        )
        yield event
        await asyncio.sleep(random.uniform(2.0, 8.0))

async def weather_event_generator(source: str = "weather"):
    """Slow moving data every 5s."""
    temp = 22.0
    while True:
        temp += random.uniform(-0.5, 0.5)
        event = Event(
            event_type="weather",
            payload={
                "temperature": round(temp, 1),
                "wind_kph": random.randint(5, 30),
                "uv_index": random.randint(1, 11)
            },
            generated_at=datetime.now(timezone.utc),
            source=source
        )
        yield event
        await asyncio.sleep(5.0)

def get_all_generators():
    """Helper to retrieve all instantiated async generators."""
    return [
        stock_ticker_generator(),
        live_score_generator(),
        system_metrics_generator(),
        notification_generator(),
        weather_event_generator()
    ]
