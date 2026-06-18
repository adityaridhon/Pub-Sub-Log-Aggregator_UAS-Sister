from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_stats_contains_required_fields():

    response = client.get("/stats")

    assert response.status_code == 200

    data = response.json()

    assert "received" in data
    assert "unique_processed" in data
    assert "duplicate_dropped" in data
    assert "topics" in data
    assert "uptime" in data