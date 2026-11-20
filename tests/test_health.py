import pytest
from backend.main import app
from database.connection import init_db

def test_health():
    init_db()
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
