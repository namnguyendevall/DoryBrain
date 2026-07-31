from .E017_Base import Actor as BaseActor

class Actor(BaseActor):
    def __init__(self, seed: int, beta: float = 100.0, keep_q: bool = False, keep_n: bool = False, keep_buffer: bool = False, decay_n: float = 1.0, decay_buffer: float = 1.0):
        super().__init__(seed=seed, beta=beta, keep_q=keep_q, keep_n=keep_n, keep_buffer=keep_buffer)
        self.decay_n = decay_n
        self.decay_buffer = decay_buffer
        
    def reset(self):
        """Reset the actor's episodic memory and counters, applying specific decay policies."""
        # Reset tick counters
        self.tick = 0
        self.last_state = None
        self.last_action = None
        
        # Reset tracked metrics for the new episode
        self.first_investment_tick = -1
        self.first_successful_replay_tick = -1
        self.max_resource_reached = 0.0
        self.time_above_50 = 0
        self.unique_causal_actions = set()
        self.replay_count = 0
        self.total_replay_age = 0
        self.candidate_actions = 0
        
        # Memory retention logic
        if not self.keep_q:
            self.Q = {}
            
        if not self.keep_n:
            self.N = {}
        elif self.decay_n < 1.0:
            for s in self.N:
                for a in self.N[s]:
                    self.N[s][a] *= self.decay_n
                
        if not self.keep_buffer:
            self.buffer = []
        elif self.decay_buffer < 1.0:
            retain_count = int(len(self.buffer) * self.decay_buffer)
            self.buffer = self.buffer[-retain_count:] if retain_count > 0 else []
            
