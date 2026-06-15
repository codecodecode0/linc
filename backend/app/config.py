"""Application configuration, loaded from environment / .env file."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- Instagram / Meta provider (placeholders until provided) ---
    meta_app_id: str = ""
    meta_app_secret: str = ""
    meta_api_version: str = "v21.0"
    meta_scopes: str = (
        "instagram_basic,instagram_manage_insights,"
        "pages_show_list,pages_read_engagement"
    )

    # --- YouTube / Google provider (placeholders until provided) ---
    youtube_client_id: str = ""
    youtube_client_secret: str = ""
    youtube_scopes: str = (
        "https://www.googleapis.com/auth/youtube.readonly,"
        "https://www.googleapis.com/auth/yt-analytics.readonly"
    )

    # --- Google "Sign in with Gmail" (OpenID Connect) — placeholders ---
    google_client_id: str = ""
    google_client_secret: str = ""
    google_login_scopes: str = "openid,email,profile"

    # --- Auth / sessions ---
    auth_secret: str = "dev-insecure-change-me"
    session_ttl_seconds: int = 60 * 60 * 24 * 7  # 7 days
    otp_ttl_seconds: int = 300  # 5 minutes

    # --- App URLs ---
    frontend_url: str = "http://localhost:8000"
    api_base_url: str = "http://localhost:8000"

    # --- CORS ---
    cors_origins: str = "*"

    # --- Database (not used yet — reserved for the Postgres migration) ---
    database_url: str = ""

    # -- Helpers ------------------------------------------------------------
    def redirect_uri(self, platform: str) -> str:
        """OAuth callback URL for a given platform (per-platform by design)."""
        return f"{self.api_base_url.rstrip('/')}/api/auth/{platform}/callback"

    @staticmethod
    def _split(value: str) -> List[str]:
        return [v.strip() for v in value.split(",") if v.strip()]

    @property
    def meta_scopes_list(self) -> List[str]:
        return self._split(self.meta_scopes)

    @property
    def youtube_scopes_list(self) -> List[str]:
        return self._split(self.youtube_scopes)

    @property
    def google_login_scopes_list(self) -> List[str]:
        return self._split(self.google_login_scopes)

    @property
    def google_login_mock(self) -> bool:
        return not (self.google_client_id and self.google_client_secret)

    @property
    def cors_list(self) -> List[str]:
        return self._split(self.cors_origins)

    @property
    def graph_base(self) -> str:
        return f"https://graph.facebook.com/{self.meta_api_version}"

    @property
    def oauth_dialog_base(self) -> str:
        return f"https://www.facebook.com/{self.meta_api_version}/dialog/oauth"


@lru_cache
def get_settings() -> Settings:
    return Settings()
