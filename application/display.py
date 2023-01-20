import random

from infra.mongo_db import get_ad_list

OVER_CHARGE_OFFSET: int = 0


async def get_ad_to_display():
    ad_targets = await get_ad_list(over_charge_offset=OVER_CHARGE_OFFSET)
    if ad_targets:
        return random.choice(ad_targets)
    return None
