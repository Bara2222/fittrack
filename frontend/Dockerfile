FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY frontend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy frontend source
COPY frontend /app/frontend

# Copy Streamlit config (secrets) into image so Streamlit finds them at runtime
COPY frontend/.streamlit /app/.streamlit

ENV PYTHONUNBUFFERED=1

# Streamlit listens on 8501 by default
EXPOSE 8501

CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
