"""Instagram provider (via Meta / Facebook Login + Instagram Graph API)."""

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


class InstagramProvider(SocialProvider):
    platform = Platform.instagram

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def is_mock(self) -> bool:
        return not (self._settings.meta_app_id and self._settings.meta_app_secret)

    # -- OAuth --------------------------------------------------------------
    def authorize_url(self, state: str, redirect_uri: str) -> str:
        if self.is_mock:
            return self.mock_authorize_url(state, redirect_uri)
        params = urlencode(
            {
                "client_id": self._settings.meta_app_id,
                "redirect_uri": redirect_uri,
                "scope": ",".join(self._settings.meta_scopes_list),
                "response_type": "code",
                "state": state,
            }
        )
        return f"{self._settings.oauth_dialog_base}?{params}"

    async def exchange_code(self, code: str, redirect_uri: str) -> TokenResult:
        if self.is_mock or code.startswith("mock"):
            return TokenResult(access_token="mock-ig-token", expires_in=5_184_000)

        async with httpx.AsyncClient(timeout=15) as client:
            short = await client.get(
                f"{self._settings.graph_base}/oauth/access_token",
                params={
                    "client_id": self._settings.meta_app_id,
                    "client_secret": self._settings.meta_app_secret,
                    "redirect_uri": redirect_uri,
                    "code": code,
                },
            )
            _raise_for_graph(short)
            short_token = short.json()["access_token"]

            long = await client.get(
                f"{self._settings.graph_base}/oauth/access_token",
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": self._settings.meta_app_id,
                    "client_secret": self._settings.meta_app_secret,
                    "fb_exchange_token": short_token,
                },
            )
            _raise_for_graph(long)
            payload = long.json()
            return TokenResult(
                access_token=payload["access_token"],
                expires_in=int(payload.get("expires_in", 5_184_000)),
            )

    async def fetch_account(self, access_token: str) -> ProviderAccount:
        if self.is_mock or access_token.startswith("mock"):
            return ProviderAccount(
                account_id="17841400000000000",
                username="mayacreates",
                followers_count=480000,
                scopes=self._settings.meta_scopes_list,
                metadata={"ig_user_id": "17841400000000000"},
            )

        async with httpx.AsyncClient(timeout=15) as client:
            pages = await client.get(
                f"{self._settings.graph_base}/me/accounts",
                params={
                    "fields": "instagram_business_account",
                    "access_token": access_token,
                },
            )
            _raise_for_graph(pages)
            ig_account = next(
                (
                    p["instagram_business_account"]["id"]
                    for p in pages.json().get("data", [])
                    if p.get("instagram_business_account")
                ),
                None,
            )
            if not ig_account:
                raise ProviderError(
                    "No Instagram Professional account is linked to this login."
                )

            profile = await client.get(
                f"{self._settings.graph_base}/{ig_account}",
                params={
                    "fields": "username,followers_count,profile_picture_url",
                    "access_token": access_token,
                },
            )
            _raise_for_graph(profile)
            info = profile.json()
            return ProviderAccount(
                account_id=ig_account,
                username=info.get("username", ""),
                followers_count=int(info.get("followers_count", 0)),
                profile_picture=info.get("profile_picture_url", ""),
                scopes=self._settings.meta_scopes_list,
                metadata={"ig_user_id": ig_account},
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
        ig = connection.account_id
        token = connection.access_token
        base = self._settings.graph_base

        async with httpx.AsyncClient(timeout=15) as client:
            profile = (
                await client.get(
                    f"{base}/{ig}",
                    params={"fields": "followers_count", "access_token": token},
                )
            ).json()
            metrics_resp = (
                await client.get(
                    f"{base}/{ig}/insights",
                    params={
                        "metric": "reach,impressions,profile_views",
                        "period": "day",
                        "access_token": token,
                    },
                )
            ).json()

        followers = int(profile.get("followers_count", connection.followers_count))
        m = {"reach": 0, "impressions": 0, "profile_views": 0}
        for item in metrics_resp.get("data", []):
            if item.get("name") in m:
                m[item["name"]] = int((item.get("values") or [{}])[-1].get("value", 0))
        engagement = round(m["reach"] / followers * 100, 1) if followers else 0.0

        return self._build(
            connection, followers, engagement,
            m["reach"], m["impressions"], m["profile_views"], source="live",
        )

    def _mock(self, connection: SocialConnection) -> SocialInsights:
        followers = connection.followers_count or 100000
        seed = sum(ord(c) for c in connection.username) % 20
        engagement = round(3.5 + seed / 10, 1)
        return self._build(
            connection, followers, engagement,
            int(followers * 3.8), int(followers * 6.2), int(followers * 0.12),
            source="mock",
        )

    def _build(self, connection, followers, engagement, reach, impressions,
               profile_views, source) -> SocialInsights:
        return SocialInsights(
            creator_id=connection.creator_id,
            platform=self.platform,
            username=connection.username,
            followers=followers,
            followers_label="Followers",
            metrics=[
                Metric(key="engagement", label="Engagement", value=engagement,
                       format=MetricFormat.percent),
                Metric(key="reach", label="Reach (day)", value=reach),
                Metric(key="impressions", label="Impressions", value=impressions),
                Metric(key="profileViews", label="Profile views", value=profile_views),
            ],
            audience=sample_audience(),
            updated_at=datetime.now(timezone.utc),
            source=source,
        )


def _raise_for_graph(response: httpx.Response) -> None:
    if response.status_code >= 400:
        try:
            err = response.json().get("error", {}).get("message", response.text)
        except Exception:  # noqa: BLE001
            err = response.text
        raise ProviderError(f"Meta Graph API error: {err}")
