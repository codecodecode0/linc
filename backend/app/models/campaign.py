from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import CamelModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CampaignObjective(str, Enum):
    awareness = "awareness"
    traffic = "traffic"
    engagement = "engagement"
    conversions = "conversions"
    app_installs = "app_installs"


class CampaignStatus(str, Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    completed = "completed"
    archived = "archived"


class Campaign(CamelModel):
    id: str
    brand_id: str
    name: str
    objective: CampaignObjective = CampaignObjective.awareness
    product_category: Optional[str] = None
    status: CampaignStatus = CampaignStatus.draft
    budget_amount: int = 0  # rupees
    spend_amount: int = 0
    currency: str = "INR"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    target_audience: Dict[str, Any] = Field(default_factory=dict)
    platforms: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_utcnow)


class CampaignCreate(CamelModel):
    name: str
    objective: CampaignObjective = CampaignObjective.awareness
    product_category: Optional[str] = None
    budget_amount: int = 0
    currency: str = "INR"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    target_audience: Optional[Dict[str, Any]] = None
    platforms: Optional[List[str]] = None


class CampaignUpdate(CamelModel):
    name: Optional[str] = None
    objective: Optional[CampaignObjective] = None
    product_category: Optional[str] = None
    status: Optional[CampaignStatus] = None
    budget_amount: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    target_audience: Optional[Dict[str, Any]] = None
    platforms: Optional[List[str]] = None
