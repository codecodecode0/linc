from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import field_validator

from .base import CamelModel


class AccountType(str, Enum):
    creator = "creator"
    brand = "brand"


class OtpChannel(str, Enum):
    email = "email"
    phone = "phone"


# --- Request bodies ---------------------------------------------------------
class CreatorCreate(CamelModel):
    name: str
    email: str
    phone: str
    niche: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Enter a valid email address.")
        return value

    @field_validator("phone")
    @classmethod
    def valid_phone(cls, value: str) -> str:
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) < 10:
            raise ValueError("Enter a valid phone number.")
        return value


class BrandCreate(CamelModel):
    name: str
    email: str
    phone: str
    category: Optional[str] = None
    website: Optional[str] = None

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Enter a valid email address.")
        return value

    @field_validator("phone")
    @classmethod
    def valid_phone(cls, value: str) -> str:
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) < 10:
            raise ValueError("Enter a valid phone number.")
        return value


class CreatorUpdate(CamelModel):
    name: Optional[str] = None
    niche: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    rate: Optional[int] = None


class BrandUpdate(CamelModel):
    name: Optional[str] = None
    category: Optional[str] = None
    website: Optional[str] = None


class OtpRequest(CamelModel):
    channel: OtpChannel
    value: str  # email address or phone number
    account_type: Optional[AccountType] = None


class OtpVerify(CamelModel):
    channel: OtpChannel
    value: str
    code: str
    account_type: Optional[AccountType] = None


# --- Responses --------------------------------------------------------------
class OtpRequestResult(CamelModel):
    sent: bool
    channel: OtpChannel
    value: str
    # Only populated in mock mode so the demo can complete the flow.
    dev_code: Optional[str] = None
    expires_in: int


class Session(CamelModel):
    token: str
    account_type: AccountType
    account_id: str
    account: Dict[str, Any]
