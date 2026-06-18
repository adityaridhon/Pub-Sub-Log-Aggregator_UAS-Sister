import json
import redis

from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.database import SessionLocal
from app.models import ProcessedEvent, Stats

r = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)


def start_consumer():

    pubsub = r.pubsub()

    pubsub.subscribe("logs")

    print("Consumer started...", flush=True)

    for message in pubsub.listen():

        if message["type"] != "message":
            continue

        data = json.loads(
            message["data"]
        )

        db = SessionLocal()

        try:

            stats = db.query(Stats).first()

            if not stats:
                stats = Stats()
                db.add(stats)
                db.commit()
                db.refresh(stats)

            stats.received += 1

            event = ProcessedEvent(
                topic=data["topic"],
                event_id=data["event_id"],
                timestamp=data["timestamp"],
                source=data["source"],
                payload=data["payload"]
            )

            db.add(event)

            db.commit()

            stats.unique_processed += 1

            db.commit()

            print(
                f"PROCESSED: {data['event_id']}",
                flush=True
            )

        except IntegrityError:

            db.rollback()

            stats = db.query(Stats).first()

            stats.duplicate_dropped += 1

            db.commit()

            print(
                f"DUPLICATE: {data['event_id']}",
                flush=True
            )

        except Exception as e:

            db.rollback()

            print(
                f"ERROR: {e}",
                flush=True
            )

        finally:

            db.close()