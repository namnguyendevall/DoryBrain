from .E016A_Optimistic import Actor as BaseActor
class Actor(BaseActor):
    def __init__(self, seed: int):
        super().__init__(seed=seed, batch_size=32)
