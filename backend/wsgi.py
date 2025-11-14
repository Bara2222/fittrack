from backend import app as application

# Gunicorn entrypoint: gunicorn -w 2 -b 0.0.0.0:8000 backend.wsgi:application
