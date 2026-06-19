import time
import uuid
import requests

BASE_URL = "http://localhost:8080"

TOTAL_EVENTS = 20000
DUPLICATE_RATE = 0.30
BATCH_SIZE = 500


def build_events():

    unique_count = int(
        TOTAL_EVENTS * (1 - DUPLICATE_RATE)
    )

    duplicate_count = (
        TOTAL_EVENTS - unique_count
    )

    events = []

    unique_ids = []

    for _ in range(unique_count):

        eid = str(uuid.uuid4())

        unique_ids.append(eid)

        events.append(
            {
                "topic": "perf",
                "event_id": eid,
                "timestamp": "2026-06-19T00:00:00",
                "source": "performance-test",
                "payload": {
                    "cpu": 50
                }
            }
        )

    for i in range(duplicate_count):

        events.append(
            {
                "topic": "perf",
                "event_id": unique_ids[
                    i % len(unique_ids)
                ],
                "timestamp": "2026-06-19T00:00:00",
                "source": "performance-test",
                "payload": {
                    "cpu": 50
                }
            }
        )

    return events


def test_performance():

    session = requests.Session()

    events = build_events()

    start = time.time()

    accepted = 0

    for i in range(
        0,
        len(events),
        BATCH_SIZE
    ):

        batch = {
            "events": events[
                i:i+BATCH_SIZE
            ]
        }

        r = session.post(
            f"{BASE_URL}/publish-batch",
            json=batch,
            timeout=60
        )

        assert r.status_code == 200

        accepted += r.json()["accepted"]

    publish_time = (
        time.time() - start
    )

    print()

    print("=" * 50)

    print(
        f"EVENTS      : {TOTAL_EVENTS}"
    )

    print(
        f"DUPLICATES  : {int(TOTAL_EVENTS*DUPLICATE_RATE)}"
    )

    print(
        f"PUBLISH TIME: {publish_time:.2f}s"
    )

    print(
        f"THROUGHPUT  : {TOTAL_EVENTS/publish_time:.2f} event/sec"
    )

    print("=" * 50)

    deadline = time.time() + 300

    while time.time() < deadline:

        stats = requests.get(
            f"{BASE_URL}/stats"
        ).json()

        if stats["received"] >= TOTAL_EVENTS:

            break

        print(
            f"waiting... {stats['received']}/{TOTAL_EVENTS}"
        )

        time.sleep(2)

    duplicate_rate = (
        stats["duplicate_dropped"]
        / stats["received"]
        if stats["received"] > 0
        else 0
    )

    print()

    print("FINAL STATS")

    print(
        f"received            : {stats['received']}"
    )

    print(
        f"unique_processed    : {stats['unique_processed']}"
    )

    print(
        f"duplicate_dropped   : {stats['duplicate_dropped']}"
    )

    print(
        f"duplicate_rate      : {duplicate_rate:.2%}"
    )

    assert (
        stats["received"]
        >= TOTAL_EVENTS
    )