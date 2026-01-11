# 🔍 Troubleshooting Google OAuth v Dockeru

## Problém: Po Google přihlášení se zobrazí landing page

### Příčiny a řešení:

#### 1. Session cookies nejsou správně nastaveny

**Symptomy:**
- Po úspěšném Google OAuth se objeví landing page místo dashboardu
- V URL se na chvíli objeví `?auth=success&user_id=X`, pak zmizí
- Frontend volá `/oauth/session`, ale session není vytvořena

**Řešení:**

Zkontrolujte logy backendu:
```powershell
docker-compose logs -f backend
```

Měli byste vidět:
```
[OAuth] Session created for user id: X
```

Pokud ne, problém je v session cookies.

#### 2. CORS není správně nakonfigurován

**Kontrola:**
```powershell
# Zkontrolujte .env soubor
cat .env
```

Ujistěte se, že máte:
```
FRONTEND_URL=http://localhost:8501
BACKEND_URL=http://localhost:5000
CORS_ORIGINS=http://localhost:8501,http://127.0.0.1:8501
```

#### 3. Google OAuth credentials nejsou správně nastaveny

**Kontrola Google Cloud Console:**

1. Jděte na https://console.cloud.google.com/
2. Vyberte váš projekt
3. APIs & Services → Credentials
4. Zkontrolujte OAuth 2.0 Client ID
5. **Authorized redirect URIs** musí obsahovat:
   ```
   http://localhost:5000/api/google/callback
   ```

**Kontrola .env:**
```
GOOGLE_CLIENT_ID=váš-client-id
GOOGLE_CLIENT_SECRET=váš-client-secret
```

**Kontrola .secrets/google_client_secret:**
```powershell
cat .secrets\google_client_secret
```

#### 4. Debug režim

Zapněte debug výpisy v Docker logs:

```powershell
docker-compose logs -f
```

Pak se pokuste přihlásit přes Google a sledujte:
1. Frontend: `[OAuth] POSTing to /oauth/session with user_id=X`
2. Backend: `[OAuth] Session created for user id: X`
3. Frontend: `Přihlášení přes Google úspěšné!`

### Manuální test OAuth flow:

1. **Otevřete backend v prohlížeči:**
   ```
   http://localhost:5000/api/google/login
   ```
   
2. **Měli byste být přesměrováni na Google přihlášení**

3. **Po úspěšném přihlášení byste měli být přesměrováni na:**
   ```
   http://localhost:8501/?auth=success&user_id=X
   ```

4. **Frontend by měl zavolat:**
   ```
   POST http://localhost:5000/api/oauth/session
   Body: {"user_id": X}
   ```

5. **Odpověď by měla být:**
   ```json
   {
     "ok": true,
     "user": {
       "id": X,
       "username": "...",
       ...
     }
   }
   ```

### Častá řešení:

#### Reset session a restart:

```powershell
# Zastavit kontejnery
docker-compose down

# Smazat session cookies v prohlížeči (F12 → Application → Cookies → Clear)

# Spustit znovu
docker-compose up -d

# Sledovat logy
docker-compose logs -f
```

#### Vyčistit úplně vše:

```powershell
# Zastavit a smazat vše
docker-compose down -v

# Smazat databázi
Remove-Item instance\db.sqlite3 -ErrorAction SilentlyContinue

# Znovu build a start
docker-compose up -d --build

# Sledovat logy
docker-compose logs -f
```

#### Test pomocí curl:

Po úspěšném Google OAuth (když máte user_id):

```powershell
# Test vytvoření session
curl -X POST http://localhost:5000/api/oauth/session `
  -H "Content-Type: application/json" `
  -d '{"user_id": 1}' `
  -c cookies.txt

# Test /me s session cookie
curl http://localhost:5000/api/me `
  -b cookies.txt
```

### Známé omezení:

V současné konfiguraci Docker běží na `localhost`, což znamená:
- Backend: `http://localhost:5000`
- Frontend: `http://localhost:8501`

Pro správnou funkčnost session cookies v produkci byste měli:
1. Používat HTTPS
2. Nastavit `SESSION_COOKIE_SECURE=true`
3. Nastavit správnou doménu pro cookies

### Alternativní přihlášení:

Pokud Google OAuth nefunguje, můžete:

1. **Použít klasickou registraci:**
   - Klikněte na "Registrace"
   - Vytvořte účet s uživatelským jménem a heslem

2. **Použít admin účet:**
   - Username: `admin`
   - Password: (zkontrolujte `ADMIN_PASSWORD` v `.env`, výchozí: `Admin&4`)

## Rychlá diagnostika:

```powershell
# 1. Jsou kontejnery běžící?
docker-compose ps

# 2. Jsou nějaké chyby v logu?
docker-compose logs --tail=50 backend
docker-compose logs --tail=50 frontend

# 3. Funguje backend API?
curl http://localhost:5000/health

# 4. Je Google OAuth správně nakonfigurován?
docker exec fittrack_backend env | grep GOOGLE
```
