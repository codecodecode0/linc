"""Deal CRUD (a campaign ↔ creator booking).

  POST/GET   /api/campaigns/{campaign_id}/deals
  GET/PATCH/DELETE  /api/deals/{deal_id}
"""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ..deps import get_campaign_service, get_creator_service, get_deal_service
from ..models import Campaign, Deal, DealCreate, DealUpdate
from ..services import CreatorNotFound, CreatorService, CrudService, NotFound

router = APIRouter(tags=["deals"])


@router.post("/api/campaigns/{campaign_id}/deals", response_model=Deal, status_code=201)
def create_deal(
    campaign_id: str,
    body: DealCreate,
    campaigns: CrudService[Campaign] = Depends(get_campaign_service),
    creators: CreatorService = Depends(get_creator_service),
    service: CrudService[Deal] = Depends(get_deal_service),
):
    try:
        campaigns.get(campaign_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Campaign not found")
    try:
        creators.get_creator(body.creator_id)
    except CreatorNotFound:
        raise HTTPException(status_code=404, detail="Creator not found")

    deal = Deal(
        id=str(uuid.uuid4()), campaign_id=campaign_id, **body.model_dump(exclude_none=True)
    )
    return service.create(deal)


@router.get("/api/campaigns/{campaign_id}/deals", response_model=List[Deal])
def list_deals(
    campaign_id: str, service: CrudService[Deal] = Depends(get_deal_service)
):
    return service.list(campaign_id=campaign_id)


@router.get("/api/deals/{deal_id}", response_model=Deal)
def get_deal(deal_id: str, service: CrudService[Deal] = Depends(get_deal_service)):
    try:
        return service.get(deal_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Deal not found")


@router.patch("/api/deals/{deal_id}", response_model=Deal)
def update_deal(
    deal_id: str,
    body: DealUpdate,
    service: CrudService[Deal] = Depends(get_deal_service),
):
    try:
        return service.update(deal_id, body.model_dump(exclude_none=True))
    except NotFound:
        raise HTTPException(status_code=404, detail="Deal not found")


@router.delete("/api/deals/{deal_id}", status_code=204)
def delete_deal(deal_id: str, service: CrudService[Deal] = Depends(get_deal_service)):
    try:
        service.delete(deal_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Deal not found")
