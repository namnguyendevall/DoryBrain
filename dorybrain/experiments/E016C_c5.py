from .E016C_UCB import Actor as BaseActor
class Actor(BaseActor):
    def __init__(self, seed: int):
        super().__init__(seed=seed, batch_size=32, c=5.0)
