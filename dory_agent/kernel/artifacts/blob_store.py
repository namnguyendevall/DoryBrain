from typing import Dict, Any
from dory_agent.kernel.contracts import ArtifactId

class BlobStore:
    """
    Abstracts the physical storage of Artifact data.
    Could be Local Disk, S3, Memory, etc.
    """
    def __init__(self):
        # Using memory for demonstration. In production, this saves to a workspace/.artifacts folder.
        self._blobs: Dict[ArtifactId, bytes] = {}

    def write(self, artifact_id: ArtifactId, data: bytes):
        self._blobs[artifact_id] = data
        
    def read(self, artifact_id: ArtifactId) -> bytes:
        return self._blobs.get(artifact_id, b"")
        
    def delete(self, artifact_id: ArtifactId):
        self._blobs.pop(artifact_id, None)
