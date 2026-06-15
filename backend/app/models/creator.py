from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import Field

from .base import CamelModel
from .connection import Platform


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Creator(CamelModel):
    id: str
    name: str
    email: str
    phone: str
    handle: str
    niche: str = ""
    city: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    # Cached display strings used by the recommendation cards.
    followers: str = ""
    engagement: str = ""
    match_score: int = 0
    avatar: str = ""
    certified: bool = False
    rate: int = 0  # starting rate per video, in rupees
    status: str = "onboarding"  # onboarding | active | paused
    google_sub: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)
    # Which platforms this creator has linked — derived at read time.
    connected_platforms: List[Platform] = Field(default_factory=list)
