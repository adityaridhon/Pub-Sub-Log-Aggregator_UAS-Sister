import json
import redis

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

from app.config import settings
from app.database import SessionLocal
from app.models import ProcessedEvent
from app.schemas import BatchEvent
import os


r = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)


def start_consumer():

    pubsub = r.pubsub()

    pubsub.subscribe("logs")

    print(f"Consumer started id: {os.getpid()}", flush=True)

    for message in pubsub.listen():

        if message["type"] != "message":
            continue

        data = json.loads(message["data"])

        db = SessionLocal()

        try:

            stmt = (
                insert(ProcessedEvent)
                .values(
                    topic=data["topic"],
                    event_id=data["event_id"],
                    timestamp=data["timestamp"],
                    source=data["source"],
                    payload=data["payload"]
                )
                .on_conflict_do_nothing(
                    index_elements=[
                        "topic",
                        "event_id"
                    ]
                )
            )

            result = db.execute(stmt)

            if result.rowcount == 1:

                db.execute(
                    text("""
                        UPDATE stats
                        SET
                            received = received + 1,
                            unique_processed = unique_processed + 1
                    """)
                )

            else:

                db.execute(
                    text("""
                        UPDATE stats
                        SET
                            received = received + 1,
                            duplicate_dropped = duplicate_dropped + 1
                    """)
                )

            db.commit()

        except Exception as e:

            db.rollback()

            print(
                f"ERROR: {e}",
                flush=True
            )

        finally:

            db.close()