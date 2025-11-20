# backend/run.py
"""
Backend Server Entry Point
Run the Flask application
"""
import os
from backend import app

if __name__ == '__main__':
    # Get configuration from environment
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"""
╔══════════════════════════════════════╗
║   FitTrack Backend API Server        ║
║   Running on: http://localhost:{port}   ║
╚══════════════════════════════════════╝
    """)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
