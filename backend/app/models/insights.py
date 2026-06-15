from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List

from .base import CamelModel
from .connection import Platform


class MetricFormat(str, Enum):
    number = "number"
    percent = "percent"
    currency = "currency"
    duration = "duration"  # seconds
    hours = "hours"


class Metric(CamelModel):
    """A single headline number. The set differs per platform, so insights
    carry a *list* of these rather than fixed columns."""

    key: str
    label: str
    value: float
    format: MetricFormat = MetricFormat.number


class AgeGenderBreakdown(CamelModel):
    label: str  # e.g. "25-34"
    female: float
    male: float


class PlaceShare(CamelModel):
    name: str
    share: float


class AudienceDemographics(CamelModel):
    age_gender: List[AgeGenderBreakdown]
    top_cities: List[PlaceShare]
    top_countries: List[PlaceShare]


class SocialInsights(CamelModel):
    """Platform-agnostic insights for one connected account."""

    creator_id: str
    platform: Platform
    username: str
    followers: int  # generic audience size
    followers_label: str  # "Followers" / "Subscribers"
    metrics: List[Metric]
    audience: AudienceDemographics
    updated_at: datetime
    source: str  # "live" when pulled from the platform API, else "mock"
