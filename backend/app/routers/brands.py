"""Brand account CRUD."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..deps import get_account_service
from ..models import Brand, BrandCreate, BrandUpdate
from ..services import AccountNotFound, AccountService, DuplicateAccount

router = APIRouter(prefix="/api/brands", tags=["brands"])


@router.post("", response_model=Brand, status_code=201)
def create_brand(
    body: BrandCreate, service: AccountService = Depends(get_account_service)
):
    try:
        return service.create_brand(body)
    except DuplicateAccount as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get("/{brand_id}", response_model=Brand)
def get_brand(brand_id: str, service: AccountService = Depends(get_account_service)):
    try:
        return service.get_brand(brand_id)
    except AccountNotFound:
        raise HTTPException(status_code=404, detail="Brand not found")


@router.patch("/{brand_id}", response_model=Brand)
def update_brand(
    brand_id: str,
    body: BrandUpdate,
    service: AccountService = Depends(get_account_service),
):
    try:
        return service.update_brand(brand_id, body)
    except AccountNotFound:
        raise HTTPException(status_code=404, detail="Brand not found")
