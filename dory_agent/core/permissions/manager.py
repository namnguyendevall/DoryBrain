from typing import List, Protocol

class PermissionManager(Protocol):
    """
    Interface for managing and verifying capability-based permissions.
    """
    def grant(self, permission: str, scope: str):
        pass

    def check(self, permission: str, scope: str) -> bool:
        pass

class DefaultPermissionManager(PermissionManager):
    def __init__(self):
        # Maps permission string -> list of allowed scopes
        # Example: "filesystem.read" -> ["workspace", "temp"]
        self._grants = {}

    def grant(self, permission: str, scope: str):
        if permission not in self._grants:
            self._grants[permission] = set()
        self._grants[permission].add(scope)

    def check(self, permission: str, scope: str) -> bool:
        allowed_scopes = self._grants.get(permission, set())
        return scope in allowed_scopes or "*" in allowed_scopes
