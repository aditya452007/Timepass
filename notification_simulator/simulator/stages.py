# stages.py
from typing import List, Dict, Any
from .config import CONFIG
from .models import NotificationEvent

# Simulated "Database" of user preferences
USER_DATABASE = {
    "user_123": {
        "dnd_mode": False,
        "opted_out_channels": [],
        "online": True
    }
}

def get_user_data(user_id: str, overrides: Dict[str, Any] = None) -> Dict[str, Any]:
    """Fetch user data, allowing simulation overrides."""
    base_data = USER_DATABASE.get(user_id, {
        "dnd_mode": False,
        "opted_out_channels": [],
        "online": False
    }).copy()
    if overrides:
        base_data.update(overrides)
    return base_data

def ingestion_layer(event_type: str, user_id: str) -> NotificationEvent:
    """Stage 1: API Gateway / Ingestion Layer"""
    event_config = CONFIG["events"].get(event_type)
    if not event_config:
        raise ValueError(f"Unknown event type: {event_type}")
        
    event = NotificationEvent(
        event_type=event_type,
        user_id=user_id,
        priority=event_config["priority"],
        metadata={"default_channels": event_config["default_channels"]}
    )
    return event

def preference_checker(event: NotificationEvent, user_data: Dict[str, Any]) -> List[str]:
    """Stage 2: Check User Preferences and DND"""
    approved_channels = event.metadata["default_channels"].copy()
    
    if event.priority != "critical" and user_data["dnd_mode"]:
        # Block promotional and normal messages during DND
        return []
    
    # Remove opted-out channels
    approved_channels = [c for c in approved_channels if c not in user_data.get("opted_out_channels", [])]
    return approved_channels

def online_status_checker(event: NotificationEvent, approved_channels: List[str], user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Stage 3: Check Online Status (Redis Simulation)"""
    final_channels = approved_channels.copy()
    decisions = []
    
    is_online = user_data["online"]
    
    if is_online:
        decisions.append("User is ONLINE.")
        if "in_app" in final_channels:
            if "email" in final_channels and event.priority != "critical":
                final_channels.remove("email")
                decisions.append("Email suppressed because user is active right now.")
    else:
        decisions.append("User is OFFLINE.")
        if "in_app" not in final_channels and "push" in CONFIG["events"][event.event_type]["default_channels"]:
             pass 

    return {
        "channels": final_channels,
        "decisions": decisions
    }
