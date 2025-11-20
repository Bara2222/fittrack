# 💪 FitTrack - Clean Architecture Edition# 💪 FitTrack - Fitness Tracking Application



Moderní fitness tracking aplikace s **kompletně odděleným** backendem (Flask REST API) a frontendem (Streamlit).Moderní fitness tracking aplikace s rozděleným frontendem (Streamlit) a backendem (Flask API).



## 🏗️ Architektura## 🚀 Funkce



```- ✅ **Registrace a přihlášení** - Klasická registrace nebo Google OAuth

FitTrack/- 💪 **Správa tréninků** - Vytváření, editace a mazání tréninků

├── backend/              # 🔧 Flask REST API Server- 🏋️ **Evidence cviků** - Detailní záznamy o cvicích, sériích, opakováních a váhách

│   ├── __init__.py      # Package initialization- 📊 **Dashboard** - Přehled statistik a posledních tréninků

│   ├── app.py           # Flask app factory- ⚡ **Rychlý start** - Předpřipravené tréninky pro začátečníky, pokročilé a experty

│   ├── config.py        # Configuration management- 📚 **Katalog cviků** - Inspirace pro vaše tréninky

│   ├── database_models.py # SQLAlchemy ORM models- 📥 **Export dat** - Stažení všech dat do CSV formátu

│   ├── api_routes.py    # REST API endpoints- ⚙️ **Admin panel** - Správa uživatelů (pouze pro adminy)

│   ├── run.py           # Server entry point- 🔐 **Google OAuth** - Jednoduché přihlášení přes Google účet

│   ├── requirements.txt # Backend dependencies

│   └── instance/        # SQLite database (gitignored)## 📋 Požadavky

│

├── frontend/            # 🎨 Streamlit UI Application- Python 3.8+

│   ├── streamlit_app.py # Main UI application- Git (pro klonování repozitáře)

│   └── requirements.txt # Frontend dependencies

│## 🔧 Instalace

├── .env                 # 🔐 Environment variables

├── .gitignore          # Git ignore rules### 1. Naklonujte repozitář

└── README.md           # This file

``````bash

git clone https://github.com/davidandel/FitTrack.git

## ✨ Funkcecd FitTrack

```

- ✅ **Autentizace** - Registrace, přihlášení, Google OAuth

- 💪 **Správa tréninků** - Vytváření, editace, mazání### 2. Vytvořte a aktivujte virtuální prostředí

- 🏋️ **Evidence cviků** - Série, opakování, váhy

- 📊 **Dashboard** - Statistiky a přehled**Windows PowerShell:**

- ⚡ **Rychlý start** - Předpřipravené tréninky```powershell

- 📚 **Katalog cviků** - Databáze cvičenípython -m venv .venv

- 📥 **Export dat** - CSV export.\.venv\Scripts\Activate.ps1

- ⚙️ **Admin panel** - Správa uživatelů```



## 🚀 Rychlý start**Linux/Mac:**

```bash

### 1. Instalacepython -m venv .venv

source .venv/bin/activate

```bash```

# Naklonujte repozitář

git clone https://github.com/davidandel/FitTrack.git### 3. Nainstalujte závislosti

cd FitTrack

```bash

# Vytvořte virtuální prostředípip install -r requirements.txt

python -m venv .venv```



# Windows### 4. Konfigurace (.env soubor)

.\.venv\Scripts\Activate.ps1

Soubor `.env` už obsahuje základní konfiguraci včetně Google OAuth credentials. Pro produkční použití změňte:

# Linux/Mac

source .venv/bin/activate```env

```GOOGLE_CLIENT_ID="your_google_client_id"

GOOGLE_CLIENT_SECRET="your_google_client_secret"

### 2. Backend setupSECRET_KEY="your_secret_key"

ADMIN_PASSWORD="your_admin_password"

```bash```

# Instalace backend dependencies

cd backend### 5. Inicializace databáze

pip install -r requirements.txt

cd ..Databáze se vytvoří automaticky při prvním spuštění, nebo můžete spustit migrace:

```

```bash

Vytvořte `.env` soubor v kořenovém adresáři:python -m alembic upgrade head

```

```env

# Flask Configuration## 🚀 Spuštění aplikace

SECRET_KEY=your-secret-key-change-in-production

FLASK_ENV=development### Backend (Flask API)



# Admin CredentialsV hlavním terminálu:

ADMIN_PASSWORD=Admin&4

```bash

# Google OAuth (optional)python app.py

GOOGLE_CLIENT_ID=your-google-client-id```

GOOGLE_CLIENT_SECRET=your-google-client-secret

API bude dostupné na `http://localhost:5000`

# CORS

CORS_ORIGINS=http://localhost:8501,http://127.0.0.1:8501### Frontend (Streamlit)

