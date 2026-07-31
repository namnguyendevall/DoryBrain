from experiments.E014 import Actor as E014Actor

class Actor(E014Actor):
    """
    E014_Control: Online-only Agent (Physics-Constrained Exploration Protocol)
    Capability: Online Tabular Q-learning
    Mechanism: Collects experience into buffer but batch_size = 0 (no replay)
    """
    def __init__(self, seed: int):
        super().__init__(seed)
        self.batch_size = 0
