from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from dory_agent.core.contracts import ArtifactId, GoalId, StepId, generate_id

class ArtifactMetadata(BaseModel):
    """
    Metadata representation of an Artifact (The DAG Node).
    Contains no blob data, only provenance and identification.
    """
    id: ArtifactId = Field(default_factory=lambda: ArtifactId(generate_id()))
    type: str  # e.g. "file", "json", "dom_snapshot", "ast"
    name: str
    
    # Provenance (DAG links)
    parent_ids: List[ArtifactId] = Field(default_factory=list)
    creator_tool: str
    goal_id: Optional[GoalId] = None
    step_id: Optional[StepId] = None
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # MIME or format specifics
    content_type: str = "text/plain"
    byte_size: int = 0
