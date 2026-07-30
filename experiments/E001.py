"""
Experiment E001: Threshold 30 Actor.
Actor: Works unless Resource < 30.
"""

class Actor:
    def __init__(self, seed: int):
        pass

    def choose(self, observation: dict) -> str:
        if observation.get("resource", 0) < 30:
            return "rest"
        return "work"
