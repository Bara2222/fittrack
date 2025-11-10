from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os, sys
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Zajistíme existenci instance složky a použijeme absolutní DB cestu
os.makedirs(app.instance_path, exist_ok=True)
DB_PATH = os.path.join(app.instance_path, 'db.sqlite3')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tajny_klic')
# Prefer env var; otherwise ensure absolute sqlite path
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') or f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True

db = SQLAlchemy(app)

# Ensure DB schema has required columns even if migrations weren't applied
def _ensure_schema():
    try:
        from sqlalchemy import text
        with app.app_context():
            # Create tables if not present
            db.create_all()
            # Check existing columns in user table
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
            # profile fields: age, height_cm, weight_kg
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
            # Create unique index on email if not exists (SQLite uses indexes to enforce UNIQUE)
            try:
                db.session.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uix_user_email ON user(email)"))
            except Exception:
                pass
            db.session.commit()
    except Exception:
        # Silent guard; app can still start and migrations can fix later
        pass

_ensure_schema()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = 'error'

sys.modules.setdefault('app', sys.modules[__name__])

import auth
# Register optional API blueprint (created in backend/). If it fails, continue silently.
try:
    from backend.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
except Exception:
    pass

print("[DEBUG] URL MAP:", app.url_map)

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
