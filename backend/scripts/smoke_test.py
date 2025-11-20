import sys, os
# Ensure repository root is on sys.path so 'import backend' works when running from scripts/
sys.path.insert(0, os.getcwd())
import backend
from backend import db
app = backend.app
with app.app_context():
    db.create_all()
    print('Created tables')

client = app.test_client()
r = client.post('/api/register', json={'username':'testuser_smoke','password':'testpass123'})
print('POST /api/register =>', r.status_code, r.get_json())
r2 = client.post('/api/login', json={'username':'testuser_smoke','password':'testpass123'})
print('POST /api/login =>', r2.status_code, r2.get_json())
r3 = client.get('/api/me')
print('GET /api/me =>', r3.status_code, r3.get_json())
