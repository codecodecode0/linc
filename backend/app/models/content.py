from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import Field

from .base import CamelModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ContentType(str, Enum):
    raw_video = "raw_video"
    edited_video = "edited_video"
    image = "image"
    reel = "reel"
    story = "story"


class ContentStatus(str, Enum):
    requested = "requested"
    submitted = "submitted"
    in_review = "in_review"
    revisions_requested = "revisions_requested"
    approved = "approved"
    delivered = "delivered"
    rejected = "rejected"


class Content(CamelModel):
    id: str
    deal_id: str
    title: str
    type: ContentType
    status: ContentStatus = ContentStatus.requested
    revision_no: int = 0
    asset_url: Optional[str] = None  # uploaded file / generated asset
    due_date: Optional[date] = None
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)


class ContentCreate(CamelModel):
    title: str
    type: ContentType
    due_date: Optional[date] = None
    notes: Optional[str] = None


class ContentUpdate(CamelModel):
    status: Optional[ContentStatus] = None
    asset_url: Optional[str] = None
    revision_no: Optional[int] = None
    notes: Optional[str] = None
