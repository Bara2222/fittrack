# backend/oauth.py
"""
Google OAuth integration using Authlib
"""
import os
from authlib.integrations.flask_client import OAuth
from flask import current_app


oauth = None


def init_oauth(app):
    """Initialize OAuth with Flask app"""
    global oauth
    
    client_id = app.config.get('GOOGLE_CLIENT_ID')
    client_secret = app.config.get('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        app.logger.warning('Google OAuth credentials not configured')
        oauth = None
        return None
    
    oauth = OAuth(app)
    
    # Register Google OAuth client
    google = oauth.register(
        name='google',
        client_id=client_id,
        client_secret=client_secret,
        server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    
    app.logger.info('Google OAuth initialized successfully')
    return oauth


def is_configured():
    """Check if OAuth is properly configured"""
    return oauth is not None

