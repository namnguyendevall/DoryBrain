import random

class Actor:
    """
    Continuous Latent State Estimator (EWMA).
    Capability: Continuous filtering (EWMA) of environmental trend.
    """
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.alpha = 0.2
        self.estimated_delta = 0.0
        self.last_resource = None

    def get_state(self) -> dict:
        return {
            "estimated_delta": self.estimated_delta
        }

    def choose(self, observation: dict) -> str:
        resource = observation.get('resource', 0)
        
        # 1. Update continuous latent state
        if self.last_resource is not None:
            current_delta = resource - self.last_resource
            self.estimated_delta = (self.alpha * current_delta) + ((1 - self.alpha) * self.estimated_delta)
        self.last_resource = resource
        
        # 2. Base policy with preference override
        base_threshold = 20
        buffer = 5 if self.estimated_delta < 0 else 0
        effective_threshold = base_threshold + buffer

        # 3. Action Logic
        if resource >= effective_threshold:
            return 'work'
        return 'rest'
