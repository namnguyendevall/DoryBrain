from dory_agent.memory.working_memory import WorkingMemory
from dory_agent.memory.episodic_memory import EpisodicMemory
from dory_agent.memory.semantic_memory import SemanticMemory
from dory_agent.memory.long_term_memory import LongTermMemory

class MemoryManager:
    """
    Facade over all 4 memory tiers.
    The Runtime only interacts with this Manager, which orchestrates updates
    to the specific memory tiers.
    """
    def __init__(self):
        self.working = WorkingMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.long_term = LongTermMemory()