```

V druhém terminálu:

### 3. Spuštění Backend serveru

```bash

```bashstreamlit run frontend/streamlit_app.py

cd backend```

python run.py

```Streamlit UI bude dostupné na `http://localhost:8501`



Backend API běží na: **http://localhost:5000**## 📁 Struktura projektu



### 4. Spuštění Frontend aplikace```

FitTrack/

V **novém terminálu**:├── backend/           # Flask API blueprinty

│   ├── __init__.py

```bash│   └── api.py        # REST API endpointy

# Aktivujte virtuální prostředí├── frontend/          # Streamlit frontend

.\.venv\Scripts\Activate.ps1  # Windows│   └── streamlit_app.py

├── migrations/        # Alembic database migrations

# Instalace frontend dependencies├── templates/         # Flask HTML templates (legacy web UI)

cd frontend├── instance/          # SQLite database (gitignored)

pip install -r requirements.txt├── app.py            # Flask aplikace + API registrace

├── auth.py           # Autentizace a HTML routes

# Spuštění Streamlit├── models.py         # SQLAlchemy databázové modely

streamlit run streamlit_app.py├── forms.py          # WTForms formuláře

```├── oauth.py          # Google OAuth konfigurace

├── requirements.txt  # Python závislosti

Frontend UI běží na: **http://localhost:8501**├── .env             # Konfigurace (Google OAuth, secret keys)

└── README.md        # Tento soubor

## 🔌 API Endpoints```



### Authentication## 🔐 Google OAuth nastavení

```

POST   /api/register          # Registrace1. Jděte na [Google Cloud Console](https://console.cloud.google.com/)

POST   /api/login             # Přihlášení2. Vytvořte nový projekt nebo vyberte existující

POST   /api/logout            # Odhlášení3. Aktivujte Google+ API

GET    /api/me                # Aktuální uživatel4. Vytvořte OAuth 2.0 credentials (Web application)

GET/POST /api/profile         # Profil5. Přidejte authorized redirect URIs:

```   - `http://localhost:5000/auth/google/callback`

   - `http://127.0.0.1:5000/auth/google/callback`

### Workouts6. Zkopírujte Client ID a Client Secret do `.env` souboru

```

GET    /api/workouts          # Seznam tréninků## 🔌 API Endpointy

GET    /api/workouts/<id>     # Detail

POST   /api/workouts          # Vytvoření### Autentizace

DELETE /api/workouts/<id>     # Smazání- `POST /api/register` - Registrace nového uživatele

```- `POST /api/login` - Přihlášení

- `POST /api/logout` - Odhlášení

### Exercises- `GET /api/me` - Informace o přihlášeném uživateli

```- `GET /api/google/login` - Google OAuth URL

POST   /api/exercises/<workout_id>/add  # Přidat cvik- `GET /api/google/callback` - Google OAuth callback

DELETE /api/exercises/<id>              # Smazat cvik

GET    /api/catalog                     # Katalog cviků### Tréninky

```- `GET /api/workouts` - Seznam tréninků

- `GET /api/workouts/<id>` - Detail tréninku

### Utils- `POST /api/workouts` - Vytvoření tréninku

```- `DELETE /api/workouts/<id>` - Smazání tréninku

GET    /api/stats                    # Statistiky

POST   /api/quickstart/<level>       # Rychlý start### Cviky

GET    /api/export/csv               # Export CSV- `POST /api/exercises/<workout_id>/add` - Přidání cviku

GET    /api/admin/users              # Admin panel- `DELETE /api/exercises/<id>` - Smazání cviku

```- `GET /api/catalog` - Katalog doporučených cviků



## 🛠️ Technologie### Ostatní

- `GET /api/stats` - Statistiky uživatele

### Backend- `POST /api/quickstart/<level>` - Rychlý start tréninku

- Flask 3.0, SQLAlchemy 2.0, Flask-Login, Flask-CORS- `GET /api/export/csv` - Export do CSV

- Authlib (OAuth), Werkzeug (Security)- `GET /api/admin/users` - Admin panel (pouze pro adminy)



### Frontend## 👤 Výchozí admin účet

- Streamlit 1.29, Requests, Pandas

- Username: `admin`

### Database- Password: `Admin&4` (nebo hodnota z `.env`)

- SQLite (dev) / PostgreSQL (production)

## 🛠️ Technologie

## 🔐 Google OAuth Setup

**Backend:**

