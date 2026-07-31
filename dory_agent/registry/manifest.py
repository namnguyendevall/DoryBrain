from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from dory_agent.core.contracts import Capability

class ToolManifest(BaseModel):
    """
    Metadata for a tool plugin. Defines what the tool can do, 
    without needing to instantiate the tool itself.
    """
    name: str
    version: str
    description: str
    author: Optional[str] = "Dory Ecosystem"
    
    # Capabilities this tool provides
    provides: List[Capability]
    
    # Capabilities or Permissions this tool requires to function
    requires: List[str] = Field(default_factory=list)
    
    # Path to the module or class if lazy loading
    entrypoint: str
