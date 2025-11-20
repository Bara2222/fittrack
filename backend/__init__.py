# backend/__init__.py
from backend.app import create_app, db, login_manager

app = create_app()
__all__ = ['app', 'db', 'login_manager']
__all__ = ['app', 'db', 'login_manager']
