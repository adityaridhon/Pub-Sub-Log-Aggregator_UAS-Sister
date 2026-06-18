import time

from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models import ProcessedEvent

client = TestClient(app)


def test_unique_constraint():

    payload = {
        "topic": "system",
        "event_id": "UNIQUE-TEST",
        "timestamp": "2026-01-01T00:00:00",
        "source": "pytest",
        "payload": {
            "msg": "unique"
        }
    }

    client.post("/publish", json=payload)

    client.post("/publish", json=payload)

    client.post("/publish", json=payload)

    time.sleep(2)

    db = SessionLocal()

    count = (
        db.query(ProcessedEvent)
        .filter(
            ProcessedEvent.event_id == "UNIQUE-TEST"
        )
        .count()
    )

    db.close()

    assert count == 1