from __future__ import annotations

from .base import CamelModel


class PlatformStats(CamelModel):
    creators_certified: int
    brands_active: int
    agencies_active: int
    ai_ads_generated: int
    paid_to_creators: int  # rupees
    avg_roas: float


# NOTE: these two are read-only *summary* views that power the demo dashboards
# (/api/deals, /api/campaigns). The real, CRUD-managed entities are Deal and
# Campaign in their own modules.
class DealSummary(CamelModel):
    id: str
    title: str
    brand: str
    creator: str
    status: str  # brief | contract | filming | review | paid
    budget: int  # rupees
    path: str  # video | ai-static | ai-video


class CampaignSummary(CamelModel):
    id: str
    name: str
    brand: str
    creator: str
    status: str  # live | draft | ended
    spend: int  # rupees
    roas: float
    ctr: float
    reach: int


class Activity(CamelModel):
    id: str
    type: str  # earning | match | delivery | campaign
    text: str
    meta: str
    time: str
