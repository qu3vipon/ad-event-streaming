from typing import Tuple

from domain.entity import AdEventType


def get_charge_values(event_type: str) -> Tuple[int, int, int]:
    # return: (credit, imp, click)
    return (1, 1, 0) if event_type == AdEventType.IMPRESSION else (2, 0, 1)
