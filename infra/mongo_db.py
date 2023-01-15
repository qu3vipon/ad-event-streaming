from typing import List

import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://root:ad-event-stream@localhost:27017")
db = client.ad_event_stream.ad


async def init_ad_credit():
    ad_credit = [{"id": str(i), "credit": i * 100} for i in range(1, 5)]
    await db.insert_many(ad_credit)


async def get_ad_list() -> List[dict]:
    return [
        document async for document in db.find({"credit": {"$gt": 0}})
    ]


def init_db():
    loop = client.get_io_loop()
    loop.run_until_complete(init_ad_credit())
