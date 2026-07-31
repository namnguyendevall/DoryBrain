import random

class Actor:
    """
    E013_Control: TD-Learning (Q-Lambda) Planner Control
    Actions 'invest_gain' and 'invest_decay' are mapped to dummy actions in the environment.
    They cost 30 resources and increment the counter, but provide NO physics change.
    """
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        
        self.Q = {}
        self.E = {}
        
        self.alpha = 0.1
        self.gamma = 0.99
        self.lambd = 0.8
        
        self.actions = ['rest', 'work', 'invest_gain', 'invest_decay']
        
        self.tick = 0
        
        self.last_state = None
        self.last_action = None
        self.last_resource = None
        
        self.unique_causal_actions_explored = set()
        self.first_investment_tick = -1
        
    def _get_bin(self, resource):
        if resource < 5: return 0
        if resource < 10: return 1
        return min(10, int(resource // 10) + 1)
        
    def _get_state_key(self, obs):
        r_bin = self._get_bin(obs.get('resource', 0))
        ig = obs.get('invest_gain_count', 0)
        idc = obs.get('invest_decay_count', 0)
        return (r_bin, ig, idc)
        
    def _get_q(self, s, a):
        if s not in self.Q: self.Q[s] = {act: 0.0 for act in self.actions}
        return self.Q[s][a]
        
    def _get_max_q(self, s):
        if s not in self.Q: return 0.0
        return max(self.Q[s].values())
        
    def get_state(self) -> dict:
        invest_q = []
        for s in self.Q:
            invest_q.append(self.Q[s]['invest_gain'])
        avg_invest_q = sum(invest_q) / len(invest_q) if invest_q else 0.0
        
        return {
            "unique_causal_actions_explored": len(self.unique_causal_actions_explored),
            "first_investment_tick": self.first_investment_tick,
            "q_size": len(self.Q),
            "avg_invest_q": avg_invest_q
        }

    def choose(self, observation: dict) -> str:
        self.tick += 1
        current_state = self._get_state_key(observation)
        current_resource = observation.get('resource', 0)
        
        # 1. Update Q(lambda)
        if self.last_state is not None and self.last_action is not None:
            r = -0.01 # Default small penalty for living
            if not observation.get('last_action_successful', True):
                r = -1.0 # Invalid action penalty
            else:
                if self.last_action == 'work':
                    r = 10.0
                elif self.last_action in ['invest_gain', 'invest_decay']:
                    r = -0.01
                    
            delta = r + self.gamma * self._get_max_q(current_state) - self._get_q(self.last_state, self.last_action)
            
            if self.last_state not in self.E:
                self.E[self.last_state] = {act: 0.0 for act in self.actions}
            self.E[self.last_state][self.last_action] += 1.0
            
            for s in list(self.E.keys()):
                if s not in self.Q: self.Q[s] = {act: 0.0 for act in self.actions}
                for a in self.actions:
                    if self.E[s][a] > 0:
                        self.Q[s][a] += self.alpha * delta * self.E[s][a]
                        self.E[s][a] *= self.gamma * self.lambd
                        if self.E[s][a] < 1e-4:
                            self.E[s][a] = 0.0
                            
        # 2. Choose Action
        epsilon = max(0.05, 1.0 - (0.95 / 3000.0) * self.tick)
        
        if self.rng.random() < epsilon:
            best_action = self.rng.choice(self.actions)
        else:
            if current_state not in self.Q:
                self.Q[current_state] = {act: 0.0 for act in self.actions}
            max_q = max(self.Q[current_state].values())
            best_actions = [a for a, q in self.Q[current_state].items() if abs(q - max_q) < 1e-6]
            best_action = self.rng.choice(best_actions)
            
        if best_action in ['invest_gain', 'invest_decay'] and observation.get('last_action_successful', True):
            self.unique_causal_actions_explored.add(best_action)
            if self.first_investment_tick == -1:
                self.first_investment_tick = self.tick
                
        self.last_state = current_state
        self.last_action = best_action
        self.last_resource = current_resource
        
        # Mute the action before sending it to the environment
        if best_action == 'invest_gain':
            return 'invest_gain_dummy'
        elif best_action == 'invest_decay':
            return 'invest_decay_dummy'
            
        return best_action
