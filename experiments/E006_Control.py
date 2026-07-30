import random
from collections import deque

class Actor:
    """
    Isomorphic Control for Finite-History Controller.
    Same history queue complexity, but filled with a deterministic clock.
    """
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.window_size = 10
        self.history = deque(maxlen=self.window_size)
        self.tick = 0
        
        # Pre-fill history to match E006
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
        
        # 1. Update internal history window based on deterministic clock
        # Pushes 1 for 2 ticks, then 0 for 8 ticks, repeating.
        if self.tick % 10 < 2:
            self.history.append(1)
        else:
            self.history.append(0)
            
        self.tick += 1
        
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
