from typing import List

import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://root:ad-event-stream@localhost:27017")
db = client.ad_event_stream.ad


async def seeding():
    ad_credit = [{"id": str(i), "credit": 100, "impression": 0, "click": 0} for i in range(1, 11)]
    await db.insert_many(ad_credit)


async def drop_collection():
    await db.drop()


async def get_ad_list(over_charge_offset: int) -> List[dict]:
    return [
        document async for document in db.find({"credit": {"$gt": over_charge_offset}})
    ]


async def charge(ad_id: int, credit: int, impression: int, click: int):
    await db.update_one(
        {"id": ad_id},
        {
            "$inc": {
                "credit": -credit,
                "impression": impression,
                "click": click,
            }
        }
    )


async def visualize_after_charge(event):
    after_charge = {
        document["id"]: document["credit"] async for document in db.find()
    }
    after_charge = sorted(after_charge.items(), key=lambda kv: (kv[1], kv[0]))
    print(f"{event=}")
    print(f"{after_charge=}")
