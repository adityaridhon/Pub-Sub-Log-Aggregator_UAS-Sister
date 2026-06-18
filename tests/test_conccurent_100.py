import time
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def send_duplicate():

    payload = {
        "topic": "system",
        "event_id": "CONCURRENCY-100",
        "timestamp": "2026-01-01T00:00:00",
        "source": "pytest",
        "payload": {
            "message": "race-condition"
        }
    }

    return client.post(
        "/publish",
        json=payload
    )


def test_concurrency_100():

    start = time.time()

    with ThreadPoolExecutor(max_workers=100) as executor:

        futures = [
            executor.submit(send_duplicate)
            for _ in range(100)
        ]

        for future in futures:
            response = future.result()
            assert response.status_code == 200

    duration = time.time() - start

    time.sleep(5)

    stats = client.get("/stats").json()

    assert stats["received"] >= 100

    assert stats["duplicate_dropped"] >= 99

    assert duration < 30