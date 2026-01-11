# 🐳 Docker Příkazy pro FitTrack

## Základní příkazy

### Spustit aplikaci
```powershell
docker-compose up -d
```

### Zastavit aplikaci
```powershell
docker-compose down
```

### Restartovat aplikaci
```powershell
docker-compose restart
```

### Rebuild a spuštění
```powershell
docker-compose up -d --build
```

## Zobrazení logů

### Všechny logy (live)
```powershell
docker-compose logs -f
```

### Logy backendu
```powershell
docker-compose logs -f backend
```

### Logy frontendu
```powershell
docker-compose logs -f frontend
```

### Posledních 50 řádků logů
```powershell
docker-compose logs --tail=50
```

## Stav kontejnerů

### Zobrazit běžící kontejnery
```powershell
docker-compose ps
```

### Zobrazit všechny Docker kontejnery
```powershell
docker ps -a
```

## Údržba

### Restart konkrétní služby
```powershell
docker-compose restart backend
docker-compose restart frontend
```

### Vyčistit vše včetně dat
```powershell
docker-compose down -v
```

### Smazat nepoužívané Docker objekty
```powershell
docker system prune -a
```

## Přístup do kontejneru

### Backend shell
```powershell
docker exec -it fittrack_backend /bin/bash
```

### Frontend shell
```powershell
docker exec -it fittrack_frontend /bin/bash
```

## Databáze

### Přístup k databázi (v backend kontejneru)
```powershell
docker exec -it fittrack_backend python -c "from backend.database_models import db; from backend.app import create_app; app = create_app(); app.app_context().push(); print('Tables:', db.engine.table_names())"
```

### Reset databáze
```powershell
docker-compose down -v
Remove-Item instance\db.sqlite3 -ErrorAction SilentlyContinue
docker-compose up -d
```

## Troubleshooting

### Zobrazit chyby při buildu
```powershell
docker-compose up --build
```

### Kontrola síťového připojení
```powershell
docker network inspect fittrack_fittrack_network
```

### Zkontrolovat environment variables
```powershell
docker exec fittrack_backend env
docker exec fittrack_frontend env
```

## Přístup k aplikaci

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:5000
- **API Docs**: http://localhost:5000/api
