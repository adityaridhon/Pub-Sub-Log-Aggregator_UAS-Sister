import time

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_duplicate_counter():

    payload = {
        "topic": "system",
        "event_id": "COUNTER-TEST",
        "timestamp": "2026-01-01T00:00:00",
        "source": "pytest",
        "payload": {
            "message": "duplicate test"
        }
    }

    for _ in range(5):
        client.post(
            "/publish",
            json=payload
        )

    time.sleep(1)

    stats = client.get("/stats").json()

    assert stats["duplicate_dropped"] >= 4

    assert (
        stats["received"]
        ==
        stats["unique_processed"]
        +
        stats["duplicate_dropped"]
    )