import time
import logging
from typing import Dict, Any
from dory_agent.core.contracts import Action, Observation, ObservationStatus
from dory_agent.registry.registry import ToolRegistry
from dory_agent.execution.policy import PolicyDecision

class Executor:
    """
    Pure execution engine. Zero logic.
    Receives an Action, finds the Tool via Registry, and executes it.
    Does not retry, does not reason.
    """
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        
    def execute(self, action: Action, policy: PolicyDecision) -> Observation:
        if not policy.allowed:
            return Observation(
                status=ObservationStatus.ERROR,
                tool_name="policy_engine",
                latency_seconds=0.0,
                stdout="",
                stderr=policy.reason or "Action blocked by policy.",
            )
            
        tool = self.registry.get_tool_for_capability(action.capability)
        if not tool:
            return Observation(
                status=ObservationStatus.ERROR,
                tool_name="registry",
                latency_seconds=0.0,
                stdout="",
                stderr=f"No tool found for capability: {action.capability}"
            )
            
        start_time = time.time()
        try:
            # Here we would implement the actual timeout logic from policy.timeout_seconds
            observation = tool.execute(**action.arguments)
        except Exception as e:
            logging.error(f"Tool {tool.name} failed: {e}")
            observation = Observation(
                status=ObservationStatus.ERROR,
                tool_name=tool.name,
                latency_seconds=time.time() - start_time,
                stdout="",
                stderr=str(e)
            )
            
        # Ensure latency is recorded
        observation.latency_seconds = time.time() - start_time
        return observation
