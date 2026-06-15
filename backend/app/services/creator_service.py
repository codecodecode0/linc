"""Orchestrates creators, their social connections and insights.

Platform-agnostic: it resolves the right provider from the registry and never
hard-codes Instagram, YouTube, etc.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from ..config import Settings
from ..models import Creator, Platform, SocialConnection, SocialInsights
from ..providers import ProviderRegistry
from ..repositories import ConnectionRepository, CreatorRepository, OAuthStateRepository


class CreatorNotFound(Exception):
    pass


class NotConnected(Exception):
    pass


class CreatorService:
    def __init__(
        self,
        creators: CreatorRepository,
        connections: ConnectionRepository,
        states: OAuthStateRepository,
        registry: ProviderRegistry,
        settings: Settings,
    ) -> None:
        self._creators = creators
        self._connections = connections
        self._states = states
        self._registry = registry
        self._settings = settings

    # -- Creators -----------------------------------------------------------
    def list_creators(self) -> List[Creator]:
        creators = self._creators.list()
        for c in creators:
            c.connected_platforms = [
                conn.platform for conn in self._connections.list_for_creator(c.id)
            ]
        return creators

    def get_creator(self, creator_id: str) -> Creator:
        creator = self._creators.get(creator_id)
        if not creator:
            raise CreatorNotFound(creator_id)
        creator.connected_platforms = [
            conn.platform for conn in self._connections.list_for_creator(creator_id)
        ]
        return creator

    # -- Connection flow ----------------------------------------------------
    def start_connect(self, creator_id: str, platform: Platform) -> str:
        self.get_creator(creator_id)  # validate creator exists
        provider = self._registry.get(platform)
        state = uuid.uuid4().hex
        self._states.save(state, creator_id)
        return provider.authorize_url(state, self._settings.redirect_uri(platform.value))

    async def complete_connect(
        self, platform: Platform, code: str, state: str
    ) -> Tuple[str, SocialConnection]:
        creator_id = self._states.pop(state)
        if not creator_id:
            from ..providers import ProviderError

            raise ProviderError("Invalid or expired OAuth state.")

        provider = self._registry.get(platform)
        redirect_uri = self._settings.redirect_uri(platform.value)
        token = await provider.exchange_code(code, redirect_uri)
        account = await provider.fetch_account(token.access_token)

        now = datetime.now(timezone.utc)
        connection = SocialConnection(
            id=str(uuid.uuid4()),
            creator_id=creator_id,
            platform=platform,
            account_id=account.account_id,
            username=account.username,
            profile_picture=account.profile_picture or None,
            followers_count=account.followers_count,
            scopes=account.scopes,
            connected_at=now,
            token_expires_at=now + timedelta(seconds=token.expires_in),
            metadata=account.metadata,
            access_token=token.access_token,
            refresh_token=token.refresh_token or None,
        )
        self._connections.upsert(connection)
        return creator_id, connection

    def list_connections(self, creator_id: str) -> List[SocialConnection]:
        return self._connections.list_for_creator(creator_id)

    def get_connection(
        self, creator_id: str, platform: Platform
    ) -> Optional[SocialConnection]:
        return self._connections.get(creator_id, platform)

    def disconnect(self, creator_id: str, platform: Platform) -> bool:
        return self._connections.delete(creator_id, platform)

    # -- Insights -----------------------------------------------------------
    async def get_insights(
        self, creator_id: str, platform: Platform
    ) -> SocialInsights:
        connection = self._connections.get(creator_id, platform)
        if not connection:
            raise NotConnected(creator_id)
        provider = self._registry.get(platform)
        return await provider.fetch_insights(connection)
