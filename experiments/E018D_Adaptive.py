from .E018_Base import Actor as BaseActor
class Actor(BaseActor):
    def __init__(self, seed: int):
        super().__init__(seed=seed, keep_q=True, keep_n=True, keep_buffer=True, decay_n=0.99, decay_buffer=0.0)
