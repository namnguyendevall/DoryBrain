"""
Experiment E000: Threshold Actor.
Actor: Works unless Resource < 20.
"""

class Actor:
    def __init__(self, seed: int):
        pass

    def choose(self, observation: dict) -> str:
        if observation.get("resource", 0) < 20:
            return "rest"
        return "work"
