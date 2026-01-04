# 💪 FitTrack - Fitness Tracking Application

Webová aplikace vyvíjená ve Flask/Streamlit jako projekt pro sledování fitness pokroku.
Cílem je vytvořit osobní tréninkový deník s možností detailního sledování cvičení – uživatel může vytvářet tréninky, evidovat cviky, sledovat progres a analyzovat statistiky svého výkonu.

## ✨ Funkce

- ✅ **Registrace a přihlášení** - Klasická registrace nebo Google OAuth
- 💪 **Správa tréninků** - Vytváření, editace a mazání tréninků  
- 🏋️ **Evidence cviků** - Detailní záznamy o cvicích, sériích, opakováních a váhách
- 📊 **Dashboard** - Přehled statistik a posledních tréninků
- ⚡ **Rychlý start** - Předpřipravené tréninky pro začátečníky, pokročilé a experty
- 📚 **Katalog cviků** - Inspirace pro vaše tréninky
- 📈 **Pokročilé statistiky** - Interaktivní grafy pokroku s Plotly
- 📥 **Export dat** - Stažení všech dat do CSV, JSON nebo PDF formátu
- ⚙️ **Admin panel** - Správa uživatelů (pouze pro adminy)
- 🔐 **Google OAuth** - Jednoduché přihlášení přes Google účet
- 🌐 **Webové rozhraní** - Moderní responsive design s tmavým motivem

## 🏗️ Architektura

```
FitTrack/
├── backend/              # 🔧 Flask REST API Server
│   ├── __init__.py      # Package initialization
│   ├── app.py           # Flask app factory
│   ├── config.py        # Configuration management
│   ├── database_models.py # SQLAlchemy ORM models
│   ├── api_routes.py    # REST API endpoints
│   ├── run.py           # Server entry point
│   ├── requirements.txt # Backend dependencies
│   └── instance/        # SQLite database (gitignored)
│
├── frontend/            # 🎨 Streamlit UI Application
│   ├── streamlit_app.py # Main UI application
│   └── requirements.txt # Frontend dependencies
│
├── .env                 # 🔐 Environment variables
├── .gitignore          # Git ignore rules
├── docker-compose.yml  # Docker orchestration
└── README.md           # This file
```

## 🛠 Použité technologie

**Backend:**
- Flask - Python web framework
- SQLAlchemy - ORM pro databázi
- Flask-Login - Správa uživatelských relací
- Flask-CORS - Cross-Origin Resource Sharing
- SQLite - Lokální databáze
- Alembic - Database migrations
- Google OAuth - Autentizace přes Google

**Frontend:**
- Streamlit - Rychlé vytváření webových aplikací
- Plotly - Interaktivní grafy a vizualizace
- Pandas - Analýza a manipulace dat
- Requests - HTTP komunikace s backendem

**DevOps:**
- Docker & Docker Compose - Kontejnerizace
- Python 3.13 - Programovací jazyk

## 📋 Požadavky

- Python 3.8+
- Git (pro klonování repozitáře)
- Docker (volitelné, pro kontejnerové spuštění)

## 🔧 Instalace

### 1. Naklonujte repozitář

```bash
git clone https://github.com/Bara2222/fittrack.git
cd fittrack
```

### 2. Vytvořte a aktivujte virtuální prostředí

**Windows PowerShell:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Nainstalujte závislosti

```bash
pip install -r requirements.txt
```

### 4. Konfigurace (.env soubor)

Soubor `.env` už obsahuje základní konfiguraci včetně Google OAuth credentials. Pro produkční použití změňte:

```env
GOOGLE_CLIENT_ID="your_google_client_id"
GOOGLE_CLIENT_SECRET="your_google_client_secret"
SECRET_KEY="your_secret_key"
ADMIN_PASSWORD="your_admin_password"
```

### 5. Inicializace databáze

Databáze se vytvoří automaticky při prvním spuštění, nebo můžete spustit migrace:

```bash
python -m alembic upgrade head
```

## 🚀 Spuštění aplikace

### Metoda 1: Nativní Python

**Backend (Flask API)**

