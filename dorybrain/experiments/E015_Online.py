import random

class Actor:
    """
    E015_Online: Online Compute Budget Control
    """
    def __init__(self, seed: int, batch_size: int = 32):
        self.rng = random.Random(seed)
        
        self.Q = {}
        
        self.alpha = 0.1
        self.gamma = 0.99
        
        self.batch_size = batch_size
        self.buffer = []
        self.max_buffer = 5000
        
        self.all_actions = ['rest', 'work', 'invest_gain', 'invest_decay']
        
        self.tick = 0
        
        self.last_state = None
        self.last_action = None
        
        self.unique_causal_actions_explored = set()
        self.first_investment_tick = -1
        
        
        # New Metrics for Protocol Validation & Replay
        self.masked_actions = 0
        self.candidate_actions = 0
        self.effective_explorations = 0
        self.attempted_explorations = 0
        self.first_successful_replay_tick = -1
        self.total_replay_age = 0.0
        self.replay_count = 0
        self.q_invest_latency = -1
        self.q_invest_crossed_tick = -1
        
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
        q_invest = 0.0
        q_rest = 0.0
        
        # Start state is resource=30, ig=0, idc=0. Bin for 30 is 4.
        start_state = (4, 0, 0)
        if start_state in self.Q:
            q_invest = self.Q[start_state].get('invest_gain', 0.0)
            q_rest = self.Q[start_state].get('rest', 0.0)
            
        mask_rate = self.masked_actions / max(1, self.candidate_actions)
        effective_exploration_rate = self.effective_explorations / max(1, self.tick)
        
        avg_replay_age = self.total_replay_age / self.replay_count if self.replay_count > 0 else 0.0
        
        return {
            "unique_causal_actions_explored": len(self.unique_causal_actions_explored),
            "first_investment_tick": self.first_investment_tick,
            "q_size": len(self.Q),
            "q_invest_start": q_invest,
            "q_rest_start": q_rest,
            "mask_rate": mask_rate,
            "effective_exploration_rate": effective_exploration_rate,
            "first_successful_replay_tick": self.first_successful_replay_tick,
            "investment_latency": self.q_invest_latency,
            "avg_replay_age": avg_replay_age
        }

    def _get_valid_actions(self, obs: dict) -> list[str]:
        valid = []
        resource = obs.get('resource', 0)
        physics = obs.get('physics', {})
        passive_decay = physics.get('passive_decay', 1.0)
        max_resource = physics.get('max_resource', 100.0)
        work_cost = physics.get('work_cost', 0.0)
        
        # We need to account for decay_reduction and rest_gain_bonus if we had access to them,
        # but passive_decay parameter is the base. For safety, base passive_decay is an upper bound.
        # Actually, effective decay can be 0, but using base passive_decay is safe.
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
                    
                # Also mask if already maxed to avoid pointless death
                if a == 'invest_gain' and obs.get('invest_gain_count', 0) >= 2:
                    is_valid = False
                if a == 'invest_decay' and obs.get('invest_decay_count', 0) >= 2:
                    is_valid = False
                    
            if is_valid:
                valid.append(a)
                
        # Fallback if nothing is valid (shouldn't happen unless completely doomed)
        if not valid:
            return self.all_actions
            
        return valid

    def choose(self, observation: dict) -> str:
        self.tick += 1
        current_state = self._get_state_key(observation)
        valid_actions = self._get_valid_actions(observation)
        
        # 1. Store experience and Online Update
        if self.last_state is not None and self.last_action is not None:
            r = -0.01
            if not observation.get('last_action_successful', True):
                r = -1.0
            else:
                if self.last_action == 'work':
                    r = 10.0
                elif self.last_action in ['invest_gain', 'invest_decay']:
                    r = -0.01
            
            # Store in buffer
            self.buffer.append((self.last_state, self.last_action, r, current_state, valid_actions, self.tick))
            if len(self.buffer) > self.max_buffer:
                self.buffer.pop(0)
                
            # Online Q-learning update
            max_q = self._get_max_q(current_state, valid_actions)
            delta = r + self.gamma * max_q - self._get_q(self.last_state, self.last_action)
            self.Q[self.last_state][self.last_action] += self.alpha * delta

        # 2. Online Control (Compute Budget equivalent)
        # Thực hiện N lần Bellman backup trên transition hiện tại, nhưng chia alpha thành alpha/N.
        if self.batch_size > 0 and self.last_state is not None and self.last_action is not None:
            scaled_alpha = self.alpha / self.batch_size
            for _ in range(self.batch_size):
                max_q_next = self._get_max_q(current_state, valid_actions)
                delta_b = r + self.gamma * max_q_next - self._get_q(self.last_state, self.last_action)
                self.Q[self.last_state][self.last_action] += scaled_alpha * delta_b

        # 2. Choose Action
        # Epsilon decay from 0.3 to 0.05 over 1000 ticks
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
            # Re-select from valid actions
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
            if self.q_invest_crossed_tick != -1 and self.q_invest_latency == -1:
                self.q_invest_latency = self.tick - self.q_invest_crossed_tick
                
        # Track when Q(invest) > Q(rest)
        if self.q_invest_crossed_tick == -1 and current_state in self.Q:
            q_rest = self.Q[current_state].get('rest', 0.0)
            q_ig = self.Q[current_state].get('invest_gain', 0.0)
            q_id = self.Q[current_state].get('invest_decay', 0.0)
            if q_ig > q_rest or q_id > q_rest:
                self.q_invest_crossed_tick = self.tick
                
        self.last_state = current_state
        self.last_action = best_action
        
        return best_action
