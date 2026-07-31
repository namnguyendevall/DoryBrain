import random

class Actor:
    """
    E011_B: Environment Modification (Invest Decay)
    """
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        
    def get_state(self) -> dict:
        return {}

    def choose(self, observation: dict) -> str:
        resource = observation.get('resource', 0)
        invest_count = observation.get('invest_decay_count', 0)
        
        # Save up to invest first
        if invest_count < 2:
            if resource >= 32:
                return 'invest_decay'
            else:
                return 'rest'
            
        # Baseline E000 behavior after max investment
        if resource > 20:
            return 'work'
        else:
            return 'rest'
