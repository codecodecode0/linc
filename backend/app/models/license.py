from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import Field

from .base import CamelModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class GranteeType(str, Enum):
    platform = "platform"
    brand = "brand"


class MediaScope(str, Enum):
    static = "static"
    video = "video"
    both = "both"


class RateModel(str, Enum):
    per_generation = "per_generation"
    per_use = "per_use"
    flat_monthly = "flat_monthly"


class LicenseStatus(str, Enum):
    active = "active"
    paused = "paused"
    revoked = "revoked"
    expired = "expired"


class LikenessLicense(CamelModel):
    """Certified Digi Creator consent — a creator's likeness license."""

    id: str
    creator_id: str
    grantee_type: GranteeType = GranteeType.platform
    brand_id: Optional[str] = None  # set when grantee_type == brand
    media_scope: MediaScope = MediaScope.both
    allowed_use: Optional[str] = None
    territory: Optional[str] = None
    term_start: Optional[date] = None
    term_end: Optional[date] = None
    rate_model: RateModel = RateModel.per_generation
    rate_amount: int = 0  # rupees
    currency: str = "INR"
    status: LicenseStatus = LicenseStatus.active
    created_at: datetime = Field(default_factory=_utcnow)


class LikenessLicenseCreate(CamelModel):
    grantee_type: GranteeType = GranteeType.platform
    brand_id: Optional[str] = None
    media_scope: MediaScope = MediaScope.both
    allowed_use: Optional[str] = None
    territory: Optional[str] = None
    term_start: Optional[date] = None
    term_end: Optional[date] = None
    rate_model: RateModel = RateModel.per_generation
    rate_amount: int = 0
    currency: str = "INR"


class LikenessLicenseUpdate(CamelModel):
    status: Optional[LicenseStatus] = None
    media_scope: Optional[MediaScope] = None
    allowed_use: Optional[str] = None
    rate_model: Optional[RateModel] = None
    rate_amount: Optional[int] = None
    term_end: Optional[date] = None
