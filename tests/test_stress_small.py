import time

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_small_batch_performance():

    start = time.time()

    for i in range(100):

        payload = {
            "topic": "stress",
            "event_id": f"stress-{i}",
            "timestamp": "2026-01-01T00:00:00",
            "source": "pytest",
            "payload": {
                "batch": i
            }
        }

        client.post(
            "/publish",
            json=payload
        )

    duration = time.time() - start

    assert duration < 10