1. [Google Cloud Console](https://console.cloud.google.com/)- Flask - Web framework

2. Vytvořte projekt → OAuth 2.0 credentials- Flask-SQLAlchemy - ORM

3. Authorized redirect: `http://localhost:5000/api/google/callback`- Flask-Login - Session management

4. Zkopírujte Client ID/Secret do `.env`- Authlib - Google OAuth

- Alembic - Database migrations

## 📝 Clean Architecture- Flask-CORS - API CORS support



- ✅ Separace Backend/Frontend**Frontend:**

- ✅ RESTful API- Streamlit - Modern Python web framework

- ✅ Input Validation- Pandas - Data manipulation

- ✅ Error Handling & Logging- Requests - HTTP client

- ✅ Security (Password hashing, CORS)

- ✅ Factory Pattern**Database:**

- SQLite (dev) / PostgreSQL (production ready)

## 👨‍💻 Author

## 📝 Poznámky

**David Anděl** - [GitHub](https://github.com/davidandel)

- Streamlit komunikuje s Flask API přes session cookies

## 📄 License- Pro produkční nasazení doporučujeme přejít na JWT tokeny

- Původní Flask HTML UI zůstává funkční na hlavní URL

MIT- Streamlit frontend běží na samostatném portu (8501)


## 🤝 Příspěvky

Pull requesty jsou vítány! Pro větší změny prosím nejdřív otevřete issue.

## 📄 Licence

MIT

## 👨‍💻 Autor

David Anděl - [GitHub](https://github.com/davidandel)# Maturitní projekt
# **Závěrečný projekt IT4 – SmartTrainer**

**Aplikace pro tvorbu a sledování tréninkových plánů**

---

## 🔍 **Popis projektu**

**SmartTrainer** je interaktivní aplikace zaměřená na uživatele, kteří si chtějí vytvářet vlastní tréninkové plány, sledovat svůj progres a mít přehled o svých aktivitách. Cílem je vytvořit moderní, uživatelsky přívětivý nástroj dostupný na mobilních zařízeních nebo ve webovém prohlížeči.

---

## 🎯 **Cíle projektu**

* Navrhnout a vytvořit přehlednou a intuitivní aplikaci pro plánování tréninků.
* Umožnit uživatelům personalizovat si své tréninky dle:

  * obtížnosti (začátečník, pokročilý, expert),
  * typu cvičení (kardio, síla, protažení atd.),
  * časových možností.
* Poskytnout databázi cviků s informacemi jako:

  * název, popis, kategorie (typ cviku), video nebo obrázek, doporučený počet opakování nebo čas.
* Implementovat časovač pro řízení tréninkových jednotek (intervaly, pauzy).
* Zajistit historii tréninků a statistiky – sledování pokroku, opakování tréninků.
* Zavést uživatelskou autentizaci (registrace/přihlášení) a ukládání dat v cloudu.
* Optimalizovat UI pro mobilní i desktopová zařízení (responzivní design).

---

## 🔧 **Hlavní funkce aplikace**

1. ### **Registrace a přihlášení**

   * Vytvoření účtu / přihlášení.
   * Ukládání osobních tréninků, historie a statistik.

2. ### **Tvorba tréninkových plánů**

   * Výběr cviků z databáze (název, popis, obrázek/video).
   * Možnost zadat:

     * Počet sérií, počet opakování, délku trvání (pro cviky typu plank apod.).

3. ### **Nastavení obtížnosti**

   * Výběr úrovně: **Začátečník / Pokročilý / Expert**.
   * Úroveň ovlivňuje:

     * Počet cviků, série, délku pauzy, intenzitu tréninku.

4. ### **Časovač (Timer)**

   * Spouštění odpočítávání mezi sériemi a cviky.
   * Možnost **pauzy / restartu** během tréninku.
   * Režim pro **HIIT** a **kruhové tréninky**.

5. ### **Historie tréninků a statistiky**

   * Záznam: datum, délka tréninku, obtížnost, dokončené tréninky.
   * Možnost zopakovat předchozí trénink jedním kliknutím.
   * Statistické grafy pokroku (volitelně).

6. ### **Přednastavené šablony tréninků**

   * Rychlý výběr hotových plánů:

     * „Celé tělo“, „Domácí HIIT“, „Protažení po běhu“, atd.

---

## 🗓 **Harmonogram práce**

| Fáze | Popis                              | Termín  |
| ---- | ---------------------------------- | ------- |
| 1.   | Návrh UI/UX, struktura databáze    |         |
| 2.   | Autentizace uživatelů              |         |
| 3.   | Databáze cviků, tvorba tréninku    |         |
| 4.   | Implementace časovače              |         |
| 5.   | Historie, statistiky               |         |
| 6.   | Testování a opravy                 |         |
| 7.   | Finalizace, dokumentace, odevzdání |         |

---

## 🧠 **Co se chci naučit**

* **Práce s databází** (strukturování, CRUD operace)
* **Autentizace uživatelů**
* **Návrh a vývoj UI/UX**
* **Práce s časem v aplikaci** (časovač, délka tréninku)
* Volitelně: základy mobilního vývoje (Flutter) 

---

## 🛠 **Použité technologie**
* **Frontend:** Flutter

### ✅ Doporučená varianta: **Mobilní aplikace**

* **Frontend:** Streamlit
* **Backend:** Firebase (Firestore + Auth) Flask
* **Bonus:** Možnost přehrávání videí u cviků

---

## 📚 **Zdroje a inspirace**

* Open-source workout aplikace na GitHubu
* YouTube tutoriály pro tvorbu Flutter aplikací
* Firebase dokumentace
* Figma / Canva pro návrh UI
* Weby jako [Exercisedb.io](https://exercisedb.io) – pro inspiraci u databáze cviků

---

# FitTrack - Průvodce nastavením a spuštěním

Tento dokument popisuje, jak nakonfigurovat a spustit aplikaci FitTrack, včetně nastavení Google OAuth pro přihlašování.

## 1. Požadavky

- Python 3.8+
- `pip` a `venv`

## 2. Instalace

Nejprve si vytvořte a aktivujte virtuální prostředí. V příkazovém řádku (PowerShell) spusťte:

```powershell
# Vytvoření virtuálního prostředí v adresáři .venv
python -m venv .venv

# Aktivace virtuálního prostředí
. .\.venv\Scripts\Activate.ps1
```

Poté nainstalujte všechny potřebné závislosti:

```powershell
pip install -r requirements.txt
```

## 3. Nastavení Google OAuth 2.0

Pro přihlašování přes Google je nutné získat `Client ID` a `Client Secret`.

### Krok 1: Vytvoření projektu v Google Cloud Console

1.  Přejděte na [Google Cloud Console](https://console.cloud.google.com/).
2.  Vytvořte nový projekt (nebo vyberte existující).
3.  V menu přejděte na **APIs & Services -> Credentials**.

### Krok 2: Konfigurace OAuth Consent Screen

1.  Pokud jste tak ještě neučinili, klikněte na **Configure Consent Screen**.
2.  Zvolte **External** a klikněte na **Create**.
3.  Vyplňte povinné údaje:
    -   **App name**: `FitTrack` (nebo název dle vaší volby)
    -   **User support email**: Vaše emailová adresa.
    -   **Developer contact information**: Vaše emailová adresa.
4.  Uložte a pokračujte. Na dalších stránkách (Scopes, Test Users) můžete prozatím nechat výchozí nastavení a uložit.

### Krok 3: Vytvoření OAuth 2.0 Client ID

1.  Vraťte se na stránku **Credentials**.
2.  Klikněte na **+ Create Credentials** a vyberte **OAuth client ID**.
3.  Zvolte **Application type -> Web application**.
4.  Pojmenujte klienta (např. `FitTrack Web Client`).
5.  V sekci **Authorized redirect URIs** přidejte následující dvě adresy:
    -   `http://127.0.0.1:5000/auth/google/callback`
    -   `http://localhost:5000/auth/google/callback`
6.  Klikněte na **Create**. Zobrazí se vám **Your Client ID** a **Your Client Secret**.

### Krok 4: Uložení klíčů do souboru `.env`

1.  V kořenovém adresáři projektu (`FitTrack/`) vytvořte soubor s názvem `.env`.
2.  Do tohoto souboru vložte získané klíče a také tajný klíč pro Flask:

    ```env
    # Google OAuth Keys
    GOOGLE_CLIENT_ID="VAŠE_CLIENT_ID_Z_GOOGLE_CONSOLE"
    GOOGLE_CLIENT_SECRET="VÁŠ_CLIENT_SECRET_Z_GOOGLE_CONSOLE"

    # Flask Secret Key (pro sessions a bezpečnostní tokeny)
    SECRET_KEY="dlouhy-a-velmi-tajny-nahodny-retezec"

    # Heslo pro admina (volitelné, pokud chcete jiné než výchozí)
    ADMIN_PASSWORD="nove_heslo_pro_admina"
    ```

    **Důležité:** Nahraďte zástupné texty skutečnými hodnotami. `SECRET_KEY` by měl být dlouhý a náhodný řetězec.

## 4. Spuštění aplikace

Po uložení souboru `.env` můžete aplikaci spustit. Ujistěte se, že máte stále aktivované virtuální prostředí.

```powershell
python app.py
```

Aplikace by se měla spustit a být dostupná na adrese [http://127.0.0.1:5000](http://127.0.0.1:5000). Nyní by mělo přihlašování přes Google fungovat správně.

## 5. Databáze

Aplikace standardně používá SQLite databázi, která se automaticky vytvoří v souboru `instance/db.sqlite3`. Migrace databáze jsou spravovány pomocí Alembic.




