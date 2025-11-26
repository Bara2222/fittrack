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

# Copy backend source
COPY backend /app/backend

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=backend.run
ENV PORT=5000

# Expose port for Flask
EXPOSE 5000

# Run as module so package imports resolve correctly
CMD ["python", "-m", "backend.run"]
