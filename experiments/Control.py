import random

class Actor:
    def __init__(self, seed: int):
        self.rng = random.Random(seed)

    def choose(self, observation: dict) -> str:
        return self.rng.choice(["rest", "work"])
