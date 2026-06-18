import time

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_uptime_increases():

    first = client.get(
        "/stats"
    ).json()["uptime"]

    time.sleep(3)

    second = client.get(
        "/stats"
    ).json()["uptime"]

    assert second > first