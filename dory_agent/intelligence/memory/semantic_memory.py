from typing import Dict, Any, Optional

class SemanticMemory:
    """
    Stores persistent factual knowledge, learned skills, environment data, 
    and constants (e.g., how to run a specific command, project structure).
    """
    def __init__(self):
        # In the future, this could be backed by a VectorDB
        self.knowledge_base: Dict[str, Any] = {}
        
    def store_fact(self, key: str, value: Any):
        self.knowledge_base[key] = value
        
    def query(self, query_str: str) -> Optional[Any]:
        # Simple exact match for now
        return self.knowledge_base.get(query_str)
