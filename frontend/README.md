# Frontend (Streamlit)

This folder contains the Streamlit frontend for FitTrack.

## Run locally

1. Install dependencies (recommended in a venv):

   pip install -r ../requirements.txt

2. Run Streamlit:

   streamlit run frontend/streamlit_app.py

   The UI will be available at http://localhost:8501

3. API base

By default the app uses `http://localhost:5000/api`. To override this, either:

- Set a secret in Streamlit Cloud (key: `api_base`), or
- Modify `API_BASE` at the top of `frontend/streamlit_app.py`.

## Notes

- The Streamlit app communicates with the Flask backend over HTTP. Make sure the backend is running (default `http://localhost:5000`).
- If you use Google OAuth, ensure the backend has `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` set in environment variables.
