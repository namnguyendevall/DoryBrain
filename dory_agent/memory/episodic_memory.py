from typing import List, Dict, Any
from dory_agent.core.contracts import Event

class EpisodicMemory:
    """
    Stores the sequence of events and actions that have just occurred in the current session.
    Provides a short-term chronological history for the Planner to understand 'what just happened'.
    """
    def __init__(self):
        self.episodes: List[Event] = []
        
    def add_event(self, event: Event):
        self.episodes.append(event)
        
    def get_recent_events(self, limit: int = 10) -> List[Event]:
        return self.episodes[-limit:]
        
    def clear(self):
        self.episodes.clear()
