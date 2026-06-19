import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE_URL = "http://localhost:8080"


def make_event(event_id):

    return {
        "topic": "stress-test",
        "event_id": event_id,
        "timestamp": "2026-06-19T00:00:00",
        "source": "performance_test",
        "payload": {
            "cpu": 50,
            "memory": 40
        }
    }


def send_event(event):

    response = requests.post(
        f"{BASE_URL}/publish",
        json=event,
        timeout=30
    )

    return response.status_code


def test_20000_events():

    TOTAL_EVENTS = 20000
    DUPLICATE_RATE = 0.30

    unique_count = int(
        TOTAL_EVENTS * (1 - DUPLICATE_RATE)
    )

    duplicate_count = (
        TOTAL_EVENTS - unique_count
    )

    print("\nGenerating events...")

    unique_ids = [
        str(uuid.uuid4())
        for _ in range(unique_count)
    ]

    events = []

    for eid in unique_ids:

        events.append(
            make_event(eid)
        )

    for i in range(duplicate_count):

        events.append(
            make_event(
                unique_ids[
                    i % len(unique_ids)
                ]
            )
        )

    print(
        f"Total Events     : {TOTAL_EVENTS}"
    )

    print(
        f"Unique Events    : {unique_count}"
    )

    print(
        f"Duplicate Events : {duplicate_count}"
    )

    start_time = time.time()

    with ThreadPoolExecutor(
        max_workers=100
    ) as executor:

        futures = [
            executor.submit(
                send_event,
                event
            )
            for event in events
        ]

        success = 0

        for future in as_completed(
            futures
        ):

            if future.result() == 200:
                success += 1

    publish_time = (
        time.time() - start_time
    )

    print(
        f"\nPublish Finished: "
        f"{publish_time:.2f}s"
    )

    print(
        "Waiting consumer..."
    )

    time.sleep(15)

    stats = requests.get(
        f"{BASE_URL}/stats"
    ).json()

    received = stats["received"]
    unique_processed = stats["unique_processed"]
    duplicate_dropped = stats["duplicate_dropped"]

    throughput = (
        received / publish_time
    )

    duplicate_rate = (
        duplicate_dropped / received
    ) * 100

    avg_latency_ms = (
        publish_time / TOTAL_EVENTS
    ) * 1000

    print("\n========== RESULT ==========")

    print(
        f"Received            : {received}"
    )

    print(
        f"Unique Processed    : "
        f"{unique_processed}"
    )

    print(
        f"Duplicate Dropped   : "
        f"{duplicate_dropped}"
    )

    print(
        f"Throughput          : "
        f"{throughput:.2f} events/sec"
    )

    print(
        f"Average Latency     : "
        f"{avg_latency_ms:.2f} ms/event"
    )

    print(
        f"Duplicate Rate      : "
        f"{duplicate_rate:.2f}%"
    )

    assert received >= TOTAL_EVENTS

    assert duplicate_rate >= 30