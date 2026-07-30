import random

class Actor:
    """
    E010: Reactive Storage Policy.
    Capability: Uses Action Expansion (STORE/RETRIEVE) to manage hidden resources.
    """
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        
    def get_state(self) -> dict:
        return {}

    def choose(self, observation: dict) -> str:
        resource = observation.get('resource', 0)
        bank = observation.get('bank', 0.0)
        
        # Policy: Reactive storage logic
        if resource > 50:
            return 'store'
        elif resource < 15 and bank > 0:
            return 'retrieve'
        else:
            # Baseline E000 behavior
            if resource > 20:
                return 'work'
            else:
                return 'rest'
