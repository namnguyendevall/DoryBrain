from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Protocol, Set
from uuid import UUID, uuid4

# ============================================================================
# 1. INTENT (Immutable)
# ============================================================================

class IntentId(str): pass

class Intent(BaseModel):
    """
    Immutable representation of what the Planner wants to achieve.
    No execution state (like retry_count or progress) is stored here.
    """
    id: IntentId = Field(default_factory=lambda: IntentId(str(uuid4())))
    name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        frozen = True  # Enforce immutability

# ============================================================================
# 2. COMMAND & EXECUTION PLAN (DAG)
# ============================================================================

class CommandId(str): pass

class Command(BaseModel):
    """
    Pure data structure representing a specific execution step.
    Does not contain execution logic (no I/O, no OS calls).
    """
    id: CommandId = Field(default_factory=lambda: CommandId(str(uuid4())))
    capability: str
    action: str
    arguments: Dict[str, Any] = Field(default_factory=dict)

class ExecutionPlan(BaseModel):
    """
    A DAG of Commands to satisfy an Intent.
    """
    intent_id: IntentId
    nodes: Dict[CommandId, Command] = Field(default_factory=dict)
    # Mapping of a CommandId to the set of CommandIds that depend on it
    edges: Dict[CommandId, Set[CommandId]] = Field(default_factory=dict)

# ============================================================================
# 3. DETECTOR & CONFIDENCE
# ============================================================================

class Confidence(BaseModel):
    value: Any
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: Optional[str] = None

class Detector(Protocol):
    """
    Interface for heuristic detectors (Language, Framework, Test, etc).
    """
    def detect(self, context: Dict[str, Any]) -> Confidence:
        ...

# ============================================================================
# 4. CAPABILITY & RESOLVER
# ============================================================================

class CapabilityResolver(Protocol):
    """
    Translates an Intent into an ExecutionPlan (DAG of Commands).
    """
    def resolve(self, intent: Intent) -> ExecutionPlan:
        ...

class CapabilityInterface(Protocol):
    """
    The universal interface for all capabilities (Filesystem, Terminal, Browser).
    """
    def get_resolver(self) -> CapabilityResolver:
        ...

# ============================================================================
# 5. ARTIFACT PROMOTION (Raw vs Derived)
# ============================================================================

class ArtifactTier(str):
    RAW = "raw"
    DERIVED = "derived"

class WorkspaceProfile(BaseModel):
    """
    The Root Node of the Knowledge Fabric.
    A high-level derived artifact representing the Project Identity.
    """
    language: Optional[Confidence] = None
    framework: Optional[Confidence] = None
    package_manager: Optional[Confidence] = None
    vcs: Optional[Confidence] = None
    build_system: Optional[Confidence] = None
    entrypoints: List[Confidence] = Field(default_factory=list)
    test_frameworks: List[Confidence] = Field(default_factory=list)
    overall_confidence: float = 0.0
