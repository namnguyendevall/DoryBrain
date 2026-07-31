import random

class Actor:
    """
    Isomorphic Control for Continuous Latent State Estimator.
    Same continuous state update mechanism, but driven by a deterministic pseudo-trend.
    """
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.alpha = 0.2
        self.estimated_delta = 0.0
        self.tick = 0

    def get_state(self) -> dict:
        return {
            "estimated_delta": self.estimated_delta
        }

    def choose(self, observation: dict) -> str:
        resource = observation.get('resource', 0)
        
        # 1. Update continuous latent state with pseudo-trend
        # Pseudo-trend: +1 for 50 ticks, -1 for 50 ticks
        if (self.tick // 50) % 2 == 0:
            pseudo_delta = 1.0
        else:
            pseudo_delta = -1.0
            
        self.estimated_delta = (self.alpha * pseudo_delta) + ((1 - self.alpha) * self.estimated_delta)
        self.tick += 1
        
        # 2. Base policy with preference override
        base_threshold = 20
        buffer = 5 if self.estimated_delta < 0 else 0
        effective_threshold = base_threshold + buffer

        # 3. Action Logic
        if resource >= effective_threshold:
            return 'work'
        return 'rest'
