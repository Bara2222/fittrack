# FitTrack Docker OAuth Setup

## 🔧 Nastavení Google OAuth pro Docker

Když spouštíte FitTrack přes Docker, musíte správně nakonfigurovat Google OAuth redirect URIs.

### 1. Google Cloud Console nastavení

Přejděte na [Google Cloud Console](https://console.cloud.google.com/):

1. **Vyberte nebo vytvořte projekt**
2. **Zapněte Google+ API** (nebo Google Identity API)
3. **Jděte do "Credentials" → "OAuth 2.0 Client IDs"**
4. **Pro vaši OAuth aplikaci přidejte tyto Authorized redirect URIs:**

```
http://localhost:5000/api/google/callback
http://127.0.0.1:5000/api/google/callback
```

### 2. Environment Variables

Docker automaticky používá správné environment variables. V `.env` souboru:

```bash
# Google OAuth credentials
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here

# URLs for Docker environment  
FRONTEND_URL=http://localhost:8501
BACKEND_URL=http://localhost:5000
```

### 3. Docker konfigurace

Docker-compose automaticky nastavuje:
- `API_BASE=http://backend:5000/api` (interní Docker komunikace)
- `API_BASE_EXTERNAL=http://localhost:5000/api` (externí browser přístupy)

### 4. OAuth Flow v Dockeru

1. **User klikne "Přihlásit se přes Google"** na http://localhost:8501
2. **Browser přesměrován na** `http://localhost:5000/auth/google`
3. **Google autorizace** → přesměrování na Google
4. **Google callback** → `http://localhost:5000/api/google/callback`
5. **Backend zpracuje OAuth** a přesměruje na `http://localhost:8501/?auth=success`

### 3. Spuštění Docker kontejnerů

```bash
# Build a spuštění
docker-compose up --build -d

# Kontrola statusu
docker-compose ps

# Zobrazení logů
docker-compose logs -f
```

### 4. Testování OAuth

1. **Otevřete aplikaci:** http://localhost:8501
2. **Klikněte na "Přihlásit se přes Google"**
3. **OAuth proces:** 
   - Přesměrování na Google → 
   - Autorizace → 
   - Callback na backend → 
   - Návrat do frontendu

### 5. Řešení problémů

#### Problem: "redirect_uri_mismatch"
- **Řešení:** Zkontrolujte, že máte správné URIs v Google Cloud Console
- **Správné URIs:** `http://localhost:5000/api/google/callback`

#### Problem: Frontend nedostává callback
- **Řešení:** Zkontrolujte `FRONTEND_URL` environment variable
- **Musí být:** `http://localhost:8501`

#### Problem: Backend není dostupný
```bash
# Zkontrolujte status kontejnerů
docker-compose ps

# Zkontrolujte logy backendu
docker-compose logs backend
```

### 6. Produkční nasazení

Pro produkci změňte v `.env`:

```bash
FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://api.yourdomain.com
```

A v Google Cloud Console přidejte:
```
https://api.yourdomain.com/api/google/callback
```

---

## 📝 Quick Commands

```bash
# Restart pouze backend (po změně OAuth nastavení)
docker-compose restart backend

# Restart celé aplikace
docker-compose down && docker-compose up -d

# Rebuild po změnách kódu
docker-compose build --no-cache && docker-compose up -d
```