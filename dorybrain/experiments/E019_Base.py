from .E018_Base import Actor as BaseActor
from infrastructure.evolution.genome import CognitiveGenome

class Actor(BaseActor):
    def __init__(self, seed: int, genome: CognitiveGenome = None):
        # We always keep Q, N, and Buffer, but apply decay based on genome
        super().__init__(
            seed=seed, 
            beta=genome.beta if genome else 100.0, 
            keep_q=True, 
            keep_n=True, 
            keep_buffer=True, 
            decay_n=genome.memory_decay_rate if genome else 0.99,
            decay_buffer=0.0 # Handled in reset override if needed, or by maxlen
        )
        self.genome = genome if genome else CognitiveGenome()
        self.alpha = self.genome.alpha
        self.gamma = self.genome.gamma
        
        # Override buffer maxlen based on capacity
        from collections import deque
        self.buffer = deque(maxlen=self.genome.replay_capacity)
        
    def reset(self):
        super().reset()
        # In Adaptive memory, replay buffer is usually cleared or kept small across lifetimes
        # We will keep the newest 10% of the buffer as our "decay" for replay,
        # or we could clear it completely. E018D decays replay priority.
        # For simplicity, we just keep the newest capacity transitions.
        # But wait, capacity limits the buffer overall.
        pass
        
    def choose(self, observation):
        # Epsilon or Count bonus exploration
        # (This uses the parent's count bonus logic with self.beta)
        return super().choose(observation)
        
    def update(self, s, a, r, s_prime):
        # Override standard Q update to use genome.alpha and genome.gamma
        if s not in self.Q:
            self.Q[s] = {act: 0.0 for act in self.all_actions}
            
        if s_prime not in self.Q:
            self.Q[s_prime] = {act: 0.0 for act in self.all_actions}
            
        best_next = max(self.Q[s_prime].values())
        target = r + self.gamma * best_next
        self.Q[s][a] = self.Q[s][a] + self.alpha * (target - self.Q[s][a])
