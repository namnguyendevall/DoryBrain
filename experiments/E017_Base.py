from .E016B_CountBonus import Actor as BaseActor

class Actor(BaseActor):
    def __init__(self, seed: int, beta: float = 100.0, keep_q: bool = False, keep_n: bool = False, keep_buffer: bool = False):
        super().__init__(seed=seed, batch_size=32, beta=beta)
        self.keep_q = keep_q
        self.keep_n = keep_n
        self.keep_buffer = keep_buffer
        
    def reset(self):
        """Reset the actor's episodic memory and counters, but selectively preserve core memory."""
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
            
        if not self.keep_buffer:
            self.buffer = []
            
    # Override get_state to make sure time_above_50 works
    def get_state(self):
        # same as E016B but correctly referencing local episodic vars if needed
        state = super().get_state()
        return state
