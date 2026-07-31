from typing import Dict, Any, Optional

class LongTermMemory:
    """
    The hook for DoryBrain.
    Stores overarching behavioral policies, user preferences, and cross-session learnings.
    """
    def __init__(self):
        self.policies: Dict[str, Any] = {}
        
    def get_policy(self, key: str) -> Optional[Any]:
        return self.policies.get(key)
        
    def update_policy(self, key: str, value: Any):
        # This is where DoryBrain's offline learning will push updates
        self.policies[key] = value
