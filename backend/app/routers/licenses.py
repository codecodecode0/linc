"""Likeness license CRUD (Certified Digi Creator consent), scoped to a creator.

  POST/GET   /api/creators/{creator_id}/licenses
  GET/PATCH/DELETE  /api/licenses/{license_id}
"""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ..deps import get_creator_service, get_license_service
from ..models import LikenessLicense, LikenessLicenseCreate, LikenessLicenseUpdate
from ..services import CreatorNotFound, CreatorService, CrudService, NotFound

router = APIRouter(tags=["licenses"])


@router.post(
    "/api/creators/{creator_id}/licenses",
    response_model=LikenessLicense,
    status_code=201,
)
def create_license(
    creator_id: str,
    body: LikenessLicenseCreate,
    creators: CreatorService = Depends(get_creator_service),
    service: CrudService[LikenessLicense] = Depends(get_license_service),
):
    try:
        creators.get_creator(creator_id)
    except CreatorNotFound:
        raise HTTPException(status_code=404, detail="Creator not found")
    license_ = LikenessLicense(
        id=str(uuid.uuid4()), creator_id=creator_id, **body.model_dump(exclude_none=True)
    )
    return service.create(license_)


@router.get("/api/creators/{creator_id}/licenses", response_model=List[LikenessLicense])
def list_licenses(
    creator_id: str,
    service: CrudService[LikenessLicense] = Depends(get_license_service),
):
    return service.list(creator_id=creator_id)


@router.get("/api/licenses/{license_id}", response_model=LikenessLicense)
def get_license(
    license_id: str,
    service: CrudService[LikenessLicense] = Depends(get_license_service),
):
    try:
        return service.get(license_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="License not found")


@router.patch("/api/licenses/{license_id}", response_model=LikenessLicense)
def update_license(
    license_id: str,
    body: LikenessLicenseUpdate,
    service: CrudService[LikenessLicense] = Depends(get_license_service),
):
    try:
        return service.update(license_id, body.model_dump(exclude_none=True))
    except NotFound:
        raise HTTPException(status_code=404, detail="License not found")


@router.delete("/api/licenses/{license_id}", status_code=204)
def delete_license(
    license_id: str,
    service: CrudService[LikenessLicense] = Depends(get_license_service),
):
    try:
        service.delete(license_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="License not found")
