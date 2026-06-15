from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import Field

from .base import CamelModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DealType(str, Enum):
    real_video = "real_video"
    ai_static = "ai_static"
    ai_video = "ai_video"


class DealStatus(str, Enum):
    draft = "draft"
    offered = "offered"
    countered = "countered"
    accepted = "accepted"
    rejected = "rejected"
    withdrawn = "withdrawn"
    contracted = "contracted"
    in_production = "in_production"
    content_submitted = "content_submitted"
    in_review = "in_review"
    revisions = "revisions"
    approved = "approved"
    completed = "completed"
    cancelled = "cancelled"
    disputed = "disputed"


class Deal(CamelModel):
    id: str
    campaign_id: str
    creator_id: str
    type: DealType
    status: DealStatus = DealStatus.draft
    quote_amount: int = 0  # rupees
    currency: str = "INR"
    brief: Dict[str, Any] = Field(default_factory=dict)
    due_date: Optional[date] = None
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=_utcnow)


class DealCreate(CamelModel):
    creator_id: str
    type: DealType
    quote_amount: int = 0
    currency: str = "INR"
    brief: Optional[Dict[str, Any]] = None
    due_date: Optional[date] = None


class DealUpdate(CamelModel):
    status: Optional[DealStatus] = None
    quote_amount: Optional[int] = None
    brief: Optional[Dict[str, Any]] = None
    due_date: Optional[date] = None
