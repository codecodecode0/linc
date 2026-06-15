"""Content (deliverable) CRUD, scoped to a deal.

  POST/GET   /api/deals/{deal_id}/content
  GET/PATCH/DELETE  /api/content/{content_id}
"""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ..deps import get_content_service, get_deal_service
from ..models import Content, ContentCreate, ContentUpdate, Deal
from ..services import CrudService, NotFound

router = APIRouter(tags=["content"])


@router.post("/api/deals/{deal_id}/content", response_model=Content, status_code=201)
def create_content(
    deal_id: str,
    body: ContentCreate,
    deals: CrudService[Deal] = Depends(get_deal_service),
    service: CrudService[Content] = Depends(get_content_service),
):
    try:
        deals.get(deal_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Deal not found")
    content = Content(
        id=str(uuid.uuid4()), deal_id=deal_id, **body.model_dump(exclude_none=True)
    )
    return service.create(content)


@router.get("/api/deals/{deal_id}/content", response_model=List[Content])
def list_content(
    deal_id: str, service: CrudService[Content] = Depends(get_content_service)
):
    return service.list(deal_id=deal_id)


@router.get("/api/content/{content_id}", response_model=Content)
def get_content(
    content_id: str, service: CrudService[Content] = Depends(get_content_service)
):
    try:
        return service.get(content_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Content not found")


@router.patch("/api/content/{content_id}", response_model=Content)
def update_content(
    content_id: str,
    body: ContentUpdate,
    service: CrudService[Content] = Depends(get_content_service),
):
    try:
        return service.update(content_id, body.model_dump(exclude_none=True))
    except NotFound:
        raise HTTPException(status_code=404, detail="Content not found")


@router.delete("/api/content/{content_id}", status_code=204)
def delete_content(
    content_id: str, service: CrudService[Content] = Depends(get_content_service)
):
    try:
        service.delete(content_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Content not found")
