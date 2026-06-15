"""Stored payment details (no money movement here — that's the payments layer).

PayoutAccount = a creator's bank/UPI destination.
PaymentMethod = a brand's funding instrument (gateway token).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import Field

from .base import CamelModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# --- Creator payout account -------------------------------------------------
class PayoutMethod(str, Enum):
    bank = "bank"
    upi = "upi"


class VerificationStatus(str, Enum):
    pending = "pending"
    verified = "verified"
    failed = "failed"


class PayoutAccount(CamelModel):
    id: str
    creator_id: str
    method: PayoutMethod
    account_name: str
    account_number: Optional[str] = None  # encrypt at rest in production
    ifsc: Optional[str] = None
    upi_vpa: Optional[str] = None
    pan: Optional[str] = None
    gstin: Optional[str] = None
    is_default: bool = False
    verification: VerificationStatus = VerificationStatus.pending
    created_at: datetime = Field(default_factory=_utcnow)


class PayoutAccountCreate(CamelModel):
    method: PayoutMethod
    account_name: str
    account_number: Optional[str] = None
    ifsc: Optional[str] = None
    upi_vpa: Optional[str] = None
    pan: Optional[str] = None
    gstin: Optional[str] = None
    is_default: bool = False


class PayoutAccountUpdate(CamelModel):
    account_name: Optional[str] = None
    ifsc: Optional[str] = None
    upi_vpa: Optional[str] = None
    pan: Optional[str] = None
    gstin: Optional[str] = None
    is_default: Optional[bool] = None
    verification: Optional[VerificationStatus] = None


# --- Brand payment method ---------------------------------------------------
class PaymentInstrument(str, Enum):
    card = "card"
    upi = "upi"
    netbanking = "netbanking"
    upi_autopay = "upi_autopay"
    enach = "enach"


class PaymentMethod(CamelModel):
    id: str
    brand_id: str
    gateway: str = "razorpay"
    kind: PaymentInstrument
    label: str  # e.g. "HDFC •• 4321"
    is_default: bool = False
    status: str = "active"
    created_at: datetime = Field(default_factory=_utcnow)


class PaymentMethodCreate(CamelModel):
    gateway: str = "razorpay"
    kind: PaymentInstrument
    label: str
    is_default: bool = False


class PaymentMethodUpdate(CamelModel):
    label: Optional[str] = None
    is_default: Optional[bool] = None
    status: Optional[str] = None
