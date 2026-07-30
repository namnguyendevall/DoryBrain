import random

class Actor:
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.ticks_since_last_work = 0
        self.mode = "normal"
        self.threshold = 20
        
    def get_state(self) -> dict:
        return {
            "mode": self.mode,
            "ticks_since_last_work": self.ticks_since_last_work
        }

    def choose(self, observation: dict) -> str:
        last_action = observation.get("last_action")
        
        if last_action is not None:
            if last_action == "work":
                self.ticks_since_last_work = 0
            else:
                self.ticks_since_last_work += 1
                
        if self.ticks_since_last_work >= 10:
            self.mode = "starving"
            self.threshold = 15
        else:
            self.mode = "normal"
            self.threshold = 20
            
        if observation.get("resource", 0) < self.threshold:
            return "rest"
        return "work"
