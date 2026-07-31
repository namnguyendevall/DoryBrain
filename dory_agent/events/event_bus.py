import logging
from typing import Callable, List, Dict
from dory_agent.core.contracts import Event, EventType
from dory_agent.events.event_store import EventStore

# A subscriber is a function that takes an Event
Subscriber = Callable[[Event], None]

class EventBus:
    """
    Central Nervous System for the Agent Runtime.
    Responsible ONLY for broadcasting events to subscribers.
    Does NOT store events itself (that is EventStore's job).
    """
    def __init__(self, store: EventStore):
        self._subscribers: Dict[EventType, List[Subscriber]] = {
            evt: [] for evt in EventType
        }
        self._global_subscribers: List[Subscriber] = []
        
        # The Store is always a global subscriber
        self.subscribe_global(store.append)

    def subscribe(self, event_type: EventType, subscriber: Subscriber):
        """Subscribe to a specific event type."""
        if subscriber not in self._subscribers[event_type]:
            self._subscribers[event_type].append(subscriber)

    def subscribe_global(self, subscriber: Subscriber):
        """Subscribe to ALL events."""
        if subscriber not in self._global_subscribers:
            self._global_subscribers.append(subscriber)

    def publish(self, event: Event):
        """
        Broadcast the event to all relevant subscribers.
        """
        # 1. Global subscribers (e.g. EventStore, global loggers, UI)
        for sub in self._global_subscribers:
            try:
                sub(event)
            except Exception as e:
                logging.error(f"Global subscriber {sub} failed on event {event.event_id}: {e}")
                
        # 2. Specific subscribers (e.g. Memory updating on STEP_STARTED)
        for sub in self._subscribers.get(event.event_type, []):
            try:
                sub(event)
            except Exception as e:
                logging.error(f"Subscriber {sub} failed on event {event.event_id}: {e}")
