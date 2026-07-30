import random

class Actor:
    """
    E009: Depth-Limited Planner.
    Capability: Learns local transition model and evaluates depth-3 sequences.
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
        self.search_nodes = 0
        self.tie_break_count = 0
        self.u_term_contrib = 0.0
        self.u_work_contrib = 0.0
        
    def get_state(self) -> dict:
        return {
            "estimated_rest_gain": self.estimated_rest_gain,
            "estimated_work_cost": self.estimated_work_cost,
            "used_prediction": self.used_prediction,
            "predicted_next_resource": self.predicted_next_resource,
            "search_nodes": self.search_nodes,
            "tie_break_count": self.tie_break_count,
            "u_term_contrib": self.u_term_contrib,
            "u_work_contrib": self.u_work_contrib
        }

    def choose(self, observation: dict) -> str:
        resource = observation.get('resource', 0)
        
        self.search_nodes = 0
        self.tie_break_count = 0
        self.u_term_contrib = 0.0
        self.u_work_contrib = 0.0
        
        # 1. Update Model (ONLY ON REAL EXPERIENCE)
        if self.last_resource is not None and self.last_action is not None:
            if self.last_action == 'rest':
                gain = resource - self.last_resource
                if not self.rest_observed:
                    self.estimated_rest_gain = gain
                    self.rest_observed = True
                else:
                    self.estimated_rest_gain = self.alpha * gain + (1 - self.alpha) * self.estimated_rest_gain
            elif self.last_action == 'work':
                cost = self.last_resource - resource
                if not self.work_observed:
                    self.estimated_work_cost = cost
                    self.work_observed = True
                else:
                    self.estimated_work_cost = self.alpha * cost + (1 - self.alpha) * self.estimated_work_cost
                    
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
            
        # 3. Depth-3 Search Tree (Exactly 14 transitions evaluated)
        actions = ['rest', 'work']
        best_u = float('-inf')
        best_a1 = 'rest'
        best_pred = 0.0
        
        for a1 in actions:
            r1 = resource + self.estimated_rest_gain if a1 == 'rest' else resource - self.estimated_work_cost
            self.search_nodes += 1
            for a2 in actions:
                r2 = r1 + self.estimated_rest_gain if a2 == 'rest' else r1 - self.estimated_work_cost
                self.search_nodes += 1
                for a3 in actions:
                    r3 = r2 + self.estimated_rest_gain if a3 == 'rest' else r2 - self.estimated_work_cost
                    self.search_nodes += 1
                    
                    if r1 <= 0 or r2 <= 0 or r3 <= 0:
                        u = float('-inf')
                    else:
                        num_work = (1 if a1=='work' else 0) + (1 if a2=='work' else 0) + (1 if a3=='work' else 0)
                        u = r3 + 10.0 * num_work
                        
                    if u > best_u:
                        best_u = u
                        best_a1 = a1
                        best_pred = r1
                        if u != float('-inf'):
                            self.u_term_contrib = r3
                            self.u_work_contrib = 10.0 * num_work
                    elif u == best_u and u != float('-inf'):
                        self.tie_break_count += 1

        self.used_prediction = True
        self.predicted_next_resource = best_pred
        self.last_action = best_a1
        return best_a1
