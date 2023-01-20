from __future__ import annotations

import random
from datetime import datetime
from enum import Enum
from uuid import uuid4

import faust

users = [uuid4() for _ in range(100)]


class AdEventType(str, Enum):
    IMPRESSION = "impression"
    CLICK = "click"


AD_DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S.%f"


class Ad(faust.Record):
    id: str
    credit: int
    impression: int
    click: int


class AdEvent(faust.Record):
    user_id: str
    ad_id: str
    event_type: AdEventType
    event_time: datetime

    @classmethod
    def create(cls, ad) -> AdEvent:
        return AdEvent(
            user_id=random.choice(users),
            ad_id=ad["id"],
            event_type=random.choice([AdEventType.IMPRESSION, AdEventType.CLICK]),
            event_time=datetime.utcnow(),
        )
