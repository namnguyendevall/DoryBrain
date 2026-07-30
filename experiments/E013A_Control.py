import random

class Actor:
    """
    E013A_Control: Safe Q-Lambda Control Agent
    """
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        
        self.Q = {}
        self.E = {}
        
        self.alpha = 0.1
        self.gamma = 0.99
        self.lambd = 0.8
        
        self.all_actions = ['rest', 'work', 'invest_gain', 'invest_decay']
        
        self.tick = 0
        
        self.last_state = None
        self.last_action = None
        
        self.unique_causal_actions_explored = set()
        self.first_investment_tick = -1
        
        self.masked_actions = 0
        self.candidate_actions = 0
        self.effective_explorations = 0
        
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
        if s not in self.Q: self.Q[s] = {act: 0.0 for act in self.all_actions}
        return self.Q[s][a]
        
    def _get_max_q(self, s, valid_actions):
        if s not in self.Q: return 0.0
        return max(self.Q[s][a] for a in valid_actions)
        
    def get_state(self) -> dict:
        invest_q = []
        for s in self.Q:
            invest_q.append(self.Q[s]['invest_gain'])
        avg_invest_q = sum(invest_q) / len(invest_q) if invest_q else 0.0
        
        mask_rate = self.masked_actions / max(1, self.candidate_actions)
        effective_exploration_rate = self.effective_explorations / max(1, self.tick)
        
        return {
            "unique_causal_actions_explored": len(self.unique_causal_actions_explored),
            "first_investment_tick": self.first_investment_tick,
            "q_size": len(self.Q),
            "avg_invest_q": avg_invest_q,
            "mask_rate": mask_rate,
            "effective_exploration_rate": effective_exploration_rate
        }

    def _get_valid_actions(self, obs: dict) -> list[str]:
        valid = []
        resource = obs.get('resource', 0)
        physics = obs.get('physics', {})
        passive_decay = physics.get('passive_decay', 1.0)
        max_resource = physics.get('max_resource', 100.0)
        work_cost = physics.get('work_cost', 0.0)
        
        safe_margin = passive_decay
        
        for a in self.all_actions:
            is_valid = True
            
            if a == 'rest':
                if resource >= max_resource:
                    is_valid = False
            elif a == 'work':
                resource_after = resource - work_cost - safe_margin
                if resource_after <= 0:
                    is_valid = False
            elif a in ['invest_gain', 'invest_decay']:
                resource_after = resource - 30.0 - safe_margin
                if resource_after <= 0:
                    is_valid = False
                    
                if a == 'invest_gain' and obs.get('invest_gain_count', 0) >= 2:
                    is_valid = False
                if a == 'invest_decay' and obs.get('invest_decay_count', 0) >= 2:
                    is_valid = False
                    
            if is_valid:
                valid.append(a)
                
        if not valid:
            return self.all_actions
            
        return valid

    def choose(self, observation: dict) -> str:
        self.tick += 1
        current_state = self._get_state_key(observation)
        valid_actions = self._get_valid_actions(observation)
        
        if self.last_state is not None and self.last_action is not None:
            r = -0.01
            if not observation.get('last_action_successful', True):
                r = -1.0
            else:
                if self.last_action == 'work':
                    r = 10.0
                elif self.last_action in ['invest_gain', 'invest_decay']:
                    r = -0.01
                    
            delta = r + self.gamma * self._get_max_q(current_state, valid_actions) - self._get_q(self.last_state, self.last_action)
            
            if self.last_state not in self.E:
                self.E[self.last_state] = {act: 0.0 for act in self.all_actions}
            self.E[self.last_state][self.last_action] += 1.0
            
            for s in list(self.E.keys()):
                if s not in self.Q: self.Q[s] = {act: 0.0 for act in self.all_actions}
                for a in self.all_actions:
                    if self.E[s][a] > 0:
                        self.Q[s][a] += self.alpha * delta * self.E[s][a]
                        self.E[s][a] *= self.gamma * self.lambd
                        if self.E[s][a] < 1e-4:
                            self.E[s][a] = 0.0

        epsilon = max(0.05, 0.3 - (0.25 / 1000.0) * self.tick)
        
        self.candidate_actions += 1
        is_exploring = False
        raw_best_action = None
        
        if self.rng.random() < epsilon:
            is_exploring = True
            raw_best_action = self.rng.choice(self.all_actions)
        else:
            if current_state not in self.Q:
                self.Q[current_state] = {act: 0.0 for act in self.all_actions}
            max_q = max(self.Q[current_state].values())
            best_raw_actions = [a for a, q in self.Q[current_state].items() if abs(q - max_q) < 1e-6]
            raw_best_action = self.rng.choice(best_raw_actions)
            
        if raw_best_action not in valid_actions:
            self.masked_actions += 1
            if is_exploring:
                best_action = self.rng.choice(valid_actions)
                self.effective_explorations += 1
            else:
                max_valid_q = max(self.Q[current_state][a] for a in valid_actions)
                best_valid_actions = [a for a in valid_actions if abs(self.Q[current_state][a] - max_valid_q) < 1e-6]
                best_action = self.rng.choice(best_valid_actions)
        else:
            best_action = raw_best_action
            if is_exploring:
                self.effective_explorations += 1
            
        if best_action in ['invest_gain', 'invest_decay'] and observation.get('last_action_successful', True):
            self.unique_causal_actions_explored.add(best_action)
            if self.first_investment_tick == -1:
                self.first_investment_tick = self.tick
                
        self.last_state = current_state
        self.last_action = best_action
        
        if best_action == 'invest_gain':
            return 'invest_gain_dummy'
        elif best_action == 'invest_decay':
            return 'invest_decay_dummy'
            
        return best_action
