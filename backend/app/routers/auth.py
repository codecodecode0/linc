"""Social OAuth endpoints — one set of routes for every platform.

  GET /api/auth/{platform}/login?creator_id=...   -> redirect to the platform
  GET /api/auth/{platform}/callback?code=&state=  -> finish, redirect to UI
"""

from __future__ import annotations

from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse

from ..config import Settings
from ..deps import get_creator_service, settings as get_settings_dep
from ..models import Platform
from ..providers import ProviderError, UnknownPlatform
from ..services import CreatorNotFound, CreatorService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/{platform}/login")
def login(
    platform: Platform,
    creator_id: str = Query(...),
    service: CreatorService = Depends(get_creator_service),
    config: Settings = Depends(get_settings_dep),
):
    try:
        url = service.start_connect(creator_id, platform)
    except CreatorNotFound:
        return RedirectResponse(_ui_redirect(config, error="unknown_creator"))
    except UnknownPlatform:
        return RedirectResponse(_ui_redirect(config, error="unsupported_platform"))
    return RedirectResponse(url)


@router.get("/{platform}/callback")
async def callback(
    platform: Platform,
    state: str = Query(...),
    code: str = Query(default=""),
    error: str = Query(default=""),
    service: CreatorService = Depends(get_creator_service),
    config: Settings = Depends(get_settings_dep),
):
    if error or not code:
        return RedirectResponse(_ui_redirect(config, error=error or "denied"))

    try:
        creator_id, _ = await service.complete_connect(
            platform=platform, code=code, state=state
        )
    except (ProviderError, UnknownPlatform) as exc:
        return RedirectResponse(_ui_redirect(config, error=str(exc)))

    return RedirectResponse(
        _ui_redirect(config, connected=platform.value, creator=creator_id)
    )


def _ui_redirect(config: Settings, **params: str) -> str:
    query = urlencode({k: v for k, v in params.items() if v})
    base = config.frontend_url.rstrip("/")
    return f"{base}/?{query}#creator"
