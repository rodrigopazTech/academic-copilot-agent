import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_api_get_tools():
    res = client.get("/api/agent/tools")
    assert res.status_code == 200
    data = res.json()
    assert "registered_tools" in data
    assert len(data["registered_tools"]) >= 5

def test_api_run_agent():
    res = client.post("/api/agent/run", json={
        "course_keyword": "Ciencia de Datos",
        "recording_id": "rec-2026-09-04-clase-08"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "audit_report" in data
    assert "execution_trace" in data

def test_api_chat():
    res = client.post("/api/agent/chat", json={
        "message": "Hola, ¿cómo estás?"
    })
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
