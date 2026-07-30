import random

class Actor:
    """
    Finite-State Controller with Hysteresis.
    """
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.state = "NORMAL"
        self.ticks_since_last_work = 0

    def get_state(self) -> dict:
        return {
            "mode": self.state,
            "ticks_since_last_work": self.ticks_since_last_work
        }

    def choose(self, observation: dict) -> str:
        resource = observation.get('resource', 0)
        last_action = observation.get("last_action")
        last_action_successful = observation.get("last_action_successful")
        
        # 1. Update internal state based on observation
        if last_action is not None:
            if last_action == 'work':
                if last_action_successful:
                    self.ticks_since_last_work = 0
                else:
                    self.ticks_since_last_work += 1
            else:
                self.ticks_since_last_work += 1
        
        # 2. State Transitions
        if self.state == "NORMAL":
            if self.ticks_since_last_work >= 10:
                self.state = "STARVING"
        elif self.state == "STARVING":
            if last_action == 'work' and last_action_successful:
                self.state = "RECOVERING"
        elif self.state == "RECOVERING":
            if resource >= 25:
                self.state = "NORMAL"

        # 3. Action Logic based on state (Hysteresis)
        action = 'rest'
        if self.state == "NORMAL":
            if resource >= 20:
                action = 'work'
        elif self.state == "STARVING":
            if resource >= 15:
                action = 'work'
        elif self.state == "RECOVERING":
            # Force rest until recovered (threshold 25)
            action = 'rest'

        return action
