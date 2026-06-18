import requests
import uuid
import random
from datetime import datetime
import time

print("Waiting aggregator...")
time.sleep(10)

URL = "http://aggregator:8080/publish"

while True:

    duplicate = random.random() < 0.3

    if duplicate:
        event_id = "DUPLICATE-EVENT"
    else:
        event_id = str(uuid.uuid4())

    payload = {
        "topic": "system",
        "event_id": event_id,
        "timestamp": datetime.utcnow().isoformat(),
        "source": "publisher",
        "payload": {
            "cpu": random.randint(1, 100),
            "memory": random.randint(1, 100)
        }
    }

    response = requests.post(
        URL,
        json=payload
    )

    print(
        response.status_code,
        event_id
    )

    time.sleep(1)