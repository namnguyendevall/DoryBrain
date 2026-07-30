import random

class CognitiveGenome:
    def __init__(self, alpha=None, gamma=None, beta=None, memory_decay_rate=None, replay_capacity=None, replay_frequency=None, policy_genes=None):
        # Initialize randomly if not provided
        self.alpha = alpha if alpha is not None else random.uniform(0.01, 1.0)
        self.gamma = gamma if gamma is not None else random.uniform(0.8, 0.999)
        self.beta = beta if beta is not None else random.uniform(0, 500)
        self.memory_decay_rate = memory_decay_rate if memory_decay_rate is not None else random.uniform(0.90, 1.0)
        self.replay_capacity = replay_capacity if replay_capacity is not None else random.randint(100, 10000)
        self.replay_frequency = replay_frequency if replay_frequency is not None else random.randint(1, 128)
        self.policy_genes = policy_genes if policy_genes is not None else {}
        
    def to_dict(self):
        return {
            "alpha": self.alpha,
            "gamma": self.gamma,
            "beta": self.beta,
            "memory_decay_rate": self.memory_decay_rate,
            "replay_capacity": self.replay_capacity,
            "replay_frequency": self.replay_frequency,
            "policy_genes": self.policy_genes
        }
        
    def mutate(self):
        # Determine if we mutate (base probability 1.0 for these continuous variables)
        # We enforce a floor mutation rate / variance by ensuring sigma doesn't collapse.
        
        # Alpha: sigma = max(0.01, 0.1 * alpha), bounds = [0.01, 1.0]
        sigma_alpha = max(0.01, 0.1 * self.alpha)
        self.alpha = max(0.01, min(1.0, random.gauss(self.alpha, sigma_alpha)))
        
        # Gamma: sigma = 0.02, bounds = [0.8, 0.999]
        self.gamma = max(0.8, min(0.999, random.gauss(self.gamma, 0.02)))
        
        # Beta: sigma = max(5.0, 0.15 * beta), bounds = [0, 500]
        sigma_beta = max(5.0, 0.15 * self.beta)
        self.beta = max(0, min(500, random.gauss(self.beta, sigma_beta)))
        
        # Memory Decay: sigma = 0.005, bounds = [0.90, 1.0]
        self.memory_decay_rate = max(0.90, min(1.0, random.gauss(self.memory_decay_rate, 0.005)))
        
        # Replay Capacity: integer step (std = 5% of capacity, min 50), bounds = [100, 10000]
        sigma_rc = max(50, int(0.05 * self.replay_capacity))
        self.replay_capacity = max(100, min(10000, int(random.gauss(self.replay_capacity, sigma_rc))))
        
        # Replay Frequency: integer step (std = 2), bounds = [1, 128]
        self.replay_frequency = max(1, min(128, int(random.gauss(self.replay_frequency, 2))))
        
        # Mutate policy genes (used only by E019B)
        # small gaussian noise to policy logits
        for k in self.policy_genes:
            self.policy_genes[k] += random.gauss(0, 0.1)
            
        return self
        
    def clone(self):
        return CognitiveGenome(
            alpha=self.alpha,
            gamma=self.gamma,
            beta=self.beta,
            memory_decay_rate=self.memory_decay_rate,
            replay_capacity=self.replay_capacity,
            replay_frequency=self.replay_frequency,
            policy_genes=dict(self.policy_genes)
        )
