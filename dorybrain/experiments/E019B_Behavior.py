import random
from .E017_Base import Actor as BaseActor
from infrastructure.evolution.genome import CognitiveGenome

class Actor(BaseActor):
    def __init__(self, seed: int, genome: CognitiveGenome = None):
        # We don't really care about beta, keep_q, etc. for pure behavior evolution
        # But we inherit to keep the tracking metrics
        super().__init__(
            seed=seed, 
            beta=0, 
            keep_q=True, 
            keep_n=True, 
            keep_buffer=True
        )
        self.genome = genome if genome else CognitiveGenome()
        self.rng = random.Random(seed)
        self.time_above_50 = 0
        self.first_investment_tick = -1
        
    def reset(self):
        super().reset()
        self.time_above_50 = 0
        self.first_investment_tick = -1
        
        # We assume policy_genes maps state string to action probabilities
        
    def choose(self, observation):
        self.tick += 1
        current_resource = observation.get("resource", 0.0)
        
        # Track metrics
        if current_resource > 50.0:
            self.time_above_50 += 1
            
        s = str(current_resource) # Simplify state to just resource for policy
        
        # If we haven't seen this state in the genome's policy, add random logits
        if s not in self.genome.policy_genes:
            self.genome.policy_genes[s] = {act: self.rng.gauss(0, 1) for act in self.all_actions}
            
        logits = self.genome.policy_genes[s]
        
        # Softmax selection
        import math
        exp_logits = {act: math.exp(min(val, 700)) for act, val in logits.items()} # cap to prevent overflow
        total_exp = sum(exp_logits.values())
        
        rand_val = self.rng.random() * total_exp
        cumulative = 0.0
        best_action = self.all_actions[0]
        for act, p in exp_logits.items():
            cumulative += p
            if rand_val <= cumulative:
                best_action = act
                break
                
        # Track investment
        if best_action in ['invest_gain', 'invest_decay']:
            if self.first_investment_tick == -1:
                self.first_investment_tick = self.tick
                
        return best_action
        
    def update(self, s, a, r, s_prime):
        # E019B doesn't learn from experience in its lifetime,
        # but we accumulate fitness if needed.
        pass
        
    def get_state(self):
        return {
            "first_investment_tick": getattr(self, 'first_investment_tick', -1),
            "time_above_50": getattr(self, 'time_above_50', 0)
        }
