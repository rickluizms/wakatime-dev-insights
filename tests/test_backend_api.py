import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from core.config import READONLY_API_KEY

client = TestClient(app)

def test_health_check(mocker):
    # Mock do get_tables da classe filha Database para HealthCheck
    mocker.patch("core.db.Database.get_tables", return_value=["table1", "table2"])
    
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["tables_count"] == 2

def test_security_api_key_missing():
    # Endpoints seguros sem chave devem falhar com 401
    response = client.get("/summaries")
    assert response.status_code == 401
    assert "API Key não fornecida" in response.json()["detail"]

def test_security_api_key_invalid():
    # Endpoints seguros com chave errada falham (Testando mitigação de timing attack)
    response = client.get("/summaries", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401
    assert "API Key inválida" in response.json()["detail"]

def test_get_summaries_success(mocker):
    # Mock the database fetch_all para endpoints seguros
    db_mock = mocker.patch("core.db.Database.fetch_all")
    db_mock.return_value = [
        {
            "id": 1,
            "created_at": "2026-02-27T00:00:00Z",
            "date": "2026-02-27",
            "total_seconds": 3600,
            "digital": "1:00",
            "hours": 1,
            "minutes": 0,
            "text": "1 hr",
            "ai_additions": 0,
            "ai_deletions": 0,
            "human_additions": 100,
            "human_deletions": 50
        }
    ]
    
    response = client.get("/summaries", headers={"X-API-Key": READONLY_API_KEY})
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["date"] == "2026-02-27"
    assert data[0]["total_seconds"] == 3600
    
def test_get_language_stats(mocker):
    # Mock do fetch_all do language stats
    db_mock = mocker.patch("core.db.Database.fetch_all")
    db_mock.return_value = [
        {"name": "Python", "total_seconds": 7200},
        {"name": "JavaScript", "total_seconds": 3600}
    ]
    
    response = client.get("/languages/stats", headers={"X-API-Key": READONLY_API_KEY})
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Python"
    assert data[0]["total_hours"] == 2
    # Total hours é 10800 sum(). Python representa 66.67%
    assert data[0]["percentage"] == 66.67
