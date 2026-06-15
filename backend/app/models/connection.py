from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import CamelModel


class Platform(str, Enum):
    """Supported social platforms. Add a value here only when its provider
    actually exists (see app/providers). Facebook is intentionally absent:
    it's a distinct data surface from Instagram but shares the same Meta login,
    so if we ever need Facebook Page insights we add a provider that reuses the
    Meta app credentials — it isn't covered by the Instagram connection."""

    instagram = "instagram"
    youtube = "youtube"


class ConnectionStatus(str, Enum):
    connected = "connected"
    expired = "expired"
    revoked = "revoked"


class SocialConnection(CamelModel):
    """A creator's linked account on *any* platform.

    Everything platform-specific that doesn't fit the common shape goes in
    `metadata` (e.g. Instagram's `ig_user_id`, YouTube's `channel_id`), so the
    schema never has to grow a column per platform. The access token is stored
    server-side but excluded from every API response.
    """

    id: str
    creator_id: str
    platform: Platform
    account_id: str  # platform's own id for the account
    username: str  # handle / channel name
    profile_picture: Optional[str] = None
    followers_count: int = 0  # followers or subscribers
    scopes: List[str] = Field(default_factory=list)
    status: ConnectionStatus = ConnectionStatus.connected
    connected_at: datetime
    token_expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Sensitive — kept server-side only.
    access_token: str = Field(exclude=True, repr=False)
    refresh_token: Optional[str] = Field(default=None, exclude=True, repr=False)
