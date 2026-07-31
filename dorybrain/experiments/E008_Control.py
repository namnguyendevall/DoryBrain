import random

class Actor:
    """
    E008_Control: Isomorphic Control for Predictive Model.
    Uses the exact same state updates and prediction steps, but the inputs to the 
    EWMA updates are replaced by clock-generated fake observations.
    """
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.alpha = 0.2
        
        self.estimated_rest_gain = 0.0
        self.estimated_work_cost = 0.0
        
        self.rest_observed = False
        self.work_observed = False
        
        self.last_action = None
        self.last_resource = None
        
        # Diagnostics
        self.used_prediction = False
        self.predicted_next_resource = 0.0
        
        self.tick = 0

    def get_state(self) -> dict:
        return {
            "estimated_rest_gain": self.estimated_rest_gain,
            "estimated_work_cost": self.estimated_work_cost,
            "used_prediction": self.used_prediction,
            "predicted_next_resource": self.predicted_next_resource
        }

    def choose(self, observation: dict) -> str:
        resource = observation.get('resource', 0)
        self.tick += 1
        
        # Clock-generated fake observations
        fake_rest_gain = 5.0 if (self.tick // 20) % 2 == 0 else 1.0
        fake_work_cost = 2.0 if (self.tick // 20) % 2 == 1 else 6.0
        
        # 1. Update Model (Learning Rule using FAKE observations)
        if self.last_resource is not None and self.last_action is not None:
            if self.last_action == 'rest':
                if not self.rest_observed:
                    self.estimated_rest_gain = fake_rest_gain
                    self.rest_observed = True
                else:
                    self.estimated_rest_gain = self.alpha * fake_rest_gain + (1 - self.alpha) * self.estimated_rest_gain
            elif self.last_action == 'work':
                if not self.work_observed:
                    self.estimated_work_cost = fake_work_cost
                    self.work_observed = True
                else:
                    self.estimated_work_cost = self.alpha * fake_work_cost + (1 - self.alpha) * self.estimated_work_cost
                    
        self.last_resource = resource
        
        # 2. Cold-start Exploration
        if not self.rest_observed:
            self.last_action = 'rest'
            self.used_prediction = False
            return 'rest'
            
        if not self.work_observed:
            self.last_action = 'work'
            self.used_prediction = False
            return 'work'
            
        # 3. One-step Prediction
        pred_rest = resource + self.estimated_rest_gain
        pred_work = resource - self.estimated_work_cost
        
        # 4. Utility Decision
        # Utility(action) = -INF if predicted_resource < 0 else predicted_resource + bonus
        work_bonus = 10.0
        
        u_rest = float('-inf') if pred_rest <= 0 else pred_rest
        u_work = float('-inf') if pred_work <= 0 else pred_work + work_bonus
        
        self.used_prediction = True
        
        if u_work > u_rest:
            chosen = 'work'
            self.predicted_next_resource = pred_work
        else:
            chosen = 'rest'
            self.predicted_next_resource = pred_rest
            
        self.last_action = chosen
        return chosen
