from typing import List
from uuid import uuid4

import motor.motor_asyncio
from redis import Redis

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://root:ad-event-stream@localhost:27017")
db = client.ad_event_stream.ad

users = [uuid4() for _ in range(100)]


async def init_ad():
    ad_credit = [{"id": str(i), "credit": 100, "impression": 0, "click": 0} for i in range(1, 11)]
    await db.insert_many(ad_credit)


async def drop_stale_collection():
    await db.drop()


async def get_ad_list(over_charge_offset: int) -> List[dict]:
    return [
        document async for document in db.find({"credit": {"$gt": over_charge_offset}})
    ]


def init_db():
    loop = client.get_io_loop()
    loop.run_until_complete(drop_stale_collection())
    loop.run_until_complete(init_ad())

    redis = Redis()
    redis.flushdb()
