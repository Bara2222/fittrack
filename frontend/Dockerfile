FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copy frontend requirements and install
COPY frontend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy entire project (needed for imports to work correctly)
COPY . /app/

# Copy Streamlit config
COPY frontend/.streamlit /app/.streamlit

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Streamlit listens on 8501 by default
EXPOSE 8501

# Change to frontend directory and run streamlit
CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
