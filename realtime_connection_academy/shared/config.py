"""
MODULE OVERVIEW:
This module provides application-wide configuration using Pydantic Settings.
Where it fits: This represents the central nervous system for environment behaviors.
Real-world application: Centralized config management (like 12-factor apps using external env vars).

WHAT IS HAPPENING HERE:
We are defining all critical protocol timings. Instead of hardcoding "30 seconds"
for a long poll timeout deep in a route, we declare it globally here. This ensures
that if we need to adjust timeouts for load testing, we do it in one place.
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # Short Polling
    SHORT_POLL_INTERVAL_MS: int = 2000
    
    # Long Polling
    LONG_POLL_TIMEOUT_S: float = 30.0
    
    # SSE
    SSE_HEARTBEAT_INTERVAL_S: float = 15.0
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL_S: float = 30.0
    WS_PONG_TIMEOUT_S: float = 5.0
    
    class Config:
        env_file = ".env"
        # Tolerate missing env vars to allow easy out-of-the-box execution
        env_file_encoding = 'utf-8'
        extra = 'ignore'

settings = Settings()
