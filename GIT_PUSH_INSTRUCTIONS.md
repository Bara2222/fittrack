# 📦 Návod na push do GitHub repozitáře

Tento soubor obsahuje příkazy pro nahrání projektu na GitHub.

## ⚠️ Před pushnutím

1. **Zkontrolujte .env soubor** - Ujistěte se, že neobsahuje citlivé údaje, které nechcete sdílet
2. **Zkontrolujte .gitignore** - Soubor je už nastaven, ale zkontrolujte že zahrnuje všechny potřebné položky

## 🔧 Instalace Git (pokud není nainstalovaný)

### Windows
Stáhněte a nainstalujte z: https://git-scm.com/download/win

### Linux
```bash
sudo apt-get install git  # Debian/Ubuntu
sudo yum install git       # CentOS/RHEL
```

### Mac
```bash
brew install git
```

## 📤 Příkazy pro push na GitHub

### 1. Inicializace Git repozitáře (pokud ještě není)

```bash
cd "C:\Users\Admin\Downloads\FitTrack-main (2)\FitTrack-main"
git init
```

### 2. Přidání souborů do gitu

```bash
git add .
```

### 3. První commit

```bash
git commit -m "Initial commit: FitTrack with Streamlit frontend and Flask API backend"
```

### 4. Přidání remote repozitáře

```bash
git remote add origin https://github.com/davidandel/FitTrack.git
```

Pokud už remote existuje, odstraňte ho a přidejte znovu:
```bash
git remote remove origin
git remote add origin https://github.com/davidandel/FitTrack.git
```

### 5. Push na GitHub

Pro první push:
```bash
git branch -M main
git push -u origin main --force
```

Pro další pushe:
```bash
git push origin main
```

## 🔐 Autentizace

Při pushování budete vyzváni k zadání GitHub credentials:
- **Username**: davidandel
- **Password**: Použijte GitHub Personal Access Token (ne heslo)

### Vytvoření Personal Access Token:
1. Jděte na GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Zaškrtněte "repo" scope
4. Zkopírujte token a použijte ho místo hesla

## 📋 Checklist před pushnutím

- [ ] .env soubor obsahuje pouze demo credentials nebo je v .gitignore
- [ ] instance/ složka je v .gitignore (databáze se nepushuje)
- [ ] __pycache__ složky jsou v .gitignore
- [ ] .venv složka je v .gitignore
- [ ] README.md je aktuální
- [ ] requirements.txt obsahuje všechny závislosti

## 🔄 Update repozitáře (další změny)

```bash
git add .
git commit -m "Popis změn"
git push origin main
```

## 🌿 Práce s větvemi (optional)

```bash
# Vytvoření nové větve
git checkout -b feature/nova-funkcionalita

# Push větve
git push origin feature/nova-funkcionalita

# Přepnutí zpět na main
git checkout main
```

## ❗ Troubleshooting

### Konflikt při push
```bash
git pull origin main --rebase
git push origin main
```

### Smazání remote a přidání znovu
```bash
git remote remove origin
git remote add origin https://github.com/davidandel/FitTrack.git
git push -u origin main --force
```

### Zobrazení stavu
```bash
git status
git log --oneline
git remote -v
```

## 📝 .gitignore je už nastaven

Soubor .gitignore už obsahuje:
- Python cache soubory (__pycache__, *.pyc)
- Virtual environment (.venv, venv)
- Database soubory (instance/, *.db, *.sqlite3)
- IDE soubory (.vscode, .idea)
- Log soubory (*.log)
- OS soubory (.DS_Store, Thumbs.db)

⚠️ **DŮLEŽITÉ**: .env soubor NENÍ v .gitignore, protože obsahuje demo credentials.
Pro produkci vytvořte nový .env s vlastními credentials a NEPUSHUJTE ho!

## ✅ Po úspěšném push

Projekt bude dostupný na: https://github.com/davidandel/FitTrack

Můžete:
1. Přidat popis projektu na GitHubu
2. Přidat topics (python, flask, streamlit, fitness, oauth)
3. Povolit Issues a Discussions
4. Přidat LICENSE soubor
5. Přidat screenshots do README
