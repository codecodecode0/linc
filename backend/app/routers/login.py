"""Account login: email/phone OTP and Google ("Sign in with Gmail").

Routes live under /api/auth/otp/* and /api/auth/google/* with literal segments,
and are registered BEFORE the social-platform OAuth router so they win over the
`/api/auth/{platform}/...` pattern.
"""

from __future__ import annotations

from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import RedirectResponse

from ..config import Settings
from ..deps import get_auth_service, settings as get_settings_dep
from ..models import AccountType, OtpRequest, OtpRequestResult, OtpVerify, Session
from ..services import AuthError, AuthService

router = APIRouter(prefix="/api/auth", tags=["login"])


@router.post("/otp/request", response_model=OtpRequestResult)
def request_otp(body: OtpRequest, auth: AuthService = Depends(get_auth_service)):
    return auth.request_otp(body.channel, body.value)


@router.post("/otp/verify", response_model=Session)
def verify_otp(body: OtpVerify, auth: AuthService = Depends(get_auth_service)):
    try:
        return auth.verify_otp(body.channel, body.value, body.code, body.account_type)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc))


@router.get("/google/login")
def google_login(
    account_type: AccountType = Query(AccountType.creator),
    auth: AuthService = Depends(get_auth_service),
):
    return RedirectResponse(auth.google_login_url(account_type))


@router.get("/google/callback")
async def google_callback(
    state: str = Query(...),
    code: str = Query(default=""),
    error: str = Query(default=""),
    auth: AuthService = Depends(get_auth_service),
    config: Settings = Depends(get_settings_dep),
):
    base = f"{config.frontend_url.rstrip('/')}/app.html"
    if error or not code:
        return RedirectResponse(f"{base}?{urlencode({'error': error or 'denied'})}")
    try:
        session = await auth.complete_google(code, state)
    except AuthError as exc:
        return RedirectResponse(f"{base}?{urlencode({'error': str(exc)})}")
    # Hand the session token back to the UI.
    params = urlencode(
        {"token": session.token, "loggedIn": session.account_type.value}
    )
    return RedirectResponse(f"{base}?{params}")


@router.get("/me", response_model=Session)
def whoami(
    authorization: str = Header(default=""),
    auth: AuthService = Depends(get_auth_service),
):
    token = authorization[7:] if authorization.lower().startswith("bearer ") else ""
    session = auth.account_from_token(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return session
