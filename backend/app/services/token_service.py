"""Stateless signed session tokens (HMAC, stdlib only).

A token is `base64(payload).base64(hmac_sha256(payload))`. Good enough for the
demo; swap for JWT/refresh tokens when needed without touching callers.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Optional, Tuple


class TokenService:
    def __init__(self, secret: str, ttl_seconds: int) -> None:
        self._secret = secret.encode()
        self._ttl = ttl_seconds

    def issue(self, account_type: str, account_id: str) -> str:
        payload = {
            "t": account_type,
            "id": account_id,
            "exp": int(time.time()) + self._ttl,
        }
        body = self._b64(json.dumps(payload, separators=(",", ":")).encode())
        return f"{body.decode()}.{self._sign(body).decode()}"

    def verify(self, token: str) -> Optional[Tuple[str, str]]:
        """Return (account_type, account_id) or None if invalid/expired."""
        try:
            body_s, sig_s = token.encode().split(b".", 1)
            if not hmac.compare_digest(sig_s, self._sign(body_s)):
                return None
            payload = json.loads(self._unb64(body_s))
            if int(payload["exp"]) < time.time():
                return None
            return payload["t"], payload["id"]
        except Exception:  # noqa: BLE001
            return None

    # -- helpers ------------------------------------------------------------
    def _sign(self, body: bytes) -> bytes:
        digest = hmac.new(self._secret, body, hashlib.sha256).digest()
        return self._b64(digest)

    @staticmethod
    def _b64(data: bytes) -> bytes:
        return base64.urlsafe_b64encode(data).rstrip(b"=")

    @staticmethod
    def _unb64(data: bytes) -> bytes:
        return base64.urlsafe_b64decode(data + b"=" * (-len(data) % 4))
