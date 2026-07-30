"""
Experiment E002: Periodic Actor (WWRR)
Actor: Works for 2 ticks, Rests for 2 ticks, ignoring resource level.
"""

class Actor:
    def __init__(self, seed: int):
        pass

    def choose(self, observation: dict) -> str:
        tick = observation.get("tick", 1)
        # tick is 1-indexed. tick 1, 2 -> work. tick 3, 4 -> rest.
        if (tick - 1) % 4 < 2:
            return "work"
        return "rest"
