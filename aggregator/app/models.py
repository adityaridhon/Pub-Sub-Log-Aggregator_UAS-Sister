from sqlalchemy.orm import DeclarativeBase

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import JSON
from sqlalchemy import UniqueConstraint
from sqlalchemy import BigInteger


class Base(DeclarativeBase):
    pass


class ProcessedEvent(Base):
    __tablename__ = "processed_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    topic = Column(
        String(100),
        nullable=False
    )

    event_id = Column(
        String(255),
        nullable=False
    )

    timestamp = Column(
        DateTime,
        nullable=False
    )

    source = Column(
        String(100),
        nullable=False
    )

    payload = Column(
        JSON,
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "topic",
            "event_id",
            name="uq_topic_event"
        ),
    )


class Stats(Base):

    __tablename__ = "stats"

    id = Column(
        Integer,
        primary_key=True
    )

    received = Column(
        BigInteger,
        default=0
    )

    unique_processed = Column(
        BigInteger,
        default=0
    )

    duplicate_dropped = Column(
        BigInteger,
        default=0
    )