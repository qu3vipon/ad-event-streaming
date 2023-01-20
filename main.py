import random
from typing import Optional

import faust
from redis import Redis

from domain.entity import AdEvent
from application.display import get_ad_to_display
from application.charge import get_charge_values
from infra.mongo_db import charge, visualize_after_charge, client, drop_collection, seeding
from infra.redis import RollingBloomFilter


def init_storage():
    loop = client.get_io_loop()
    loop.run_until_complete(drop_collection())
    loop.run_until_complete(seeding())

    redis = Redis()
    redis.flushdb()


init_storage()

app = faust.App("ad-stream")
ad_event_topic = app.topic("ad-event", value_type=AdEvent, key_type=str, key_serializer="raw")


# Event Produce
@app.timer(interval=0.05)
async def produce_ad_event():
    ad_to_display: Optional[dict] = await get_ad_to_display()
    if ad_to_display:
        ad_event: AdEvent = AdEvent.create(ad=ad_to_display)
        await ad_event_topic.send(key=ad_event.ad_id, value=ad_event)


# Event Consume
@app.agent(ad_event_topic)
async def consume_ad_events(streams: AdEvent):
    bloom_filter = RollingBloomFilter()
    async for key, event in streams.items():
        if await bloom_filter.exists(event=event):
            # todo: possibly duplicate, check db..
            print("duplicate")
        else:
            # new event
            credit, imp, click = get_charge_values(event.event_type)
            await charge(ad_id=event.ad_id, credit=credit, impression=imp, click=click)
            bloom_filter.add(event=event)

        # visualize simulation..
        await visualize_after_charge(event)
