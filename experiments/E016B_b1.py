from .E016B_CountBonus import Actor as BaseActor
class Actor(BaseActor):
    def __init__(self, seed: int):
        super().__init__(seed=seed, batch_size=32, beta=1.0)
