import random
from datetime import datetime
from uuid import uuid4

import faust

from domain.entity import AdEvent, AdEventType
from infra.mongo_db import get_ad_list, db, init_db

init_db()

app = faust.App("ad-stream")
ad_event_topic = app.topic("ad-event", value_type=AdEvent, key_type=str, key_serializer="raw")


# Event Produce
users = [uuid4() for _ in range(100)]


@app.timer(interval=0.01)
async def produce_ad_event():
    ad_targets = await get_ad_list()

    if ad_targets:
        # ToDo: Add recommendation or bidding system
        ad_to_display = random.choice(ad_targets)

        ad_event: AdEvent = AdEvent(
            user_id=random.choice(users),
            ad_id=ad_to_display["id"],
            event_type=random.choice([AdEventType.IMPRESSION, AdEventType.CLICK]),
            event_time=datetime.utcnow(),
        )

        await ad_event_topic.send(key=ad_event.ad_id, value=ad_event)


# Event Consume

@app.agent(ad_event_topic)
async def consume_ad_events(streams: AdEvent):
    async for key, event in streams.items():
        # ToDo: validate duplicate event(w/ rolling bloom filter)

        # charge
        charge: int = 1 if event.event_type == AdEventType.IMPRESSION else 2
        await db.update_one({"id": event.ad_id}, {"$inc": {"credit": -charge}})

        # to visualize simulation..
        after_charge = [
            {
                "id": document["id"], "credit": document["credit"]
            } async for document in db.find()
        ]
        print(f"{event=}")
        print(f"{after_charge=}")
