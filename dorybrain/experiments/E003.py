import random

"""
Experiment E003: Probabilistic Actor
Actor: If resource < 20, 90% chance to rest, 10% chance to work. Otherwise work.
"""

class Actor:
    def __init__(self, seed: int):
        self.rng = random.Random(seed)

    def choose(self, observation: dict) -> str:
        if observation.get("resource", 0) < 20:
            if self.rng.random() < 0.90:
                return "rest"
            return "work"
        return "work"
