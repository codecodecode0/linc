"""Social OAuth endpoints — one set of routes for every platform.

  GET /api/auth/{platform}/login?creator_id=...&return_to=...  -> redirect
  GET /api/auth/{platform}/callback?code=&state=               -> back to UI
"""

from __future__ import annotations

import base64
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
    return_to: str = Query(default=""),
    service: CreatorService = Depends(get_creator_service),
    config: Settings = Depends(get_settings_dep),
):
    try:
        url = service.start_connect(creator_id, platform, return_to)
    except CreatorNotFound:
        return RedirectResponse(_redirect(config, "", error="unknown_creator"))
    except UnknownPlatform:
        return RedirectResponse(_redirect(config, "", error="unsupported_platform"))
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
    return_to = _decode_return_to(state)
    if error or not code:
        return RedirectResponse(_redirect(config, return_to, error=error or "denied"))

    try:
        creator_id, _ = await service.complete_connect(
            platform=platform, code=code, state=state
        )
    except (ProviderError, UnknownPlatform) as exc:
        return RedirectResponse(_redirect(config, return_to, error=str(exc)))

    return RedirectResponse(
        _redirect(config, return_to, connected=platform.value, creator=creator_id)
    )


def _decode_return_to(state: str) -> str:
    if "." not in state:
        return ""
    enc = state.split(".", 1)[1]
    try:
        return base64.urlsafe_b64decode(enc + "=" * (-len(enc) % 4)).decode()
    except Exception:  # noqa: BLE001
        return ""


def _redirect(config: Settings, return_to: str, **params: str) -> str:
    target = return_to or f"{config.frontend_url.rstrip('/')}/#creator"
    query = urlencode({k: v for k, v in params.items() if v})
    if not query:
        return target
    # Insert the query before any #fragment so hash routing still works.
    if "#" in target:
        base, frag = target.split("#", 1)
        sep = "&" if "?" in base else "?"
        return f"{base}{sep}{query}#{frag}"
    sep = "&" if "?" in target else "?"
    return f"{target}{sep}{query}"
