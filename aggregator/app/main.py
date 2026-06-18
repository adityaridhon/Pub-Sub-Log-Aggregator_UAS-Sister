from threading import Thread
import json

from fastapi import FastAPI
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from app.database import engine
from app.database import get_db
from app.models import Base
from app.models import Stats
from app.models import ProcessedEvent
from app.schemas import Event
from app.redis_client import redis_client
from app.consumer import start_consumer

Base.metadata.create_all(bind=engine)

START_TIME = datetime.utcnow()
app = FastAPI(
    title="PubSub Log Aggregator",
    version="1.0.0"
)


@app.on_event("startup")
def startup_event():

    Thread(
        target=start_consumer,
        daemon=True
    ).start()


@app.get("/")
def root():

    return {
        "service": "aggregator",
        "status": "running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }

@app.post("/publish")
def publish(event: Event):

    subscribers = redis_client.publish(
        "logs",
        json.dumps(
            event.model_dump(),
            default=str
        )
    )

    return {
        "status": "queued",
        "event_id": event.event_id,
        "subscribers": subscribers
    }


@app.get("/events")
def get_events(
    topic: str | None = None,
    db: Session = Depends(get_db)
):

    query = db.query(ProcessedEvent)

    if topic:
        query = query.filter(
            ProcessedEvent.topic == topic
        )

    events = query.all()

    return [
        {
            "id": event.id,
            "topic": event.topic,
            "event_id": event.event_id,
            "timestamp": event.timestamp,
            "source": event.source,
            "payload": event.payload
        }
        for event in events
    ]


@app.get("/stats")
def stats(
    db: Session = Depends(get_db)
):

    stats_row = db.query(Stats).first()

    if not stats_row:
        return {
            "received": 0,
            "unique_processed": 0,
            "duplicate_dropped": 0,
            "topics": {},
            "uptime": 0
        }

    topic_counts = {}

    events = db.query(ProcessedEvent).all()

    for event in events:

        topic_counts[event.topic] = (
            topic_counts.get(event.topic, 0) + 1
        )

    uptime_seconds = int(
        (datetime.utcnow() - START_TIME).total_seconds()
    )

    return {
        "received": stats_row.received,
        "unique_processed": stats_row.unique_processed,
        "duplicate_dropped": stats_row.duplicate_dropped,
        "topics": topic_counts,
        "uptime": uptime_seconds
    }