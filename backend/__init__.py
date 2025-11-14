from flask import Flask, request, jsonify
import logging
from traceback import format_exc
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os, sys
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Ensure instance path exists and set DB path
os.makedirs(app.instance_path, exist_ok=True)
DB_PATH = os.path.join(app.instance_path, 'db.sqlite3')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tajny_klic')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') or f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'api.api_login'
login_manager.login_message_category = 'error'

sys.modules.setdefault('backend', sys.modules[__name__])

# Import models early so SQLAlchemy knows model definitions before creating tables
try:
    import backend.models  # noqa: F401
except Exception:
    pass


def _ensure_schema():
    try:
        from sqlalchemy import text
        with app.app_context():
            db.create_all()
            insp_cols = []
            try:
                rows = db.session.execute(text("PRAGMA table_info(user)")).fetchall()
                insp_cols = [r[1] for r in rows]
            except Exception:
                insp_cols = []
            to_add = []
            if 'email' not in insp_cols:
                to_add.append("ALTER TABLE user ADD COLUMN email VARCHAR(255)")
            if 'oauth_provider' not in insp_cols:
                to_add.append("ALTER TABLE user ADD COLUMN oauth_provider VARCHAR(50)")
            if 'oauth_sub' not in insp_cols:
                to_add.append("ALTER TABLE user ADD COLUMN oauth_sub VARCHAR(255)")
            if 'created_at' not in insp_cols:
                to_add.append("ALTER TABLE user ADD COLUMN created_at DATETIME")
            if 'age' not in insp_cols:
                to_add.append("ALTER TABLE user ADD COLUMN age INTEGER")
            if 'height_cm' not in insp_cols:
                to_add.append("ALTER TABLE user ADD COLUMN height_cm FLOAT")
            if 'weight_kg' not in insp_cols:
                to_add.append("ALTER TABLE user ADD COLUMN weight_kg FLOAT")
            for stmt in to_add:
                try:
                    db.session.execute(text(stmt))
                except Exception:
                    pass
            try:
                db.session.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uix_user_email ON user(email)"))
            except Exception:
                pass
            db.session.commit()
    except Exception:
        pass

_ensure_schema()

@login_manager.user_loader
def load_user(user_id):
    from backend.models import User
    return User.query.get(int(user_id))
# Package marker for backend API

# Register API blueprint if available
try:
    from backend.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
except Exception:
    pass

# Add a simple root route so the server root is not 404.
@app.route('/')
def index():
    try:
        return app.send_static_file('index.html') if False else __import__('flask').render_template('index.html')
    except Exception:
        # Fallback JSON response if templates aren't available
        return {'ok': True, 'message': 'FitTrack backend running. API available under /api'}, 200


# --- Error logging -------------------------------------------------
# Ensure instance path exists and add a file handler for error logging
try:
    log_path = os.path.join(app.instance_path, 'error.log')
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fh.setFormatter(fmt)
    logger = logging.getLogger('fittrack')
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger.addHandler(fh)
except Exception:
    logger = logging.getLogger('fittrack')


@app.errorhandler(Exception)
def handle_unhandled_exception(e):
    """Log full traceback to instance/error.log and return minimal response.

    For API routes we return JSON {'ok': False, 'error': 'Internal Server Error'} to
    keep the frontend from trying to parse HTML error pages. The full traceback is
    saved to instance/error.log for inspection.
    """
    tb = format_exc()
    try:
        logger.exception('Unhandled exception: %s', str(e))
        logger.debug(tb)
    except Exception:
        pass

    # Always append the full traceback to the instance error.log file as a fallback
    try:
        log_path = os.path.join(app.instance_path, 'error.log')
        with open(log_path, 'a', encoding='utf-8') as fh:
            fh.write(f"=== {datetime.datetime.utcnow().isoformat()} UTC ===\n")
            fh.write(tb)
            fh.write("\n\n")
    except Exception:
        # If we can't write to the file, silently continue — at least the logger above ran
        pass
    # If request is an API call, return JSON
    try:
        if request.path.startswith('/api'):
            return jsonify({'ok': False, 'error': 'Internal Server Error'}), 500
    except Exception:
        pass

    # Generic fallback
    return 'Internal Server Error', 500
