# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_start_conversation():
    response = client.post("/api/chat/start")
    assert response.status_code == 200
    assert "id" in response.json()
    assert "messages" in response.json()


# Más pruebas...
