import asyncio
import pickle
from datetime import datetime, timedelta
from typing import ClassVar, List

from redis import Redis

from domain.entity import DATETIME_FORMAT

redis = Redis()


class RollingBloomFilter:
    WINDOW_HOURS: ClassVar[int] = 24
    KEY_PATTERN: ClassVar[str] = "%Y%m%d%H"

    @staticmethod
    def _as_dt(s: str) -> datetime:
        return datetime.strptime(s, DATETIME_FORMAT)

    def _get_key(self, at: datetime) -> str:
        return at.strftime(self.KEY_PATTERN)

    def _get_keys_to_search(self, at: datetime) -> List[str]:
        return [
            self._get_key(at=at - timedelta(hours=h)) for h in range(self.WINDOW_HOURS + 1)[::-1]
        ]

    async def exists(self, event) -> bool:
        loop = asyncio.get_event_loop()
        pickled_event = pickle.dumps(event)

        to_search: List[str] = self._get_keys_to_search(at=self._as_dt(event.event_time))
        for key in to_search:
            if await loop.run_in_executor(None, redis.bf().exists, key, pickled_event):
                return True
        return False

    def add(self, event):
        key: str = self._get_key(at=self._as_dt(event.event_time))

        pickled_event = pickle.dumps(event)

        # stale bloom filters will be remain..
        redis.bf().add(key=key, item=pickled_event)
