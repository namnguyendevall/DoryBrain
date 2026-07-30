import random

class Actor:
    """
    E009_Control: Isomorphic Control for E009 Planner.
    Capability: Depth-3 search tree but with a dummy clock-driven model.
    """
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        
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
        self.tick_count = 0
        
        # Fake estimated parameters from E008_Control
        self.fake_rest_gain = 0.0
        self.fake_work_cost = 0.0
        
    def get_state(self) -> dict:
        return {
            "estimated_rest_gain": self.fake_rest_gain,
            "estimated_work_cost": self.fake_work_cost,
            "used_prediction": self.used_prediction,
            "predicted_next_resource": self.predicted_next_resource,
            "search_nodes": self.search_nodes,
            "tie_break_count": self.tie_break_count,
            "u_term_contrib": self.u_term_contrib,
            "u_work_contrib": self.u_work_contrib
        }

    def choose(self, observation: dict) -> str:
        resource = observation.get('resource', 0)
        self.tick_count = observation.get('tick', 0)
        
        self.search_nodes = 0
        self.tie_break_count = 0
        self.u_term_contrib = 0.0
        self.u_work_contrib = 0.0
        
        # 1. Update Model (Dummy)
        # Fake cyclic parameter generation based on clock (like E008_Control)
        self.fake_rest_gain = 2.0 if (self.tick_count % 3 == 0) else 4.0
        self.fake_work_cost = 2.0 if (self.tick_count % 2 == 0) else 6.0
                    
        self.last_resource = resource
        
        # 2. Cold-start Exploration (Maintain identical phase to E009)
        if not self.rest_observed:
            self.last_action = 'rest'
            self.used_prediction = False
            self.rest_observed = True
            return 'rest'
            
        if not self.work_observed:
            self.last_action = 'work'
            self.used_prediction = False
            self.work_observed = True
            return 'work'
            
        # 3. Depth-3 Search Tree (Exactly 14 transitions evaluated)
        actions = ['rest', 'work']
        best_u = float('-inf')
        best_a1 = 'rest'
        best_pred = 0.0
        
        for a1 in actions:
            r1 = resource + self.fake_rest_gain if a1 == 'rest' else resource - self.fake_work_cost
            self.search_nodes += 1
            for a2 in actions:
                r2 = r1 + self.fake_rest_gain if a2 == 'rest' else r1 - self.fake_work_cost
                self.search_nodes += 1
                for a3 in actions:
                    r3 = r2 + self.fake_rest_gain if a3 == 'rest' else r2 - self.fake_work_cost
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
