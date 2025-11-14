import os
try:
    from authlib.integrations.flask_client import OAuth
    from backend import app
except Exception:
    # If authlib isn't installed or import fails, provide a noop fallback
    OAuth = None
    app = None

_g_client_id = os.getenv("GOOGLE_CLIENT_ID")
_g_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

oauth = None

def is_configured():
    return bool(_g_client_id and _g_client_secret and OAuth and app)

if is_configured():
    oauth = OAuth(app)
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_id=_g_client_id,
        client_secret=_g_client_secret,
        client_kwargs={"scope": "openid email profile"},
    )

