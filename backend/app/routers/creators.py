"""Creator + connection + insights endpoints (platform-scoped)."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from ..deps import get_creator_service
from ..models import Creator, Platform, SocialConnection, SocialInsights
from ..services import CreatorNotFound, CreatorService, NotConnected

router = APIRouter(prefix="/api/creators", tags=["creators"])


@router.get("", response_model=List[Creator])
def list_creators(service: CreatorService = Depends(get_creator_service)):
    return service.list_creators()


@router.get("/{creator_id}", response_model=Creator)
def get_creator(creator_id: str, service: CreatorService = Depends(get_creator_service)):
    try:
        return service.get_creator(creator_id)
    except CreatorNotFound:
        raise HTTPException(status_code=404, detail="Creator not found")


@router.get("/{creator_id}/connections", response_model=List[SocialConnection])
def list_connections(
    creator_id: str, service: CreatorService = Depends(get_creator_service)
):
    # Every platform the creator has linked (tokens never included).
    return service.list_connections(creator_id)


@router.get(
    "/{creator_id}/connections/{platform}",
    response_model=Optional[SocialConnection],
)
def get_connection(
    creator_id: str,
    platform: Platform,
    service: CreatorService = Depends(get_creator_service),
):
    return service.get_connection(creator_id, platform)


@router.delete("/{creator_id}/connections/{platform}")
def disconnect(
    creator_id: str,
    platform: Platform,
    service: CreatorService = Depends(get_creator_service),
):
    return {"disconnected": service.disconnect(creator_id, platform)}


@router.get(
    "/{creator_id}/insights/{platform}", response_model=SocialInsights
)
async def get_insights(
    creator_id: str,
    platform: Platform,
    service: CreatorService = Depends(get_creator_service),
):
    try:
        return await service.get_insights(creator_id, platform)
    except NotConnected:
        raise HTTPException(
            status_code=409,
            detail=f"Creator has not connected {platform.value}",
        )
