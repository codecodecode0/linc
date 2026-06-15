"""Dependency wiring.

The single place that decides which concrete repositories and providers the
app uses. To move to Postgres, return Postgres-backed repositories here when
DATABASE_URL is set — no service or router changes. To add a platform, append
its provider to `get_registry`.
"""

from __future__ import annotations

from functools import lru_cache

from .config import Settings, get_settings
from .providers import InstagramProvider, ProviderRegistry, YouTubeProvider
from .repositories import (
    BrandRepository,
    CatalogRepository,
    ConnectionRepository,
    CreatorRepository,
    InMemoryBrandRepository,
    InMemoryCatalogRepository,
    InMemoryConnectionRepository,
    InMemoryCreatorRepository,
    InMemoryOAuthStateRepository,
    InMemoryOtpRepository,
    OAuthStateRepository,
    OtpRepository,
)
from .services import AccountService, AuthService, CreatorService, TokenService


# --- Repository singletons --------------------------------------------------
@lru_cache
def get_creator_repository() -> CreatorRepository:
    # TODO(postgres): return PostgresCreatorRepository when DATABASE_URL is set.
    return InMemoryCreatorRepository()


@lru_cache
def get_brand_repository() -> BrandRepository:
    return InMemoryBrandRepository()


@lru_cache
def get_otp_repository() -> OtpRepository:
    return InMemoryOtpRepository()


@lru_cache
def get_connection_repository() -> ConnectionRepository:
    return InMemoryConnectionRepository()


@lru_cache
def get_state_repository() -> OAuthStateRepository:
    return InMemoryOAuthStateRepository()


@lru_cache
def get_catalog_repository() -> CatalogRepository:
    return InMemoryCatalogRepository()


# --- Providers --------------------------------------------------------------
@lru_cache
def get_registry() -> ProviderRegistry:
    settings = get_settings()
    return ProviderRegistry(
        [
            InstagramProvider(settings),
            YouTubeProvider(settings),
            # Add another platform's provider here — nothing else changes.
        ]
    )


# --- Service singleton ------------------------------------------------------
@lru_cache
def get_creator_service() -> CreatorService:
    return CreatorService(
        creators=get_creator_repository(),
        connections=get_connection_repository(),
        states=get_state_repository(),
        registry=get_registry(),
        settings=get_settings(),
    )


@lru_cache
def get_account_service() -> AccountService:
    return AccountService(
        creators=get_creator_repository(),
        brands=get_brand_repository(),
    )


@lru_cache
def get_token_service() -> TokenService:
    s = get_settings()
    return TokenService(secret=s.auth_secret, ttl_seconds=s.session_ttl_seconds)


@lru_cache
def get_auth_service() -> AuthService:
    return AuthService(
        settings=get_settings(),
        creators=get_creator_repository(),
        brands=get_brand_repository(),
        otps=get_otp_repository(),
        tokens=get_token_service(),
    )


def settings() -> Settings:
    return get_settings()
