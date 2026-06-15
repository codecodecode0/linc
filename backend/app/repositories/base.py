"""Repository interfaces (the data-access boundary).

Services depend only on these abstract classes — never on a concrete store.
Today the implementations are in-memory (`memory.py`); to move to Postgres we
add SQLAlchemy-backed classes implementing the same interfaces and swap the
wiring in `deps.py`. No service or router code changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from ..models import (
    Activity,
    Brand,
    Campaign,
    Creator,
    Deal,
    Platform,
    PlatformStats,
    SocialConnection,
)


class CreatorRepository(ABC):
    @abstractmethod
    def list(self) -> List[Creator]: ...

    @abstractmethod
    def get(self, creator_id: str) -> Optional[Creator]: ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Creator]: ...

    @abstractmethod
    def get_by_phone(self, phone: str) -> Optional[Creator]: ...

    @abstractmethod
    def create(self, creator: Creator) -> Creator: ...

    @abstractmethod
    def save(self, creator: Creator) -> Creator: ...


class BrandRepository(ABC):
    @abstractmethod
    def get(self, brand_id: str) -> Optional[Brand]: ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Brand]: ...

    @abstractmethod
    def get_by_phone(self, phone: str) -> Optional[Brand]: ...

    @abstractmethod
    def create(self, brand: Brand) -> Brand: ...

    @abstractmethod
    def save(self, brand: Brand) -> Brand: ...


class OtpRepository(ABC):
    """Transient store for OTP challenges, keyed by 'channel:value'."""

    @abstractmethod
    def set(self, key: str, code: str, ttl_seconds: int) -> None: ...

    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """Return the code if present and unexpired, else None."""
        ...

    @abstractmethod
    def delete(self, key: str) -> None: ...


class ConnectionRepository(ABC):
    """Social connections, keyed by (creator, platform).

    A creator can hold one connection per platform, so reads are scoped by
    platform and `list_for_creator` returns every linked account.
    """

    @abstractmethod
    def list_for_creator(self, creator_id: str) -> List[SocialConnection]: ...

    @abstractmethod
    def get(self, creator_id: str, platform: Platform) -> Optional[SocialConnection]: ...

    @abstractmethod
    def upsert(self, connection: SocialConnection) -> SocialConnection: ...

    @abstractmethod
    def delete(self, creator_id: str, platform: Platform) -> bool: ...


class OAuthStateRepository(ABC):
    """Short-lived store mapping an OAuth `state` value to a creator id."""

    @abstractmethod
    def save(self, state: str, creator_id: str) -> None: ...

    @abstractmethod
    def pop(self, state: str) -> Optional[str]:
        """Return and remove the creator id for `state`, or None if unknown."""
        ...


class CatalogRepository(ABC):
    """Read-only demo catalog (stats, deals, campaigns, activity)."""

    @abstractmethod
    def stats(self) -> PlatformStats: ...

    @abstractmethod
    def deals(self) -> List[Deal]: ...

    @abstractmethod
    def campaigns(self) -> List[Campaign]: ...

    @abstractmethod
    def activity(self) -> List[Activity]: ...
