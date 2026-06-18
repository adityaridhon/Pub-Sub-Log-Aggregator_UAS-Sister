import time

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_topic_filter():

    event_system = {
        "topic": "system",
        "event_id": "TOPIC-SYSTEM",
        "timestamp": "2026-01-01T00:00:00",
        "source": "pytest",
        "payload": {
            "msg": "system"
        }
    }

    event_app = {
        "topic": "application",
        "event_id": "TOPIC-APP",
        "timestamp": "2026-01-01T00:00:00",
        "source": "pytest",
        "payload": {
            "msg": "application"
        }
    }

    client.post("/publish", json=event_system)
    client.post("/publish", json=event_app)

    time.sleep(1)

    response = client.get(
        "/events?topic=system"
    )

    assert response.status_code == 200

    events = response.json()

    assert len(events) > 0

    for event in events:
        assert event["topic"] == "system"