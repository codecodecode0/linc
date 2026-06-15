from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import Field

from .base import CamelModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Brand(CamelModel):
    id: str
    name: str
    email: str
    phone: str
    category: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    gstin: Optional[str] = None
    status: str = "active"  # active | suspended
    google_sub: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)
