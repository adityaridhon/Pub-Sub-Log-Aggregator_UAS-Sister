import time
import uuid

from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def make_event(
    topic="system",
    event_id=None,
):
    return {
        "topic": topic,
        "event_id": event_id or str(uuid.uuid4()),
        "timestamp": "2026-06-18T12:00:00",
        "source": "pytest",
        "payload": {
            "message": "test"
        }
    }


def get_stats():
    return client.get("/stats").json()


# =====================================================
# T01 Schema Validation
# =====================================================

def test_t01_invalid_schema():

    response = client.post(
        "/publish",
        json={"topic": "system"}
    )

    assert response.status_code == 422


# =====================================================
# T02 Valid Publish
# =====================================================

def test_t02_valid_publish():

    response = client.post(
        "/publish",
        json=make_event()
    )

    assert response.status_code == 200


# =====================================================
# T03 Duplicate Event
# =====================================================

def test_t03_duplicate_event_processed_once():

    event = make_event(
        event_id=f"T03-{uuid.uuid4()}"
    )

    before = get_stats()

    client.post("/publish", json=event)
    client.post("/publish", json=event)

    time.sleep(2)

    after = get_stats()

    assert (
        after["duplicate_dropped"]
        >
        before["duplicate_dropped"]
    )


# =====================================================
# T04 Parallel Duplicate
# =====================================================

def test_t04_parallel_dedup():

    event = make_event(
        event_id=f"T04-{uuid.uuid4()}"
    )

    before = get_stats()

    def send():
        return client.post(
            "/publish",
            json=event
        )

    with ThreadPoolExecutor(max_workers=2) as executor:

        futures = [
            executor.submit(send)
            for _ in range(2)
        ]

        for future in futures:
            assert future.result().status_code == 200

    time.sleep(2)

    after = get_stats()

    assert (
        after["unique_processed"]
        -
        before["unique_processed"]
    ) == 1


# =====================================================
# T05 Concurrency 10
# =====================================================

def test_t05_concurrency_10():

    event = make_event(
        event_id=f"T05-{uuid.uuid4()}"
    )

    before = get_stats()

    def send():
        return client.post(
            "/publish",
            json=event
        )

    with ThreadPoolExecutor(max_workers=10) as executor:

        futures = [
            executor.submit(send)
            for _ in range(10)
        ]

        for future in futures:
            assert future.result().status_code == 200

    time.sleep(2)

    after = get_stats()

    assert (
        after["unique_processed"]
        -
        before["unique_processed"]
    ) == 1


# =====================================================
# T06 Concurrency 50
# =====================================================

def test_t06_concurrency_50():

    event = make_event(
        event_id=f"T06-{uuid.uuid4()}"
    )

    before = get_stats()

    def send():
        return client.post(
            "/publish",
            json=event
        )

    with ThreadPoolExecutor(max_workers=50) as executor:

        futures = [
            executor.submit(send)
            for _ in range(50)
        ]

        for future in futures:
            assert future.result().status_code == 200

    time.sleep(3)

    after = get_stats()

    assert (
        after["unique_processed"]
        -
        before["unique_processed"]
    ) == 1


# =====================================================
# T07 Concurrency 100
# =====================================================

def test_t07_concurrency_100():

    event = make_event(
        event_id=f"T07-{uuid.uuid4()}"
    )

    before = get_stats()

    def send():
        return client.post(
            "/publish",
            json=event
        )

    with ThreadPoolExecutor(max_workers=100) as executor:

        futures = [
            executor.submit(send)
            for _ in range(100)
        ]

        for future in futures:
            assert future.result().status_code == 200

    time.sleep(5)

    after = get_stats()

    assert (
        after["unique_processed"]
        -
        before["unique_processed"]
    ) == 1


# =====================================================
# T08 Stats Consistency
# =====================================================

def test_t08_stats_consistency():

    stats = get_stats()

    assert (
        stats["received"]
        ==
        stats["unique_processed"]
        +
        stats["duplicate_dropped"]
    )


# =====================================================
# T09 Stats Fields
# =====================================================

def test_t09_stats_fields():

    stats = get_stats()

    assert "received" in stats
    assert "unique_processed" in stats
    assert "duplicate_dropped" in stats
    assert "topics" in stats
    assert "uptime" in stats


# =====================================================
# T10 Uptime
# =====================================================

def test_t10_uptime():

    first = get_stats()["uptime"]

    time.sleep(2)

    second = get_stats()["uptime"]

    assert second > first


# =====================================================
# T11 Topic Filter
# =====================================================

def test_t11_topic_filter():

    topic = f"topic-{uuid.uuid4()}"

    event = make_event(
        topic=topic
    )

    client.post(
        "/publish",
        json=event
    )

    time.sleep(2)

    response = client.get(
        f"/events?topic={topic}"
    )

    events = response.json()

    assert len(events) > 0

    for event in events:

        assert (
            event["topic"]
            ==
            topic
        )


# =====================================================
# T12 Unique Constraint
# =====================================================

def test_t12_unique_constraint():

    event_id = f"T12-{uuid.uuid4()}"

    event = make_event(
        event_id=event_id
    )

    client.post("/publish", json=event)
    client.post("/publish", json=event)

    time.sleep(2)

    events = client.get(
        "/events"
    ).json()

    count = sum(
        1
        for e in events
        if e["event_id"] == event_id
    )

    assert count == 1


# =====================================================
# T13 Persistence
# =====================================================

def test_t13_persistence():

    event_id = f"T13-{uuid.uuid4()}"

    event = make_event(
        event_id=event_id
    )

    client.post(
        "/publish",
        json=event
    )

    time.sleep(2)

    before = get_stats()

    client.post(
        "/publish",
        json=event
    )

    time.sleep(2)

    after = get_stats()

    assert (
        after["duplicate_dropped"]
        >
        before["duplicate_dropped"]
    )

