from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

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


class DealActor(str, Enum):
    brand = "brand"
    creator = "creator"
    system = "system"


class DealActionType(str, Enum):
    send_offer = "send_offer"
    accept = "accept"
    reject = "reject"
    negotiate = "negotiate"
    revise_offer = "revise_offer"
    withdraw = "withdraw"
    mark_contracted = "mark_contracted"
    start_production = "start_production"
    submit_content = "submit_content"
    request_revisions = "request_revisions"
    approve_content = "approve_content"
    complete = "complete"
    cancel = "cancel"


class DealDeliverable(CamelModel):
    title: str
    type: DealType
    quantity: int = Field(default=1, ge=1)
    notes: Optional[str] = None
    due_date: Optional[date] = None


class DealEvent(CamelModel):
    actor: DealActor
    action: DealActionType
    from_status: DealStatus
    to_status: DealStatus
    quote_amount: Optional[int] = None
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)


class Deal(CamelModel):
    id: str
    campaign_id: str
    creator_id: str
    type: DealType
    status: DealStatus = DealStatus.draft
    quote_amount: int = 0  # rupees
    currency: str = "INR"
    brief: Dict[str, Any] = Field(default_factory=dict)
    deliverables: List[DealDeliverable] = Field(default_factory=list)
    last_offer_by: Optional[DealActor] = None
    events: List[DealEvent] = Field(default_factory=list)
    due_date: Optional[date] = None
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=_utcnow)


class DealCreate(CamelModel):
    creator_id: str
    type: DealType
    status: Optional[DealStatus] = None  # defaults to draft if omitted
    quote_amount: int = 0
    currency: str = "INR"
    brief: Optional[Dict[str, Any]] = None
    deliverables: Optional[List[DealDeliverable]] = None
    due_date: Optional[date] = None


class DealUpdate(CamelModel):
    quote_amount: Optional[int] = None
    brief: Optional[Dict[str, Any]] = None
    deliverables: Optional[List[DealDeliverable]] = None
    due_date: Optional[date] = None


class DealAction(CamelModel):
    actor: Optional[DealActor] = None
    action: DealActionType
    quote_amount: Optional[int] = Field(default=None, ge=0)
    note: Optional[str] = None
    deliverables: Optional[List[DealDeliverable]] = None
