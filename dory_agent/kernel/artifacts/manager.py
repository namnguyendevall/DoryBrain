from typing import Dict, Any, Optional
from dory_agent.kernel.contracts import ArtifactId
from dory_agent.kernel.artifacts.models import ArtifactMetadata
from dory_agent.kernel.artifacts.metadata_store import MetadataStore
from dory_agent.kernel.artifacts.blob_store import BlobStore
from dory_agent.kernel.contracts import Event, EventType, EventId

class ArtifactManager:
    """
    Manages the Artifact DAG (Provenance) and delegates storage to MetadataStore and BlobStore.
    """
    def __init__(self, event_bus):
        self.metadata_store = MetadataStore()
        self.blob_store = BlobStore()
        self.event_bus = event_bus

    def create_artifact(self, metadata: ArtifactMetadata, data: bytes) -> ArtifactId:
        """Saves a new artifact and broadcasts the ARTIFACT_CREATED event."""
        metadata.byte_size = len(data)
        
        self.blob_store.write(metadata.id, data)
        self.metadata_store.save(metadata)
        
        # Publish Event
        self.event_bus.publish(
            Event(
                event_type=EventType.ARTIFACT_CREATED,
                payload={"artifact_id": metadata.id, "type": metadata.type}
            )
        )
        return metadata.id
        
    def get_metadata(self, artifact_id: ArtifactId) -> Optional[ArtifactMetadata]:
        return self.metadata_store.get(artifact_id)
        
    def get_data(self, artifact_id: ArtifactId) -> bytes:
        return self.blob_store.read(artifact_id)
