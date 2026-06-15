"""Campaign CRUD (brand-owned).

  POST/GET   /api/brands/{brand_id}/campaigns
  GET/PATCH/DELETE  /api/campaigns/{campaign_id}
"""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ..deps import get_account_service, get_campaign_service
from ..models import Campaign, CampaignCreate, CampaignUpdate
from ..services import AccountNotFound, AccountService, CrudService, NotFound

router = APIRouter(tags=["campaigns"])


@router.post("/api/brands/{brand_id}/campaigns", response_model=Campaign, status_code=201)
def create_campaign(
    brand_id: str,
    body: CampaignCreate,
    accounts: AccountService = Depends(get_account_service),
    service: CrudService[Campaign] = Depends(get_campaign_service),
):
    try:
        accounts.get_brand(brand_id)
    except AccountNotFound:
        raise HTTPException(status_code=404, detail="Brand not found")
    campaign = Campaign(
        id=str(uuid.uuid4()), brand_id=brand_id, **body.model_dump(exclude_none=True)
    )
    return service.create(campaign)


@router.get("/api/brands/{brand_id}/campaigns", response_model=List[Campaign])
def list_campaigns(
    brand_id: str, service: CrudService[Campaign] = Depends(get_campaign_service)
):
    return service.list(brand_id=brand_id)


@router.get("/api/campaigns/{campaign_id}", response_model=Campaign)
def get_campaign(
    campaign_id: str, service: CrudService[Campaign] = Depends(get_campaign_service)
):
    try:
        return service.get(campaign_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Campaign not found")


@router.patch("/api/campaigns/{campaign_id}", response_model=Campaign)
def update_campaign(
    campaign_id: str,
    body: CampaignUpdate,
    service: CrudService[Campaign] = Depends(get_campaign_service),
):
    try:
        return service.update(campaign_id, body.model_dump(exclude_none=True))
    except NotFound:
        raise HTTPException(status_code=404, detail="Campaign not found")


@router.delete("/api/campaigns/{campaign_id}", status_code=204)
def delete_campaign(
    campaign_id: str, service: CrudService[Campaign] = Depends(get_campaign_service)
):
    try:
        service.delete(campaign_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Campaign not found")
