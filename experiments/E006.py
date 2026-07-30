import random
from collections import deque

class Actor:
    """
    Finite-History Controller (Sliding Window Memory).
    Capability: Aggregation over a sliding window of recent time.
    """
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.window_size = 10
        self.history = deque(maxlen=self.window_size)
        # Pre-fill history assuming we haven't worked yet
        for _ in range(self.window_size):
            self.history.append(0)
            
        self.mode = "normal"

    def get_state(self) -> dict:
        return {
            "mode": self.mode,
            "work_density": sum(self.history)
        }

    def choose(self, observation: dict) -> str:
        resource = observation.get('resource', 0)
        last_action = observation.get("last_action")
        last_action_successful = observation.get("last_action_successful")
        
        # 1. Update internal history window based on the LAST tick's outcome
        if last_action is not None:
            if last_action == 'work' and last_action_successful:
                self.history.append(1)
            else:
                self.history.append(0)
        
        # 2. Decision Logic based on Work Density
        work_density = sum(self.history)
        
        if work_density == 0:
            self.mode = "starving" # Low threshold
            threshold = 15
        else:
            self.mode = "normal"
            threshold = 20

        # 3. Action Logic
        if resource >= threshold:
            return 'work'
        return 'rest'
