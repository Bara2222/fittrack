FROM python:3.11-slim

WORKDIR /app

# Install system deps for common Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy entire project (needed for imports to work correctly)
COPY . /app/

# Create instance directory for database
RUN mkdir -p /app/instance

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV FLASK_APP=backend.run
ENV PORT=5000

# Expose port for Flask
EXPOSE 5000

# Run Flask application
CMD ["python", "-c", "import sys; sys.path.append('.'); from backend.run import app; app.run(debug=False, host='0.0.0.0', port=5000)"]
