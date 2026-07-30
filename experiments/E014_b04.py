from experiments.E014 import Actor as E014Actor
class Actor(E014Actor):
    def __init__(self, seed: int):
        super().__init__(seed)
        self.batch_size = 4
