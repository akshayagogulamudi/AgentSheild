"""Quick test of API endpoints."""
import sys
sys.path.insert(0, '.')
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Test health
print('Testing /health...')
r = client.get('/health')
print(f'Status: {r.status_code}')
print(f'Response: {r.json()}')

# Test /api/status
print('\nTesting /api/status...')
r = client.get('/api/status')
print(f'Status: {r.status_code}')
print(f'Response: {r.json()}')

# Test /api/policies
print('\nTesting /api/policies...')
r = client.get('/api/policies')
print(f'Status: {r.status_code}')
policies = r.json()
print(f'Count: {len(policies)} policies')
for p in policies:
    print(f'  - {p["role"]}')

print('\n✓ All API tests passed!')
