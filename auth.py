"""Compatibility shim: import routes from backend.auth

This module re-exports the backend.auth module so existing imports
`import auth` or `from auth import ...` remain functional during the
reorganization.
"""

from backend import auth as _backend_auth

# Re-export names commonly used by other modules (flask picks up routes
# from the imported module so nothing else is needed).
__all__ = [name for name in dir(_backend_auth) if not name.startswith('_')]

