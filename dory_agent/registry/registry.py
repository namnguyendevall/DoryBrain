from typing import Dict, List, Optional
from dory_agent.core.contracts import Capability, Tool
from dory_agent.registry.manifest import ToolManifest
import logging

class ToolRegistry:
    """
    Manages available tools via their Manifests.
    Builds a Capability Graph to understand what tools fulfill what intents,
    and what permissions those tools require.
    """
    def __init__(self):
        # Maps Capability to a List of Tool Names that provide it
        self.capability_map: Dict[Capability, List[str]] = {
            cap: [] for cap in Capability
        }
        
        # Maps Tool Name to its Manifest
        self.manifests: Dict[str, ToolManifest] = {}
        
        # Maps Tool Name to the actual Tool instance (loaded lazily or manually registered)
        self.instances: Dict[str, Tool] = {}
        
        # Capability Graph: capability -> requires list (e.g. READ_FILE -> FILESYSTEM_PERMISSION)
        self.capability_graph: Dict[Capability, List[str]] = {}

    def register_manifest(self, manifest: ToolManifest):
        """Register a tool's capabilities via its manifest."""
        self.manifests[manifest.name] = manifest
        
        for cap in manifest.provides:
            if manifest.name not in self.capability_map[cap]:
                self.capability_map[cap].append(manifest.name)
                
            # Update the capability graph with requirements
            if cap not in self.capability_graph:
                self.capability_graph[cap] = []
            
            for req in manifest.requires:
                if req not in self.capability_graph[cap]:
                    self.capability_graph[cap].append(req)
                    
        logging.info(f"Registered tool manifest: {manifest.name} v{manifest.version}")

    def register_instance(self, tool: Tool):
        """Directly register an initialized tool instance."""
        self.instances[tool.name] = tool
        # In a full implementation, this might also generate a manifest on the fly

    def get_tool_for_capability(self, capability: Capability) -> Optional[Tool]:
        """
        Finds an available tool instance that provides the requested capability.
        """
        tool_names = self.capability_map.get(capability, [])
        for name in tool_names:
            if name in self.instances:
                return self.instances[name]
        return None
        
    def get_requirements_for_capability(self, capability: Capability) -> List[str]:
        """Returns the permissions or other capabilities required by this capability."""
        return self.capability_graph.get(capability, [])
