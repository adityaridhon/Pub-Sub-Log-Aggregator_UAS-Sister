from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_invalid_event_schema():

    response = client.post(
        "/publish",
        json={
            "topic": "system"
        }
    )

    assert response.status_code == 422