"""Platform catalog endpoints powering the dashboards."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends

from ..deps import get_catalog_repository
from ..models import Activity, CampaignSummary, DealSummary, PlatformStats
from ..repositories import CatalogRepository

# Demo/showcase data powering the marketing dashboards. The real, CRUD-managed
# Deal/Campaign entities live under /api/campaigns/{id} and /api/deals/{id}.
router = APIRouter(prefix="/api", tags=["platform"])


@router.get("/stats", response_model=PlatformStats)
def stats(repo: CatalogRepository = Depends(get_catalog_repository)):
    return repo.stats()


@router.get("/deals", response_model=List[DealSummary])
def deals(repo: CatalogRepository = Depends(get_catalog_repository)):
    return repo.deals()


@router.get("/campaigns", response_model=List[CampaignSummary])
def campaigns(repo: CatalogRepository = Depends(get_catalog_repository)):
    return repo.campaigns()


@router.get("/activity", response_model=List[Activity])
def activity(repo: CatalogRepository = Depends(get_catalog_repository)):
    return repo.activity()
