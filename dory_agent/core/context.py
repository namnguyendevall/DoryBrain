from typing import Dict, Any, Optional
from pydantic import BaseModel
from dory_agent.core.contracts import Goal, GoalId, ArtifactId, TransactionId, StepId

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

class RuntimeContext:
    """
    The Global Service Container. Lives for the lifecycle of the Dory process.
    Contains Managers and Services, but NO execution data.
    """
    def __init__(
        self,
        artifact_manager,
        event_bus,
        event_store,
        memory_manager,
        permission_manager,
        transaction_manager,
        registry,
        configuration: Dict[str, Any]
    ):
        self.artifact_manager = artifact_manager
        self.event_bus = event_bus
        self.event_store = event_store
        self.memory_manager = memory_manager
        self.permission_manager = permission_manager
        self.transaction_manager = transaction_manager
        self.registry = registry
        self.configuration = configuration
