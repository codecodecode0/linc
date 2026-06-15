"""YouTube provider (via Google OAuth + YouTube Data API).

Real OAuth + channel statistics are implemented; deeper watch-time analytics
(YouTube Analytics API) is marked TODO. Runs fully in mock mode until Google
credentials are supplied — same as Instagram.
"""

from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlencode

import httpx

from ..config import Settings
from ..models import (
    Metric,
    MetricFormat,
    Platform,
    SocialConnection,
    SocialInsights,
)
from .base import ProviderAccount, ProviderError, SocialProvider, TokenResult, sample_audience

GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"
YOUTUBE_API = "https://www.googleapis.com/youtube/v3"


class YouTubeProvider(SocialProvider):
    platform = Platform.youtube

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def is_mock(self) -> bool:
        return not (
            self._settings.youtube_client_id and self._settings.youtube_client_secret
        )

    # -- OAuth --------------------------------------------------------------
    def authorize_url(self, state: str, redirect_uri: str) -> str:
        if self.is_mock:
            return self.mock_authorize_url(state, redirect_uri)
        params = urlencode(
            {
                "client_id": self._settings.youtube_client_id,
                "redirect_uri": redirect_uri,
                "scope": " ".join(self._settings.youtube_scopes_list),
                "response_type": "code",
                "access_type": "offline",
                "prompt": "consent",
                "state": state,
            }
        )
        return f"{GOOGLE_AUTH}?{params}"

    async def exchange_code(self, code: str, redirect_uri: str) -> TokenResult:
        if self.is_mock or code.startswith("mock"):
            return TokenResult(
                access_token="mock-yt-token",
                expires_in=3600,
                refresh_token="mock-yt-refresh",
            )

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                GOOGLE_TOKEN,
                data={
                    "client_id": self._settings.youtube_client_id,
                    "client_secret": self._settings.youtube_client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            _raise_for_google(resp)
            payload = resp.json()
            return TokenResult(
                access_token=payload["access_token"],
                expires_in=int(payload.get("expires_in", 3600)),
                refresh_token=payload.get("refresh_token", ""),
            )

    async def fetch_account(self, access_token: str) -> ProviderAccount:
        if self.is_mock or access_token.startswith("mock"):
            return ProviderAccount(
                account_id="UC_mock_channel",
                username="Maya Chen",
                followers_count=265000,
                scopes=self._settings.youtube_scopes_list,
                metadata={"channel_id": "UC_mock_channel"},
            )

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{YOUTUBE_API}/channels",
                params={"part": "snippet,statistics", "mine": "true"},
                headers={"Authorization": f"Bearer {access_token}"},
            )
            _raise_for_google(resp)
            items = resp.json().get("items", [])
            if not items:
                raise ProviderError("No YouTube channel found for this account.")
            ch = items[0]
            stats = ch.get("statistics", {})
            return ProviderAccount(
                account_id=ch["id"],
                username=ch["snippet"].get("title", ""),
                followers_count=int(stats.get("subscriberCount", 0)),
                profile_picture=ch["snippet"]
                .get("thumbnails", {})
                .get("default", {})
                .get("url", ""),
                scopes=self._settings.youtube_scopes_list,
                metadata={"channel_id": ch["id"]},
            )

    # -- Insights -----------------------------------------------------------
    async def fetch_insights(self, connection: SocialConnection) -> SocialInsights:
        if self.is_mock or connection.access_token.startswith("mock"):
            return self._mock(connection)
        try:
            return await self._live(connection)
        except (httpx.HTTPError, ProviderError, KeyError, ValueError):
            return self._mock(connection)

    async def _live(self, connection: SocialConnection) -> SocialInsights:
        channel_id = connection.metadata.get("channel_id", connection.account_id)
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{YOUTUBE_API}/channels",
                params={"part": "statistics", "id": channel_id},
                headers={"Authorization": f"Bearer {connection.access_token}"},
            )
            _raise_for_google(resp)
            stats = resp.json()["items"][0]["statistics"]

        subs = int(stats.get("subscriberCount", connection.followers_count))
        views = int(stats.get("viewCount", 0))
        videos = int(stats.get("videoCount", 0))
        # TODO: watch time / avg view duration via the YouTube Analytics API.
        return self._build(connection, subs, views, videos,
                           watch_hours=0, avg_view=0, source="live")

    def _mock(self, connection: SocialConnection) -> SocialInsights:
        subs = connection.followers_count or 100000
        return self._build(
            connection, subs, views=int(subs * 5.0), videos=180,
            watch_hours=int(subs * 0.18), avg_view=222, source="mock",
        )

    def _build(self, connection, subs, views, videos, watch_hours, avg_view,
               source) -> SocialInsights:
        metrics = [
            Metric(key="views", label="Views (28d)", value=views),
            Metric(key="videos", label="Videos", value=videos),
        ]
        if watch_hours:
            metrics.append(
                Metric(key="watchTime", label="Watch time", value=watch_hours,
                       format=MetricFormat.hours)
            )
        if avg_view:
            metrics.append(
                Metric(key="avgView", label="Avg view", value=avg_view,
                       format=MetricFormat.duration)
            )
        return SocialInsights(
            creator_id=connection.creator_id,
            platform=self.platform,
            username=connection.username,
            followers=subs,
            followers_label="Subscribers",
            metrics=metrics,
            audience=sample_audience(),
            updated_at=datetime.now(timezone.utc),
            source=source,
        )


def _raise_for_google(response: httpx.Response) -> None:
    if response.status_code >= 400:
        try:
            err = response.json().get("error_description") or response.json().get(
                "error", {}
            )
        except Exception:  # noqa: BLE001
            err = response.text
        raise ProviderError(f"Google/YouTube API error: {err}")
