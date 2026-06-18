import time

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_duplicate_event_processed_once():

    payload = {
        "topic": "system",
        "event_id": "TEST-DUP",
        "timestamp": "2026-01-01T00:00:00",
        "source": "pytest",
        "payload": {
            "message": "hello"
        }
    }

    client.post("/publish", json=payload)

    client.post("/publish", json=payload)

    time.sleep(1)

    stats = client.get("/stats").json()

    assert stats["duplicate_dropped"] >= 1