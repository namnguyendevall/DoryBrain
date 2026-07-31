from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from dory_agent.core.contracts import Action, Capability

class PolicyDecision(BaseModel):
    allowed: bool
    reason: Optional[str] = None
    requires_approval: bool = False
    timeout_seconds: int = 60

class PolicyEngine:
    """
    Sits between Planner and Executor.
    Evaluates an Action to ensure it complies with security rules, budget limits,
    and user preferences.
    """
    def __init__(self):
        self.whitelisted_capabilities: List[Capability] = [
            Capability.READ_FILE,
            Capability.WRITE_FILE,
            Capability.SEARCH_FILE,
            Capability.MANAGE_FILE,
            Capability.EXECUTE_COMMAND
        ]
        
    def evaluate(self, action: Action) -> PolicyDecision:
        """
        Evaluate if an action is allowed to proceed.
        """
        if action.capability not in self.whitelisted_capabilities:
            return PolicyDecision(
                allowed=False, 
                reason=f"Capability {action.capability} is not whitelisted."
            )
            
        # Example logic for potentially dangerous actions
        if action.capability == Capability.EXECUTE_COMMAND:
            return PolicyDecision(
                allowed=True,
                requires_approval=True,  # Might require human-in-the-loop
                timeout_seconds=30
            )
            
        return PolicyDecision(allowed=True, timeout_seconds=60)
