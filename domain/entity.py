from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import faust


@dataclass
class User:
    uuid: str


class AdEventType(str, Enum):
    IMPRESSION = "impression"
    CLICK = "click"


class Ad(faust.Record):
    id: str
    credit: int
    impression: int
    click: int


DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S.%f"
OVER_CHARGE_OFFSET: int = 0


class AdEvent(faust.Record):
    user_id: str
    ad_id: str
    event_type: AdEventType
    event_time: datetime
