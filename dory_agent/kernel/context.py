from typing import Dict, Any, Optional
from pydantic import BaseModel
from dory_agent.kernel.contracts import Goal, GoalId, ArtifactId, TransactionId, StepId

class ServiceLocator:
    """
    Centralized registry for all core managers and services.
    Replaces massive constructor DI and avoids coupling.
    All attributes here should ideally be Interfaces in a real implementation.
    """
    def __init__(self):
        self.artifact_manager = None
        self.event_bus = None
        self.event_store = None
        self.memory_manager = None
        self.permission_manager = None
        self.transaction_engine = None
        self.registry = None
        self.virtual_fs = None
        self.configuration: Dict[str, Any] = {}

class RuntimeContext:
    """
    The Global Service Container. Lives for the lifecycle of the Dory process.
    """
    def __init__(self):
        self.services = ServiceLocator()

class ExecutionContext(BaseModel):
    """
    Data container for a specific goal/execution run.
    Lives only for the duration of the Goal.
    """
    goal: Goal
    goal_id: GoalId
    
    # Working memory for this specific execution (no large blobs, just IDs/metadata)
    working_memory: Dict[str, Any] = {}
    
    active_artifacts: list[ArtifactId] = []
    active_transactions: list[TransactionId] = []
    current_step_id: Optional[StepId] = None
