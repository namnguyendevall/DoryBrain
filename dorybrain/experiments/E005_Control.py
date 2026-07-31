import random

class Actor:
    """
    Isomorphic Control for Finite-State Controller.
    Same states and transition complexity, but transitions are semantic-free (clock-driven).
    """
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.state = "NORMAL"
        self.tick = 0

    def get_state(self) -> dict:
        return {
            "mode": self.state
        }

    def choose(self, observation: dict) -> str:
        resource = observation.get('resource', 0)
        
        # Clock-driven state transitions (Semantic-free)
        # NORMAL (10 ticks) -> STARVING (5 ticks) -> RECOVERING (10 ticks)
        cycle_tick = self.tick % 25
        if cycle_tick == 0:
            self.state = "NORMAL"
        elif cycle_tick == 10:
            self.state = "STARVING"
        elif cycle_tick == 15:
            self.state = "RECOVERING"

        # Action Logic based on state (identical to E005)
        action = 'rest'
        if self.state == "NORMAL":
            if resource >= 20:
                action = 'work'
        elif self.state == "STARVING":
            if resource >= 15:
                action = 'work'
        elif self.state == "RECOVERING":
            # Force rest until recovered
            action = 'rest'
            
        self.tick += 1
        return action
