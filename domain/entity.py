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


class AdEvent(faust.Record):
    user_id: str
    ad_id: str
    event_type: AdEventType
    event_time: datetime
