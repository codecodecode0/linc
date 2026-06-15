"""The social-provider abstraction.

Every platform integration (Instagram, YouTube, TikTok, …) implements
`SocialProvider`. A provider owns its entire integration: building the
authorize URL, exchanging the code for a token, resolving the account, and
fetching insights. Adding a platform = adding one `SocialProvider` subclass
and registering it — no model, route, or service changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List
from urllib.parse import urlencode

from ..models import (
    AgeGenderBreakdown,
    AudienceDemographics,
    Platform,
    PlaceShare,
    SocialConnection,
    SocialInsights,
)


class ProviderError(Exception):
    """A provider could not complete an OAuth or API operation."""


class UnknownPlatform(Exception):
    """No provider is registered for the requested platform."""


@dataclass
class TokenResult:
    access_token: str
    expires_in: int  # seconds
    refresh_token: str = ""


@dataclass
class ProviderAccount:
    account_id: str
    username: str
    followers_count: int = 0
    profile_picture: str = ""
    scopes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SocialProvider(ABC):
    #: The platform this provider serves.
    platform: Platform

    @property
    @abstractmethod
    def is_mock(self) -> bool:
        """True when credentials are missing — run the flow with sample data."""

    @abstractmethod
    def authorize_url(self, state: str, redirect_uri: str) -> str: ...

    @abstractmethod
    async def exchange_code(self, code: str, redirect_uri: str) -> TokenResult: ...

    @abstractmethod
    async def fetch_account(self, access_token: str) -> ProviderAccount: ...

    @abstractmethod
    async def fetch_insights(self, connection: SocialConnection) -> SocialInsights: ...

    # -- Shared helper ------------------------------------------------------
    def mock_authorize_url(
        self, state: str, redirect_uri: str, code: str = "mock-auth-code"
    ) -> str:
        """Skip the real dialog and bounce straight back to our callback."""
        return f"{redirect_uri}?{urlencode({'code': code, 'state': state})}"


def sample_audience() -> AudienceDemographics:
    """A realistic India-weighted audience, shared by mock insights."""
    return AudienceDemographics(
        age_gender=[
            AgeGenderBreakdown(label="18-24", female=16.4, male=8.2),
            AgeGenderBreakdown(label="25-34", female=24.1, male=12.7),
            AgeGenderBreakdown(label="35-44", female=14.3, male=9.1),
            AgeGenderBreakdown(label="45-54", female=6.2, male=4.0),
            AgeGenderBreakdown(label="55+", female=2.8, male=1.9),
        ],
        top_cities=[
            PlaceShare(name="Mumbai", share=18.6),
            PlaceShare(name="Delhi", share=14.2),
            PlaceShare(name="Bengaluru", share=11.5),
            PlaceShare(name="Hyderabad", share=7.8),
            PlaceShare(name="Pune", share=6.1),
        ],
        top_countries=[
            PlaceShare(name="India", share=82.0),
            PlaceShare(name="United States", share=5.4),
            PlaceShare(name="UAE", share=3.6),
            PlaceShare(name="United Kingdom", share=2.7),
        ],
    )
