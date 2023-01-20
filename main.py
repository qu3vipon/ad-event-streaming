import random
from datetime import datetime

import faust

from domain.entity import AdEvent, AdEventType, OVER_CHARGE_OFFSET
from infra import mongo_db
from infra.redis import RollingBloomFilter

mongo_db.init_db()

app = faust.App("ad-stream")
ad_event_topic = app.topic("ad-event", value_type=AdEvent, key_type=str, key_serializer="raw")


# Event Produce
@app.timer(interval=0.05)
async def produce_ad_event():
    ad_targets = await mongo_db.get_ad_list(over_charge_offset=OVER_CHARGE_OFFSET)
    if ad_targets:
        ad_to_display = random.choice(ad_targets)
        ad_event: AdEvent = AdEvent(
            user_id=random.choice(mongo_db.users),
            ad_id=ad_to_display["id"],
            event_type=random.choice([AdEventType.IMPRESSION, AdEventType.CLICK]),
            event_time=datetime.utcnow(),
        )

        await ad_event_topic.send(key=ad_event.ad_id, value=ad_event)


# Event Consume
@app.agent(ad_event_topic)
async def consume_ad_events(streams: AdEvent):
    bloom_filter = RollingBloomFilter()
    async for key, event in streams.items():
        if await bloom_filter.exists(event=event):
            # possibly duplicate, check db..
            print("duplicate")
        else:
            # new event
            charge: int = 1 if event.event_type == AdEventType.IMPRESSION else 2
            await mongo_db.db.update_one(
                {"id": event.ad_id},
                {
                    "$inc": {
                        "credit": -charge,
                        "impression": 1 if event.event_type == AdEventType.IMPRESSION else 0,
                        "click": 1 if event.event_type == AdEventType.CLICK else 0,
                    }
                }
            )
            bloom_filter.add(event=event)

        # visualize simulation..
        after_charge = {
            document["id"]: document["credit"] async for document in mongo_db.db.find()
        }
        after_charge = sorted(after_charge.items(), key=lambda kv: (kv[1], kv[0]))
        print(f"{event=}")
        print(f"{after_charge=}")
