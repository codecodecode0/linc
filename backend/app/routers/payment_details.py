"""Stored payment details — creator payout accounts and brand payment methods.

  POST/GET   /api/creators/{creator_id}/payout-accounts
  GET/PATCH/DELETE  /api/payout-accounts/{id}
  POST/GET   /api/brands/{brand_id}/payment-methods
  GET/PATCH/DELETE  /api/payment-methods/{id}
"""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ..deps import (
    get_account_service,
    get_creator_service,
    get_payment_method_service,
    get_payout_account_service,
)
from ..models import (
    PaymentMethod,
    PaymentMethodCreate,
    PaymentMethodUpdate,
    PayoutAccount,
    PayoutAccountCreate,
    PayoutAccountUpdate,
)
from ..services import (
    AccountNotFound,
    AccountService,
    CreatorNotFound,
    CreatorService,
    CrudService,
    NotFound,
)

router = APIRouter(tags=["payment-details"])


# --- Creator payout accounts ------------------------------------------------
@router.post(
    "/api/creators/{creator_id}/payout-accounts",
    response_model=PayoutAccount,
    status_code=201,
)
def create_payout_account(
    creator_id: str,
    body: PayoutAccountCreate,
    creators: CreatorService = Depends(get_creator_service),
    service: CrudService[PayoutAccount] = Depends(get_payout_account_service),
):
    try:
        creators.get_creator(creator_id)
    except CreatorNotFound:
        raise HTTPException(status_code=404, detail="Creator not found")
    account = PayoutAccount(
        id=str(uuid.uuid4()), creator_id=creator_id, **body.model_dump(exclude_none=True)
    )
    return service.create(account)


@router.get(
    "/api/creators/{creator_id}/payout-accounts", response_model=List[PayoutAccount]
)
def list_payout_accounts(
    creator_id: str,
    service: CrudService[PayoutAccount] = Depends(get_payout_account_service),
):
    return service.list(creator_id=creator_id)


@router.get("/api/payout-accounts/{account_id}", response_model=PayoutAccount)
def get_payout_account(
    account_id: str,
    service: CrudService[PayoutAccount] = Depends(get_payout_account_service),
):
    try:
        return service.get(account_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Payout account not found")


@router.patch("/api/payout-accounts/{account_id}", response_model=PayoutAccount)
def update_payout_account(
    account_id: str,
    body: PayoutAccountUpdate,
    service: CrudService[PayoutAccount] = Depends(get_payout_account_service),
):
    try:
        return service.update(account_id, body.model_dump(exclude_none=True))
    except NotFound:
        raise HTTPException(status_code=404, detail="Payout account not found")


@router.delete("/api/payout-accounts/{account_id}", status_code=204)
def delete_payout_account(
    account_id: str,
    service: CrudService[PayoutAccount] = Depends(get_payout_account_service),
):
    try:
        service.delete(account_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Payout account not found")


# --- Brand payment methods --------------------------------------------------
@router.post(
    "/api/brands/{brand_id}/payment-methods",
    response_model=PaymentMethod,
    status_code=201,
)
def create_payment_method(
    brand_id: str,
    body: PaymentMethodCreate,
    accounts: AccountService = Depends(get_account_service),
    service: CrudService[PaymentMethod] = Depends(get_payment_method_service),
):
    try:
        accounts.get_brand(brand_id)
    except AccountNotFound:
        raise HTTPException(status_code=404, detail="Brand not found")
    method = PaymentMethod(
        id=str(uuid.uuid4()), brand_id=brand_id, **body.model_dump(exclude_none=True)
    )
    return service.create(method)


@router.get(
    "/api/brands/{brand_id}/payment-methods", response_model=List[PaymentMethod]
)
def list_payment_methods(
    brand_id: str,
    service: CrudService[PaymentMethod] = Depends(get_payment_method_service),
):
    return service.list(brand_id=brand_id)


@router.get("/api/payment-methods/{method_id}", response_model=PaymentMethod)
def get_payment_method(
    method_id: str,
    service: CrudService[PaymentMethod] = Depends(get_payment_method_service),
):
    try:
        return service.get(method_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Payment method not found")


@router.patch("/api/payment-methods/{method_id}", response_model=PaymentMethod)
def update_payment_method(
    method_id: str,
    body: PaymentMethodUpdate,
    service: CrudService[PaymentMethod] = Depends(get_payment_method_service),
):
    try:
        return service.update(method_id, body.model_dump(exclude_none=True))
    except NotFound:
        raise HTTPException(status_code=404, detail="Payment method not found")


@router.delete("/api/payment-methods/{method_id}", status_code=204)
def delete_payment_method(
    method_id: str,
    service: CrudService[PaymentMethod] = Depends(get_payment_method_service),
):
    try:
        service.delete(method_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Payment method not found")
