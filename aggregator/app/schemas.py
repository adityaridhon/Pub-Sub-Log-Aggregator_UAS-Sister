from pydantic import BaseModel
from datetime import datetime
from typing import Any


class Event(BaseModel):

    topic: str
    event_id: str
    timestamp: datetime
    source: str
    payload: dict[str, Any]

class BatchEvent(BaseModel):
    events: list[Event]