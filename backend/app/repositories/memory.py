"""In-memory implementations of the repository interfaces.

State lives in process and resets on restart — fine for the demo. Each class
maps 1:1 onto a future SQLAlchemy/Postgres implementation.
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple

from ..data import seed
from ..models import (
    Activity,
    Brand,
    CampaignSummary,
    Creator,
    DealSummary,
    Platform,
    PlatformStats,
    SocialConnection,
)
from .base import (
    BrandRepository,
    CatalogRepository,
    ConnectionRepository,
    CreatorRepository,
    OAuthStateRepository,
    OtpRepository,
)


class InMemoryCreatorRepository(CreatorRepository):
    def __init__(self) -> None:
        self._creators: Dict[str, Creator] = {c.id: c for c in seed.seed_creators()}

    def list(self) -> List[Creator]:
        return list(self._creators.values())

    def get(self, creator_id: str) -> Optional[Creator]:
        return self._creators.get(creator_id)

    def get_by_email(self, email: str) -> Optional[Creator]:
        return next(
            (c for c in self._creators.values() if c.email.lower() == email.lower()),
            None,
        )

    def get_by_phone(self, phone: str) -> Optional[Creator]:
        return next(
            (c for c in self._creators.values() if c.phone == phone), None
        )

    def create(self, creator: Creator) -> Creator:
        self._creators[creator.id] = creator
        return creator

    def save(self, creator: Creator) -> Creator:
        self._creators[creator.id] = creator
        return creator


class InMemoryBrandRepository(BrandRepository):
    def __init__(self) -> None:
        self._brands: Dict[str, Brand] = {}

    def get(self, brand_id: str) -> Optional[Brand]:
        return self._brands.get(brand_id)

    def get_by_email(self, email: str) -> Optional[Brand]:
        return next(
            (b for b in self._brands.values() if b.email.lower() == email.lower()),
            None,
        )

    def get_by_phone(self, phone: str) -> Optional[Brand]:
        return next((b for b in self._brands.values() if b.phone == phone), None)

    def create(self, brand: Brand) -> Brand:
        self._brands[brand.id] = brand
        return brand

    def save(self, brand: Brand) -> Brand:
        self._brands[brand.id] = brand
        return brand


class InMemoryOtpRepository(OtpRepository):
    def __init__(self) -> None:
        # key -> (code, expires_at)
        self._store: Dict[str, Tuple[str, float]] = {}

    def set(self, key: str, code: str, ttl_seconds: int) -> None:
        self._store[key] = (code, time.time() + ttl_seconds)

    def get(self, key: str) -> Optional[str]:
        entry = self._store.get(key)
        if not entry:
            return None
        code, expires_at = entry
        if time.time() > expires_at:
            self._store.pop(key, None)
            return None
        return code

    def delete(self, key: str) -> None:
        self._store.pop(key, None)


class InMemoryConnectionRepository(ConnectionRepository):
    def __init__(self) -> None:
        # keyed by (creator_id, platform)
        self._store: Dict[Tuple[str, Platform], SocialConnection] = {}

    def list_for_creator(self, creator_id: str) -> List[SocialConnection]:
        return [c for (cid, _), c in self._store.items() if cid == creator_id]

    def get(self, creator_id: str, platform: Platform) -> Optional[SocialConnection]:
        return self._store.get((creator_id, platform))

    def upsert(self, connection: SocialConnection) -> SocialConnection:
        self._store[(connection.creator_id, connection.platform)] = connection
        return connection

    def delete(self, creator_id: str, platform: Platform) -> bool:
        return self._store.pop((creator_id, platform), None) is not None


class InMemoryOAuthStateRepository(OAuthStateRepository):
    # OAuth states are valid for 10 minutes.
    TTL_SECONDS = 600

    def __init__(self) -> None:
        # state -> (creator_id, created_at)
        self._states: Dict[str, Tuple[str, float]] = {}

    def save(self, state: str, creator_id: str) -> None:
        self._prune()
        self._states[state] = (creator_id, time.time())

    def pop(self, state: str) -> Optional[str]:
        self._prune()
        entry = self._states.pop(state, None)
        return entry[0] if entry else None

    def _prune(self) -> None:
        now = time.time()
        expired = [
            s for s, (_, ts) in self._states.items()
            if now - ts > self.TTL_SECONDS
        ]
        for s in expired:
            self._states.pop(s, None)


class InMemoryCatalogRepository(CatalogRepository):
    def __init__(self) -> None:
        self._stats = seed.seed_stats()
        self._deals = seed.seed_deals()
        self._campaigns = seed.seed_campaigns()
        self._activity = seed.seed_activity()

    def stats(self) -> PlatformStats:
        return self._stats

    def deals(self) -> List[DealSummary]:
        return self._deals

    def campaigns(self) -> List[CampaignSummary]:
        return self._campaigns

    def activity(self) -> List[Activity]:
        return self._activity
