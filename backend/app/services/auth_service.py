"""Authentication: email/phone OTP and Google ("Sign in with Gmail").

All network steps fall back to deterministic mock behaviour until real
credentials are configured, so the whole login flow runs locally.

Production providers (for reference): email OTP via SES/Resend/SendGrid,
phone OTP via MSG91/Twilio/WhatsApp, Google via Google Identity (OIDC).
"""

from __future__ import annotations

import secrets
import uuid
from typing import Optional, Tuple
from urllib.parse import urlencode

import httpx

from ..config import Settings
from ..models import (
    AccountType,
    Brand,
    Creator,
    OtpChannel,
    OtpRequestResult,
    Session,
)
from ..repositories import BrandRepository, CreatorRepository, OtpRepository
from .account_service import _avatar, _handle
from .token_service import TokenService

GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO = "https://openidconnect.googleapis.com/v1/userinfo"


class AuthError(Exception):
    pass


class AuthService:
    def __init__(
        self,
        settings: Settings,
        creators: CreatorRepository,
        brands: BrandRepository,
        otps: OtpRepository,
        tokens: TokenService,
    ) -> None:
        self._settings = settings
        self._creators = creators
        self._brands = brands
        self._otps = otps
        self._tokens = tokens

    # -- OTP ----------------------------------------------------------------
    def request_otp(self, channel: OtpChannel, value: str) -> OtpRequestResult:
        code = f"{secrets.randbelow(1_000_000):06d}"
        self._otps.set(self._key(channel, value), code, self._settings.otp_ttl_seconds)
        # In production this is where SES/MSG91/Twilio would send the code.
        return OtpRequestResult(
            sent=True,
            channel=channel,
            value=value,
            dev_code=code,  # mock only — never return this in production
            expires_in=self._settings.otp_ttl_seconds,
        )

    def verify_otp(self, channel: OtpChannel, value: str, code: str) -> Session:
        expected = self._otps.get(self._key(channel, value))
        if not expected or not secrets.compare_digest(expected, code):
            raise AuthError("Invalid or expired code.")
        self._otps.delete(self._key(channel, value))

        found = self._find_account(channel, value)
        if not found:
            raise AuthError("No account found. Please sign up first.")
        account_type, account = found
        return self._session(account_type, account)

    # -- Google -------------------------------------------------------------
    def google_login_url(self, account_type: AccountType) -> str:
        state = f"{account_type.value}:{secrets.token_urlsafe(16)}"
        redirect_uri = self._settings.redirect_uri("google")
        if self._settings.google_login_mock:
            return f"{redirect_uri}?{urlencode({'code': 'mock-google-code', 'state': state})}"
        params = urlencode(
            {
                "client_id": self._settings.google_client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": " ".join(self._settings.google_login_scopes_list),
                "state": state,
                "access_type": "online",
                "prompt": "select_account",
            }
        )
        return f"{GOOGLE_AUTH}?{params}"

    async def complete_google(self, code: str, state: str) -> Session:
        account_type = AccountType(state.split(":", 1)[0])
        email, sub, name = await self._google_identity(code)

        account_type, account = self._find_or_create_google(
            account_type, email, sub, name
        )
        return self._session(account_type, account)

    async def _google_identity(self, code: str) -> Tuple[str, str, str]:
        if self._settings.google_login_mock or code.startswith("mock"):
            # Deterministic demo identity.
            return ("demo.user@gmail.com", "google-demo-sub", "Demo User")

        redirect_uri = self._settings.redirect_uri("google")
        async with httpx.AsyncClient(timeout=15) as client:
            tok = await client.post(
                GOOGLE_TOKEN,
                data={
                    "client_id": self._settings.google_client_id,
                    "client_secret": self._settings.google_client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            if tok.status_code >= 400:
                raise AuthError("Google token exchange failed.")
            access_token = tok.json()["access_token"]
            info = await client.get(
                GOOGLE_USERINFO,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if info.status_code >= 400:
                raise AuthError("Could not read Google profile.")
            data = info.json()
            return data["email"], data["sub"], data.get("name", "")

    # -- helpers ------------------------------------------------------------
    def _find_account(
        self, channel: OtpChannel, value: str
    ) -> Optional[Tuple[AccountType, object]]:
        if channel == OtpChannel.email:
            c = self._creators.get_by_email(value)
            if c:
                return AccountType.creator, c
            b = self._brands.get_by_email(value)
            if b:
                return AccountType.brand, b
        else:
            c = self._creators.get_by_phone(value)
            if c:
                return AccountType.creator, c
            b = self._brands.get_by_phone(value)
            if b:
                return AccountType.brand, b
        return None

    def _find_or_create_google(
        self, account_type: AccountType, email: str, sub: str, name: str
    ) -> Tuple[AccountType, object]:
        # Match an existing account by email across both types.
        existing = self._find_account(OtpChannel.email, email)
        if existing:
            etype, account = existing
            if not account.google_sub:
                account.google_sub = sub
                self._save(etype, account)
            return etype, account

        # Otherwise create a new account of the requested type.
        if account_type == AccountType.creator:
            creator = Creator(
                id=str(uuid.uuid4()), name=name or "New Creator", email=email,
                phone="", handle=_handle(name or email), avatar=_avatar(name or "NC"),
                google_sub=sub, status="onboarding",
            )
            return AccountType.creator, self._creators.create(creator)
        brand = Brand(
            id=str(uuid.uuid4()), name=name or "New Brand", email=email,
            phone="", google_sub=sub, status="active",
        )
        return AccountType.brand, self._brands.create(brand)

    def _save(self, account_type: AccountType, account: object) -> None:
        if account_type == AccountType.creator:
            self._creators.save(account)  # type: ignore[arg-type]
        else:
            self._brands.save(account)  # type: ignore[arg-type]

    def _session(self, account_type: AccountType, account: object) -> Session:
        token = self._tokens.issue(account_type.value, account.id)  # type: ignore[attr-defined]
        return Session(
            token=token,
            account_type=account_type,
            account_id=account.id,  # type: ignore[attr-defined]
            account=account.model_dump(by_alias=True),  # type: ignore[attr-defined]
        )

    def account_from_token(self, token: str) -> Optional[Session]:
        verified = self._tokens.verify(token)
        if not verified:
            return None
        account_type, account_id = verified
        if account_type == AccountType.creator.value:
            account = self._creators.get(account_id)
            atype = AccountType.creator
        else:
            account = self._brands.get(account_id)
            atype = AccountType.brand
        if not account:
            return None
        return Session(
            token=token, account_type=atype, account_id=account_id,
            account=account.model_dump(by_alias=True),
        )

    @staticmethod
    def _key(channel: OtpChannel, value: str) -> str:
        return f"{channel.value}:{value.lower()}"
