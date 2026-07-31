import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dory_agent.kernel.contracts import Event, EventType

class EventStore:
    """
    Append-only log for all system events.
    Responsible for persisting events for later replay, debugging, or DoryBrain training.
    """
    def __init__(self, log_file: Optional[str] = None):
        self._events: List[Event] = []
        self._log_file = log_file

    def append(self, event: Event):
        self._events.append(event)
        
        # In a real enterprise system, this might write to SQLite, Kafka, or a JSONL file
        if self._log_file:
            self._persist_to_file(event)
            
    def _persist_to_file(self, event: Event):
        try:
            with open(self._log_file, "a", encoding="utf-8") as f:
                # Serialize enum and datetime
                f.write(event.model_dump_json() + "\n")
        except Exception as e:
            logging.error(f"Failed to persist event to {self._log_file}: {e}")

    def get_all(self) -> List[Event]:
        return self._events.copy()
    
    def get_by_goal(self, goal_id: str) -> List[Event]:
        """Filter events related to a specific goal/session."""
        return [e for e in self._events if e.payload.get("goal_id") == goal_id]
