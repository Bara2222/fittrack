"""Compatibility shim exposing backend.app as app

Old imports (from app import app) expect this module to define 'app'.
We import the Flask application from the new backend package and expose
it under the expected names.
"""

from backend import app, db, login_manager  # re-export for compatibility

__all__ = ['app', 'db', 'login_manager']

