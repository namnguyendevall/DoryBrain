import queue
from typing import Dict, Any, List
from dory_agent.kernel.contracts import Goal

class Scheduler:
    """
    A FIFO queue for managing goals and background tasks.
    In the future, this can be expanded to support priorities, cron jobs,
    or multi-agent queues without changing the Runtime's core loop.
    """
    def __init__(self):
        self._goal_queue = queue.Queue()
        
    def submit_goal(self, goal: Goal):
        """Enqueue a new goal."""
        self._goal_queue.put(goal)
        
    def next_goal(self) -> Goal:
        """Get the next goal in the FIFO queue (blocks if empty)."""
        return self._goal_queue.get()
        
    def has_pending_goals(self) -> bool:
        """Check if there are goals waiting."""
        return not self._goal_queue.empty()
