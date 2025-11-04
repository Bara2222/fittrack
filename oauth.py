import os
from authlib.integrations.flask_client import OAuth
from app import app

oauth = OAuth(app)
_g_client_id = os.getenv("GOOGLE_CLIENT_ID")
_g_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

if not _g_client_id or not _g_client_secret:
    # Fail early with a helpful message so developer can fix configuration
    raise RuntimeError(
        "Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in a .env file or the environment. "
        "Also ensure the Authorized redirect URI in Google Cloud Console includes:"
        " http://127.0.0.1:5000/auth/google/callback (and/or http://localhost:5000/auth/google/callback)."
    )

oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=_g_client_id,
    client_secret=_g_client_secret,
    client_kwargs={"scope": "openid email profile"},
)
