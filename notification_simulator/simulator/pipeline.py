import time
import json
import uuid
import random
from typing import Generator, Dict, Any
from .config import CONFIG
from .models import NotificationEvent, QueueMessage
from . import stages

class SimulationPipeline:
    def __init__(self, slow_mode: bool = False, fail_rate: int = 0):
        self.slow_mode = slow_mode
        self.fail_rate = fail_rate / 100.0
        self.queues = {channel: [] for channel in CONFIG["channels"]}
        self.dlq = []
        
    def _delay(self, base_time: float):
        if self.slow_mode:
            time.sleep(base_time * CONFIG["simulated_delay"]["slow_mode_multiplier"])
        else:
            time.sleep(base_time)
            
    def _yield_state(self, step: str, status: str, message: str, data: Dict[str, Any] = None) -> str:
        """Helper to yield SSE formatted data"""
        payload = {
            "step": step,
            "status": status, # processing, success, failed, error, info
            "message": message,
            "data": data or {},
            "queues": {ch: len(q) for ch, q in self.queues.items()},
            "dlq_count": len(self.dlq),
            "timestamp": time.time()
        }
        return f"data: {json.dumps(payload)}\n\n"

    def run_simulation(self, event_type: str, user_id: str, overrides: Dict[str, Any]) -> Generator[str, None, None]:
        user_data = stages.get_user_data(user_id, overrides)
        
        # 1. Ingestion
        yield self._yield_state("ingestion", "processing", f"API Gateway received event: {event_type}")
        self._delay(CONFIG["simulated_delay"]["gateway"])
        try:
            event = stages.ingestion_layer(event_type, user_id)
            msg = f"Event parsed. Priority: {event.priority}. Default channels: {', '.join(event.metadata['default_channels'])}"
            yield self._yield_state("ingestion", "success", msg, {"event_id": event.event_id})
        except Exception as e:
            yield self._yield_state("ingestion", "failed", f"Ingestion error: {str(e)}")
            return
            
        # 2. Preference Checker
        yield self._yield_state("preference_check", "processing", "Database Check: User preferences & DND status")
        self._delay(CONFIG["simulated_delay"]["preference_check"])
        approved_channels = stages.preference_checker(event, user_data)
        if not approved_channels:
            yield self._yield_state("preference_check", "failed", "Event blocked by preferences (e.g., DND active).")
            return
        yield self._yield_state("preference_check", "success", f"Approved channels computed: {', '.join(approved_channels)}")
            
        # 3. Online Status Check
        yield self._yield_state("online_check", "processing", "Checking Redis for user online status...")
        self._delay(CONFIG["simulated_delay"]["online_check"])
        online_result = stages.online_status_checker(event, approved_channels, user_data)
        final_channels = online_result["channels"]
        reasons = " ".join(online_result["decisions"])
        yield self._yield_state("online_check", "success", f"Resolved endpoints: {', '.join(final_channels)}. {reasons}")
        
        if not final_channels:
             yield self._yield_state("online_check", "failed", "All channels suppressed dynamically.")
             return
             
        # 4. Publisher (Fanout)
        yield self._yield_state("publisher", "processing", f"Pub/Sub Fanning out to {len(final_channels)} queues...")
        self._delay(CONFIG["simulated_delay"]["fanout"])
        
        messages_to_process = []
        for channel in final_channels:
            msg_id = str(uuid.uuid4())
            q_msg = QueueMessage(message_id=msg_id, event_id=event.event_id, channel=channel, payload={"data": "..."})
            self.queues[channel].append(q_msg)
            messages_to_process.append(q_msg)
            
        yield self._yield_state("publisher", "success", "Messages successfully pushed to topic queues.")
        yield self._yield_state("queues", "info", "Queues populated", {"messages": [m.channel for m in messages_to_process]})

        # 5. Workers & Delivery
        for idx, q_msg in enumerate(messages_to_process):
            channel = q_msg.channel
            step_name = f"worker_{channel}"
            
            # Rate limiting simulation info
            limit = CONFIG["rate_limits_per_sec"].get(channel, 10)
            yield self._yield_state(step_name, "processing", f"Worker pulling from queue. Rate limit enforces max {limit}/sec.")
            self._delay(0.2)
            
            # Remove from queue visually
            if q_msg in self.queues[channel]:
                self.queues[channel].remove(q_msg)
                
            yield self._yield_state(step_name, "processing", f"Calling 3rd party {channel.upper()} provider...")
            self._delay(CONFIG["simulated_delay"]["worker_process"])
            
            # Simulate Success/Fail based on fail rate
            success = random.random() > self.fail_rate
            
            if success:
                yield self._yield_state(step_name, "success", f"Delivered {channel.upper()} successfully.")
            else:
                yield self._yield_state(step_name, "error", f"Delivery failed API Error (Simulated Outage).")
                
                # Retry logic
                retries = 0
                while retries < CONFIG["max_retries"] and not success:
                    retries += 1
                    backoff = CONFIG["base_backoff_seconds"] ** retries
                    yield self._yield_state(step_name, "error", f"Exponential backoff: Retrying {retries}/{CONFIG['max_retries']} in {backoff}s...")
                    
                    if not self.slow_mode:
                        time.sleep(min(1.0, backoff * 0.3)) # Visual delay
                    else:
                        time.sleep(1.5)
                        
                    success = random.random() > self.fail_rate
                    if success:
                        yield self._yield_state(step_name, "success", f"Delivered successfully on retry {retries}.")
                
                if not success:
                    yield self._yield_state(step_name, "failed", f"Max retries ({CONFIG['max_retries']}) exceeded. Moving to DLQ.")
                    q_msg.status = "dlq"
                    self.dlq.append(q_msg)
                    yield self._yield_state("dlq", "info", "DLQ count increased.")
                    
        yield self._yield_state("done", "info", "Simulation flow complete.")
