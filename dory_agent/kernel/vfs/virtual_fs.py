from typing import Protocol, Dict, Optional
import os
from urllib.parse import urlparse

class VirtualFileSystem(Protocol):
    """
    Abstracts physical storage via mounts (e.g., workspace://, temp://).
    """
    def mount(self, scheme: str, root_path: str):
        pass
        
    def resolve(self, uri: str) -> str:
        pass
        
    def exists(self, uri: str) -> bool:
        pass
        
    def read(self, uri: str) -> bytes:
        pass
        
    def write(self, uri: str, data: bytes):
        pass

class DefaultVirtualFileSystem(VirtualFileSystem):
    def __init__(self):
        self._mounts: Dict[str, str] = {}
        
    def mount(self, scheme: str, root_path: str):
        """
        Example: mount("workspace", "C:/Projects/DoryWorkspace")
        """
        self._mounts[scheme] = os.path.abspath(root_path)
        
    def resolve(self, uri: str) -> str:
        """
        Resolves workspace://main.py to C:/Projects/DoryWorkspace/main.py
        """
        parsed = urlparse(uri)
        scheme = parsed.scheme
        path = parsed.netloc + parsed.path # netloc usually contains the first path component if not //
        
        # simple parsing correction for custom schemes
        if "://" in uri:
            scheme, path = uri.split("://", 1)
            
        if scheme not in self._mounts:
            raise ValueError(f"Unmounted scheme: {scheme}")
            
        root = self._mounts[scheme]
        # Prevent path traversal
        normalized_path = os.path.normpath(os.path.join(root, path))
        if not normalized_path.startswith(root):
            raise PermissionError(f"Path traversal detected in URI: {uri}")
            
        return normalized_path
        
    def exists(self, uri: str) -> bool:
        path = self.resolve(uri)
        return os.path.exists(path)
        
    def read(self, uri: str) -> bytes:
        path = self.resolve(uri)
        with open(path, 'rb') as f:
            return f.read()
            
    def write(self, uri: str, data: bytes):
        path = self.resolve(uri)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)
