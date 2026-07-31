from .E018_Base import Actor as BaseActor
class Actor(BaseActor):
    def __init__(self, seed: int):
        super().__init__(seed=seed, keep_q=False, keep_n=False, keep_buffer=False)