V hlavním terminálu:
```bash
python -c "from backend import app; app.run(host='0.0.0.0', port=5000, debug=True)"
```

API bude dostupné na `http://localhost:5000`

**Frontend (Streamlit)**

V druhém terminálu:
```bash
streamlit run frontend/streamlit_app.py --server.port 8501
```

Streamlit UI bude dostupné na `http://localhost:8501`

### Metoda 2: Docker Compose

```bash
docker-compose up --build
```

- Backend: `http://localhost:5000`
- Frontend: `http://localhost:8501`

## 📱 Použití

1. **Registrace/Přihlášení** - Vytvořte si účet nebo se přihlaste přes Google
2. **Dashboard** - Prohlédněte si přehled svých statistik
3. **Rychlý start** - Vyberte si předpřipravený trénink podle úrovně
4. **Nový trénink** - Vytvořte vlastní trénink s cviky
5. **Katalog** - Prohlédněte si dostupné cviky pro inspiraci
6. **Statistiky** - Analyzujte svůj pokrok pomocí interaktivních grafů
7. **Export** - Stáhněte si svá data v různých formátech

## 🔌 API Endpointy

### Autentizace
- `POST /api/register` - Registrace uživatele
- `POST /api/login` - Přihlášení uživatele
- `POST /api/logout` - Odhlášení uživatele
- `GET /api/google/login` - Google OAuth přihlášení

### Tréninky
- `GET /api/workouts` - Seznam tréninků
- `POST /api/workouts` - Vytvoření tréninku
- `GET /api/workouts/{id}` - Detail tréninku
- `DELETE /api/workouts/{id}` - Smazání tréninku

### Cviky
- `POST /api/exercises/{workout_id}/add` - Přidání cviku
- `DELETE /api/exercises/{id}` - Smazání cviku
- `GET /api/catalog` - Katalog cviků

### Statistiky
- `GET /api/stats` - Základní statistiky
- `GET /api/export/csv` - Export dat do CSV

### Admin
- `GET /api/admin/users` - Seznam uživatelů (pouze admin)

## 📊 Funkce statistik

- **Frekvence tréninků** - Graf tréninků v čase
- **Nejčastější cviky** - Top 10 nejprováděnějších cviků
- **Progres objemu** - Celkový tréninkový objem v kg
- **Rozdělení cviků** - Kategorizace podle typu cviku
- **Analýza sérií a opakování** - Průměrné hodnoty
- **Týdenní aktivita** - Heatmap aktivity podle dne v týdnu
- **Sledování pokroku** - Detailní analýza konkrétních cviků

## 🔐 Zabezpečení

- **Hash hesel** - Bezpečné ukládání pomocí Werkzeug
- **Flask-Login** - Správa uživatelských relací
- **CORS** - Konfigurace pro bezpečnou komunikaci
- **Google OAuth** - Alternativní bezpečná autentizace

## 📁 Struktura databáze

### User (Uživatel)
- id, username, password_hash, email
- oauth_provider, oauth_sub
- age, height_cm, weight_kg
- is_admin, created_at

### Workout (Trénink)
- id, user_id, date, note
- created_at

### Exercise (Cvik)
- id, workout_id, name
- sets, reps, weight
- created_at

## 🚀 Deployment

### Docker Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

1. Nastavte produkční proměnné prostředí
2. Použijte Gunicorn pro backend
3. Reverse proxy přes Nginx
4. SSL certifikát pro HTTPS

## 🤝 Přispívání

1. Fork repozitář
2. Vytvořte feature branch (`git checkout -b feature/amazing-feature`)
3. Commit změny (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Otevřete Pull Request

## 📝 Licence

Tento projekt je licencován pod MIT licencí. Viz `LICENSE` soubor pro detaily.

## 👨‍💻 Autor

**Bara2222** - [GitHub](https://github.com/Bara2222)

## 📞 Podpora

Pokud máte problémy nebo dotazy:
- Otevřete issue na GitHubu
- Kontaktujte autora

---

**FitTrack** - Váš spolehlivý tréninkový partner! 💪