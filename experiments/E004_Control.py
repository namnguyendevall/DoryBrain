import random

class Actor:
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        
    def choose(self, observation: dict) -> str:
        tick = observation.get("tick", 0)
        
        # Deterministic threshold schedule based on tick
        if tick % 20 < 10:
            threshold = 15
        else:
            threshold = 20
            
        if observation.get("resource", 0) < threshold:
            return "rest"
        return "work"
