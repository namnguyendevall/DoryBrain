from dory_agent.core.contracts import Action, Observation, Goal, CriticResult, CriticState, ObservationStatus
from typing import Dict, Any

class Critic:
    """
    Evaluates an Observation against the Action and the Goal.
    Returns structured feedback (SUCCESS, PARTIAL, RETRY, REPLAN, ABORT).
    Does NOT call tools.
    """
    def evaluate(self, action: Action, observation: Observation, goal: Goal, context: Dict[str, Any]) -> CriticResult:
        # In a full implementation, this would use an LLM or logic rules
        # to assess if the observation matches the expected_result
        
        if observation.status == ObservationStatus.ERROR:
            # Basic fallback logic for errors
            if "permission denied" in observation.stderr.lower():
                return CriticResult(
                    state=CriticState.ABORT,
                    reasoning="Fatal permission error encountered.",
                    suggestions_for_planner="Request human intervention or different permissions."
                )
            elif "not found" in observation.stderr.lower():
                return CriticResult(
                    state=CriticState.REPLAN,
                    reasoning="Target not found. Planner needs a new approach.",
                    suggestions_for_planner="Try searching for the file first."
                )
            else:
                return CriticResult(
                    state=CriticState.RETRY,
                    reasoning="Transient error encountered.",
                    suggestions_for_planner="Try executing the exact same action again."
                )
                
        # If success, return success
        return CriticResult(
            state=CriticState.SUCCESS,
            reasoning="Action completed successfully and returned expected output."
        )
