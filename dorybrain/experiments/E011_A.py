import random

class Actor:
    """
    E011_A: Environment Modification (Invest Gain)
    """
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        
    def get_state(self) -> dict:
        return {}

    def choose(self, observation: dict) -> str:
        resource = observation.get('resource', 0)
        invest_count = observation.get('invest_gain_count', 0)
        
        # Save up to invest first
        if invest_count < 2:
            if resource >= 32:
                return 'invest_gain'
            else:
                return 'rest'
            
        # Baseline E000 behavior after max investment
        if resource > 20:
            return 'work'
        else:
            return 'rest'
