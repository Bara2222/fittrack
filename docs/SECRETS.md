# Managing Secrets for Fittrack

This document explains how to avoid committing secrets to the repository and how to wire Docker secrets into the `docker-compose` setup for local development.

## Goals
- Remove actual secrets from the repository
- Use Docker Compose `secrets` to mount secret files into the container at `/run/secrets/...`

## What I changed
- Replaced the real `GOOGLE_CLIENT_SECRET` value in `.env` with a placeholder.
- Added `.secrets/google_client_secret.example` as a placeholder file (do not commit real secrets).
- Updated `docker-compose.yml` to declare the `google_client_secret` secret and mount it into the `backend` service.
- Updated `backend/config.py` to read `GOOGLE_CLIENT_SECRET` from an env var or from a secret file (`/run/secrets/google_client_secret`).
- Added `.secrets/` to `.gitignore` to avoid committing real secret files.

## How to set up locally (recommended)

1. Create the `.secrets` directory at the project root (if not already present):

```powershell
cd C:\Users\student\Desktop\PROJEKT\fittrack
mkdir .secrets
```

2. Create the secret file with the actual client secret (do NOT commit this file):

```powershell
Set-Content -Path .secrets\google_client_secret -Value "YOUR_REAL_GOOGLE_CLIENT_SECRET"
```

3. Confirm the file is present and ignored by git:

```powershell
git status --ignored
```

4. Bring up the backend (it will mount the secret to `/run/secrets/google_client_secret`):

```powershell
docker-compose up -d --force-recreate backend
```

5. The backend will prefer `GOOGLE_CLIENT_SECRET` from the environment. If not present, it will read `/run/secrets/google_client_secret`.

## Notes about Docker Compose and Swarm
- Compose `secrets` are supported by Compose versions and by Docker Swarm mode. The configuration used mounts the content of the named file into the container at `/run/secrets/<name>` (Compose creates a temporary secret from the file). This works for local development with recent Compose versions; if you use `docker stack deploy` in swarm, use `docker secret create`.

## Rotating the Google client secret
1. In the Google Cloud Console, go to `APIs & Services` -> `Credentials`.
2. Find your OAuth 2.0 Client ID, click it, and use the `Reset secret` or `Create new secret` option.
3. Replace the contents of `.secrets/google_client_secret` with the new secret and restart the backend:

```powershell
Set-Content -Path .secrets\google_client_secret -Value "NEW_GOOGLE_CLIENT_SECRET"
docker-compose up -d --force-recreate backend
```

## If you prefer environment variables
If you prefer to use environment variables (not recommended for production), set `GOOGLE_CLIENT_SECRET` in the environment or in your host's environment and ensure `.env` is not tracked in Git.
