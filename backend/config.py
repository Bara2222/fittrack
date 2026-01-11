# backend/config.py
"""
Backend Configuration
Secure configuration management with environment variables
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _read_secret_file(path: str) -> str | None:
    """Read a secret from a file path; return stripped content or None."""
    try:
        if path and os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read().strip()
    except Exception:
        pass
    return None

class Config:
    """Base configuration"""
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'tajny_klic_CHANGE_IN_PRODUCTION')
    
    # Database
    _basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    _db_path = os.path.join(_basedir, 'instance', 'db.sqlite3')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{_db_path}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    
    # CORS
    # Allow spaces in .env values and ignore empty entries
    _cors = os.getenv('CORS_ORIGINS', 'http://localhost:8501,http://127.0.0.1:8501')
    CORS_ORIGINS = [o.strip() for o in _cors.split(',') if o.strip()]
    
    # OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    # Prefer explicit env var, then a file path in GOOGLE_CLIENT_SECRET_FILE, then `/run/secrets/google_client_secret`.
    _gcs_env = os.getenv('GOOGLE_CLIENT_SECRET')
    _gcs_file = os.getenv('GOOGLE_CLIENT_SECRET_FILE') or '/run/secrets/google_client_secret'
    GOOGLE_CLIENT_SECRET = _gcs_env or _read_secret_file(_gcs_file)
    
    # URLs for OAuth redirects
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:8501')
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')
    
    # Admin
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Admin&4')
    
    # Session
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = False  # Allow frontend to access session
    SESSION_COOKIE_SAMESITE = 'None' if SESSION_COOKIE_SECURE else 'Lax'  # Allow cross-origin
    SESSION_COOKIE_DOMAIN = os.getenv('SESSION_COOKIE_DOMAIN')  # Can be set for production
    REMEMBER_COOKIE_HTTPONLY = False
    REMEMBER_COOKIE_SAMESITE = 'None' if SESSION_COOKIE_SECURE else 'Lax'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_ENABLED = True

# Config selector
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get config based on FLASK_ENV"""
    env = os.getenv('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)
