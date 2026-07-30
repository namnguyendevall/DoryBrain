from .E015_Replay import Actor as BaseActor
class Actor(BaseActor):
    def __init__(self, seed: int):
        super().__init__(seed=seed, batch_size=0)
