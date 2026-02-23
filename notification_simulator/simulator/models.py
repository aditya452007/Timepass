# models.py
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class NotificationEvent:
    event_type: str
    user_id: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    priority: str = "normal"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class QueueMessage:
    message_id: str
    event_id: str
    channel: str
    payload: Dict[str, Any]
    retries: int = 0
    status: str = "pending" # pending, processing, success, failed, dlq
    error_reason: Optional[str] = None
    
@dataclass
class DeliveryLog:
    timestamp: float
    stage: str
    event_id: str
    message: str
    details: Dict[str, Any]
    status: str # info, success, warning, error
