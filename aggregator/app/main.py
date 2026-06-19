from threading import Thread
import json

from fastapi import FastAPI
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime

from app.database import engine
from app.database import get_db
from app.models import Base
from app.models import Stats
from app.models import ProcessedEvent
from app.schemas import Event
from app.redis_client import redis_client
from app.consumer import start_consumer
from app.schemas import BatchEvent
from app.database import SessionLocal

Base.metadata.create_all(bind=engine)

START_TIME = datetime.utcnow()
app = FastAPI(
    title="PubSub Log Aggregator",
    version="1.0.0"
)


@app.on_event("startup")
def startup_event():

    db = SessionLocal()

    try:

        stats = db.query(Stats).first()

        if not stats:

            db.add(
                Stats(
                    received=0,
                    unique_processed=0,
                    duplicate_dropped=0
                )
            )

            db.commit()

    finally:

        db.close()

    for _ in range(4):

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

@app.post("/publish-batch")
def publish_batch(batch: BatchEvent):

    pipe = redis_client.pipeline()

    for event in batch.events:

        pipe.publish(
            "logs",
            json.dumps(
                event.model_dump(),
                default=str
            )
        )

    results = pipe.execute()

    return {
        "accepted": len(results)
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

    topic_counts = dict(

        db.query(
            ProcessedEvent.topic,
            func.count()
        )
        .group_by(
            ProcessedEvent.topic
        )
        .all()

    )

    uptime_seconds = int(
        (datetime.utcnow() - START_TIME)
        .total_seconds()
    )

    return {
        "received": stats_row.received,
        "unique_processed": stats_row.unique_processed,
        "duplicate_dropped": stats_row.duplicate_dropped,
        "topics": topic_counts,
        "uptime": uptime_seconds
    }