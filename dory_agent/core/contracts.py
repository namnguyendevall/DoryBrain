from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

# ============================================================================
# 0. IDENTITY SYSTEM
# ============================================================================

class GoalId(str): pass
class TaskId(str): pass
class StepId(str): pass
class ActionId(str): pass
class ArtifactId(str): pass
class TransactionId(str): pass
class EventId(str): pass
class WorkflowId(str): pass

def generate_id() -> str:
    return str(uuid.uuid4())

# ============================================================================
# 1. CAPABILITIES & TOOLS
# ============================================================================

class Capability(str, Enum):
    """
    Standardized capabilities that Planner can request.
    Planner asks for a capability (e.g. READ_FILE), and Registry provides the Tool.
    """
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    EDIT_FILE = "edit_file"
    SEARCH_FILE = "search_file"
    MANAGE_FILE = "manage_file"
    EXECUTE_COMMAND = "execute_command"
    BROWSE_WEB = "browse_web"
    HTTP_REQUEST = "http_request"
    UNKNOWN = "unknown"

class Tool(BaseModel):
    """
    Interface for a Tool Plugin.
    """
    name: str
    description: str
    capabilities: List[Capability]
    
    def execute(self, **kwargs) -> 'Observation':
        raise NotImplementedError

# ============================================================================
# 2. RUNTIME MODELS (GOAL, ACTION, OBSERVATION)
# ============================================================================

class Goal(BaseModel):
    """
    The high-level objective Dory must achieve.
    """
    objective: str
    constraints: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)

class Action(BaseModel):
    """
    Standardized action requested by the Executor/Planner.
    """
    capability: Capability
    arguments: Dict[str, Any]
    expected_result: str
    
class ObservationStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"

class Observation(BaseModel):
    """
    Standardized result returned by a Tool.
    """
    status: ObservationStatus
    tool_name: str
    latency_seconds: float
    stdout: str
    stderr: str
    artifacts: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# ============================================================================
# 3. CRITIC & POLICY
# ============================================================================

class CriticState(str, Enum):
    SUCCESS = "success"    # Step completed perfectly
    PARTIAL = "partial"    # Step completed but with caveats (continue but note it)
    RETRY = "retry"        # Temporary failure, Executor should retry exactly as is
    REPLAN = "replan"      # Fundamental failure, Planner needs to create a new step
    ABORT = "abort"        # Fatal error (e.g., permission denied, max retries reached)

class CriticResult(BaseModel):
    """
    The evaluation of an Observation by the Critic.
    """
    state: CriticState
    reasoning: str
    suggestions_for_planner: Optional[str] = None

# ============================================================================
# 4. EVENT SOURCING (EVENT BUS)
# ============================================================================

class EventType(str, Enum):
    GOAL_RECEIVED = "goal_received"
    PLAN_CREATED = "plan_created"
    STEP_STARTED = "step_started"
    ACTION_STARTED = "action_started"
    OBSERVATION_RECEIVED = "observation_received"
    CRITIC_EVALUATED = "critic_evaluated"
    GOAL_COMPLETED = "goal_completed"
    GOAL_FAILED = "goal_failed"
    
    # Filesystem / Artifact Events
    ARTIFACT_CREATED = "artifact_created"
    TRANSACTION_STAGED = "transaction_staged"
    TRANSACTION_COMMITTED = "transaction_committed"
    TRANSACTION_ROLLED_BACK = "transaction_rolled_back"

class Event(BaseModel):
    """
    Immutable event record for strict Event Sourcing.
    """
    event_id: EventId = Field(default_factory=lambda: EventId(generate_id()))
    parent_event_id: Optional[EventId] = None
    goal_id: Optional[GoalId] = None
    workflow_id: Optional[WorkflowId] = None
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: EventType
    payload: Dict[str, Any]

# ============================================================================
# 5. INTERFACES (PLANNER & REGISTRY)
# ============================================================================

class PlannerInterface:
    def plan(self, goal: Goal, context: Dict[str, Any]) -> List[Action]:
        raise NotImplementedError
        
class ToolRegistryInterface:
    def register(self, tool: Tool):
        raise NotImplementedError
        
    def get_tool_for_capability(self, capability: Capability) -> Optional[Tool]:
        raise NotImplementedError
