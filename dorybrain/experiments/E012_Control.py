import random

class Actor:
    """
    E012_Control: Causal Planner Control
    Searches at Depth 5 over ['rest', 'work', 'invest_gain', 'invest_decay']
    BUT simulates investments as having NO CAUSAL EFFECT (dummy actions).
    """
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.alpha = 0.2
        
        self.estimated_base_rest_gain = 0.0
        self.estimated_base_work_cost = 0.0
        
        self.rest_observed = False
        self.work_observed = False
        
        self.last_action = None
        self.last_resource = None
        
        self.search_nodes = 0
        self.tie_break_count = 0
        
        self.action_priority = {
            'rest': 3,
            'invest_gain': 2,
            'invest_decay': 1,
            'work': 0
        }
        
    def get_state(self) -> dict:
        return {
            "estimated_rest_gain": self.estimated_base_rest_gain,
            "estimated_work_cost": self.estimated_base_work_cost,
            "search_nodes": self.search_nodes,
            "tie_break_count": self.tie_break_count
        }

    def choose(self, observation: dict) -> str:
        resource = observation.get('resource', 0)
        invest_gain_count = observation.get('invest_gain_count', 0)
        invest_decay_count = observation.get('invest_decay_count', 0)
        
        self.search_nodes = 0
        self.tie_break_count = 0
        
        # 1. Update Model
        if self.last_resource is not None and self.last_action is not None:
            if self.last_action == 'rest':
                actual_diff = resource - self.last_resource
                current_gain_bonus = invest_gain_count * 0.5
                current_decay_reduction = invest_decay_count * 0.5
                base_diff = actual_diff - current_gain_bonus - current_decay_reduction
                
                if not self.rest_observed:
                    self.estimated_base_rest_gain = base_diff
                    self.rest_observed = True
                else:
                    self.estimated_base_rest_gain = self.alpha * base_diff + (1 - self.alpha) * self.estimated_base_rest_gain
                    
            elif self.last_action == 'work':
                actual_drop = self.last_resource - resource
                current_decay_reduction = invest_decay_count * 0.5
                base_drop = actual_drop + current_decay_reduction
                
                if not self.work_observed:
                    self.estimated_base_work_cost = base_drop
                    self.work_observed = True
                else:
                    self.estimated_base_work_cost = self.alpha * base_drop + (1 - self.alpha) * self.estimated_base_work_cost

        self.last_resource = resource
        
        # 2. Cold-start Exploration
        if not self.rest_observed:
            self.last_action = 'rest'
            return 'rest'
        if not self.work_observed:
            self.last_action = 'work'
            return 'work'
            
        # 3. Depth-5 Search
        best_u = float('-inf')
        best_a1 = 'rest'
        best_a1_priority = -1
        
        actions = ['rest', 'work', 'invest_gain', 'invest_decay']
        
        def simulate(a, r, ig, idc):
            # NO CAUSAL KNOWLEDGE (dummy actions, 0 effect)
            node_gain_bonus = ig * 0.0
            node_decay_reduction = idc * 0.0
            
            new_ig = ig
            new_idc = idc
            
            if a == 'rest':
                dr = self.estimated_base_rest_gain + node_gain_bonus + node_decay_reduction
                new_r = min(100.0, r + dr)
            elif a == 'work':
                dr = -self.estimated_base_work_cost + node_decay_reduction
                new_r = r + dr
            elif a == 'invest_gain':
                if r < 30.0 or ig >= 2:
                    return -1.0, new_ig, new_idc # invalid
                dr = -30.0 + node_decay_reduction
                new_r = r + dr
                new_ig += 1
            elif a == 'invest_decay':
                if r < 30.0 or idc >= 2:
                    return -1.0, new_ig, new_idc # invalid
                dr = -30.0 + node_decay_reduction
                new_r = r + dr
                new_idc += 1
                
            return new_r, new_ig, new_idc

        for a1 in actions:
            r1, ig1, idc1 = simulate(a1, resource, invest_gain_count, invest_decay_count)
            self.search_nodes += 1
            if r1 <= 0: continue
            
            for a2 in actions:
                r2, ig2, idc2 = simulate(a2, r1, ig1, idc1)
                self.search_nodes += 1
                if r2 <= 0: continue
                
                for a3 in actions:
                    r3, ig3, idc3 = simulate(a3, r2, ig2, idc2)
                    self.search_nodes += 1
                    if r3 <= 0: continue
                    
                    for a4 in actions:
                        r4, ig4, idc4 = simulate(a4, r3, ig3, idc3)
                        self.search_nodes += 1
                        if r4 <= 0: continue
                        
                        for a5 in actions:
                            r5, ig5, idc5 = simulate(a5, r4, ig4, idc4)
                            self.search_nodes += 1
                            if r5 <= 0: continue
                            
                            num_work = (1 if a1=='work' else 0) + (1 if a2=='work' else 0) + (1 if a3=='work' else 0) + (1 if a4=='work' else 0) + (1 if a5=='work' else 0)
                            u = r5 + 10.0 * num_work
                            
                            if u > best_u:
                                best_u = u
                                best_a1 = a1
                                best_a1_priority = self.action_priority[a1]
                            elif u == best_u:
                                self.tie_break_count += 1
                                if self.action_priority[a1] > best_a1_priority:
                                    best_a1 = a1
                                    best_a1_priority = self.action_priority[a1]
                                    
        if best_u == float('-inf'):
            # Fallback if all paths lead to death
            best_a1 = 'rest'
            
        self.last_action = best_a1
        return best_a1
