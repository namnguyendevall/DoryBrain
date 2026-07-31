import os

for f in ['E016A_Optimistic.py', 'E016B_CountBonus.py', 'E016C_UCB.py']:
    path = os.path.join('experiments', f)
    with open(path, 'r') as fh:
        content = fh.read()
    
    # Common modifications for tracking new metrics
    content = content.replace('self.unique_replays_count = 0\n        self.total_replays_attempted = 0', 'self.unique_replays_count = 0\n        self.total_replays_attempted = 0\n        self.max_resource_reached = 0.0\n        self.time_above_50_resource = 0\n        self.unique_state_action_pairs = set()')
    
    content = content.replace('"effective_unique_replay_ratio": effective_unique_replay_ratio', '"effective_unique_replay_ratio": effective_unique_replay_ratio,\n            "max_resource_reached": self.max_resource_reached,\n            "time_above_50_resource": self.time_above_50_resource,\n            "unique_state_action_pairs": len(self.unique_state_action_pairs)')
    
    content = content.replace('self.tick += 1\n        current_state = self._get_state_key(observation)', 'self.tick += 1\n        current_state = self._get_state_key(observation)\n        current_resource = observation.get("resource", 0.0)\n        if current_resource > self.max_resource_reached:\n            self.max_resource_reached = current_resource\n        if current_resource > 50.0:\n            self.time_above_50_resource += 1')
    
    content = content.replace('self.last_action = best_action', 'self.unique_state_action_pairs.add((current_state, best_action))\n        self.last_action = best_action')
    
    with open(path, 'w') as fh:
        fh.write(content)
