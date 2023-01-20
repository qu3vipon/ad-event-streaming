from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Tuple

import faust


@dataclass
class User:
    uuid: str


def get_charge_values(event_type: str) -> Tuple[int, int, int]:
    # return: (credit, imp, click)
    return (1, 1, 0) if event_type == AdEventType.IMPRESSION else (2, 0, 1)


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
