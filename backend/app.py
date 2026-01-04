# backend/app.py
"""
Flask Application Factory
Clean architecture with proper initialization
"""
import os
import logging
from datetime import datetime
from traceback import format_exc

from flask import Flask, request, jsonify, g
import uuid
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from sqlalchemy import text

# Initialize extensions (will be bound to app in create_app)
db = SQLAlchemy()
login_manager = LoginManager()
logger = logging.getLogger('fittrack')


def create_app(config_name='development'):
    """
    Application factory pattern
    
    Args:
        config_name: 'development' or 'production'
    
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    from backend.config import get_config
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configure CORS
    CORS(app, 
         resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}},
         supports_credentials=True)
    
    # Configure login manager
    login_manager.login_view = 'api.login'
    login_manager.login_message_category = 'error'
    
    # Setup logging
    _setup_logging(app)
    
    # Register blueprints
    from backend.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Assign a per-request id for easier troubleshooting
    @app.before_request
    def _assign_request_id():
        try:
            rid = str(uuid.uuid4())
            g.request_id = rid
        except Exception:
            g.request_id = None

    @app.after_request
    def _add_request_id_header(response):
        try:
            rid = getattr(g, 'request_id', None)
            if rid:
                response.headers['X-Request-ID'] = rid
        except Exception:
            pass
        return response

    # Serve a basic favicon to avoid 500 noise from browsers requesting /favicon.ico
    @app.route('/favicon.ico')
    def favicon():
        # Serve a real favicon if available in instance/static, otherwise 204
        try:
            static_dir = os.path.join(app.instance_path, 'static')
            ico_path = os.path.join(static_dir, 'favicon.ico')
            if os.path.exists(ico_path):
                from flask import send_file
                return send_file(ico_path, mimetype='image/x-icon')
        except Exception:
            pass
        return ('', 204)
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from backend.database_models import User
        return User.query.get(int(user_id))
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'ok': True,
            'message': 'FitTrack Backend API',
            'version': '2.0',
            'endpoints': '/api'
        })
    
    # Health check endpoint
    @app.route('/health')
    def health():
        try:
            # Test database connection
            with app.app_context():
                db.session.execute(text('SELECT 1'))
            return jsonify({'status': 'healthy', 'database': 'connected'})
        except Exception as e:
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 500
    
    # Global error handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Global exception handler with logging"""
        tb = format_exc()
        # Include request id in the logs for traceability
        rid = getattr(g, 'request_id', None)
        if rid:
            logger.exception(f'Unhandled exception (rid={rid}): {str(e)}')
        else:
            logger.exception(f'Unhandled exception: {str(e)}')
        
        # Log to file as fallback
        try:
            log_path = os.path.join(app.instance_path, 'error.log')
            with open(log_path, 'a', encoding='utf-8') as fh:
                fh.write(f"=== {datetime.utcnow().isoformat()} UTC ===\n")
                fh.write(tb)
                fh.write("\n\n")
        except Exception:
            pass
        
        # Return JSON for API routes and include request id so client can report it
        if request.path.startswith('/api'):
            payload = {'ok': False, 'error': 'Internal Server Error'}
            rid = getattr(g, 'request_id', None)
            if rid:
                payload['request_id'] = rid
            return jsonify(payload), 500
        
        return 'Internal Server Error', 500
    
    # Create database tables
    with app.app_context():
        _init_database(app)

        # Ensure instance/static and place favicon.ico if a base64 file exists
        try:
            static_dir = os.path.join(app.instance_path, 'static')
            os.makedirs(static_dir, exist_ok=True)
            b64_src = os.path.join(os.path.dirname(__file__), 'static', 'favicon.ico.b64')
            ico_dest = os.path.join(static_dir, 'favicon.ico')
            if os.path.exists(b64_src) and not os.path.exists(ico_dest):
                import base64
                with open(b64_src, 'rb') as f:
                    b64 = f.read()
                try:
                    data = base64.b64decode(b64)
                    with open(ico_dest, 'wb') as w:
                        w.write(data)
                    logger.info('Wrote favicon to instance static directory')
                except Exception as e:
                    logger.warning(f'Could not write favicon: {str(e)}')
        except Exception:
            pass
    
    return app


def _setup_logging(app):
    """Configure application logging"""
    log_path = os.path.join(app.instance_path, 'error.log')
    
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    )
    
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger.addHandler(file_handler)
    
    app.logger.addHandler(file_handler)


def _init_database(app):
    """Initialize database schema"""
    try:
        db.create_all()
        
        # Ensure all columns exist (migration compatibility)
        _ensure_schema_columns()
        
        logger.info('Database initialized successfully')
    except Exception as e:
        logger.error(f'Database initialization failed: {str(e)}')


def _ensure_schema_columns():
    """Ensure all required columns exist (backward compatibility)"""
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        # Get existing columns in user table
        existing_cols = []
        try:
            existing_cols = [col['name'] for col in inspector.get_columns('user')]
        except Exception:
            return
        
        # Define required columns with their ALTER statements
        required_columns = {
            'email': "ALTER TABLE user ADD COLUMN email VARCHAR(255)",
            'oauth_provider': "ALTER TABLE user ADD COLUMN oauth_provider VARCHAR(50)",
            'oauth_sub': "ALTER TABLE user ADD COLUMN oauth_sub VARCHAR(255)",
            'created_at': "ALTER TABLE user ADD COLUMN created_at DATETIME",
            'age': "ALTER TABLE user ADD COLUMN age INTEGER",
            'height_cm': "ALTER TABLE user ADD COLUMN height_cm FLOAT",
            'weight_kg': "ALTER TABLE user ADD COLUMN weight_kg FLOAT"
        }
        
        # Add missing columns
        for col_name, alter_stmt in required_columns.items():
            if col_name not in existing_cols:
                try:
                    db.session.execute(text(alter_stmt))
                    logger.info(f'Added column: {col_name}')
                except Exception as e:
                    logger.warning(f'Could not add column {col_name}: {str(e)}')
        
        # Create unique index on email if it doesn't exist
        try:
            db.session.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uix_user_email ON user(email)"))
        except Exception:
            pass
        
        db.session.commit()
    except Exception as e:
        logger.error(f'Schema migration failed: {str(e)}')
        db.session.rollback()
