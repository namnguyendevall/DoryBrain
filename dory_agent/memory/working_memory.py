from typing import Dict, Any, List

class WorkingMemory:
    """Stores temporary context for the current active task/goal."""
    def __init__(self):
        self.context: Dict[str, Any] = {}
        
    def update(self, key: str, value: Any):
        self.context[key] = value
        
    def get(self, key: str) -> Any:
        return self.context.get(key)
        
    def clear(self):
        self.context.clear()
