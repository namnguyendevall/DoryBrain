from typing import Dict, Optional, List
from dory_agent.kernel.contracts import ArtifactId
from dory_agent.kernel.artifacts.models import ArtifactMetadata

class MetadataStore:
    """
    Stores and indexes Artifact Metadata (the DAG).
    """
    def __init__(self):
        self._store: Dict[ArtifactId, ArtifactMetadata] = {}

    def save(self, metadata: ArtifactMetadata):
        self._store[metadata.id] = metadata

    def get(self, artifact_id: ArtifactId) -> Optional[ArtifactMetadata]:
        return self._store.get(artifact_id)
        
    def get_children(self, parent_id: ArtifactId) -> List[ArtifactMetadata]:
        """Traverse the DAG to find children of this artifact."""
        return [m for m in self._store.values() if parent_id in m.parent_ids]
