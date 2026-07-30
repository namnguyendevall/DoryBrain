import random

class Actor:
    """
    E010_Control: Clock Storage Policy.
    Capability: Has access to STORE/RETRIEVE but triggers them based on clock, ignoring resource state.
    """
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        
    def get_state(self) -> dict:
        return {}

    def choose(self, observation: dict) -> str:
        tick = observation.get('tick', 0)
        resource = observation.get('resource', 0)
        
        cycle = tick % 20
        
        if cycle < 5:
            return 'store'
        elif cycle >= 15:
            return 'retrieve'
        else:
            # Baseline E000 behavior
            if resource > 20:
                return 'work'
            else:
                return 'rest'
