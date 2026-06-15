"""Platform catalog endpoints powering the dashboards."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends

from ..deps import get_catalog_repository
from ..models import Activity, Campaign, Deal, PlatformStats
from ..repositories import CatalogRepository

router = APIRouter(prefix="/api", tags=["platform"])


@router.get("/stats", response_model=PlatformStats)
def stats(repo: CatalogRepository = Depends(get_catalog_repository)):
    return repo.stats()


@router.get("/deals", response_model=List[Deal])
def deals(repo: CatalogRepository = Depends(get_catalog_repository)):
    return repo.deals()


@router.get("/campaigns", response_model=List[Campaign])
def campaigns(repo: CatalogRepository = Depends(get_catalog_repository)):
    return repo.campaigns()


@router.get("/activity", response_model=List[Activity])
def activity(repo: CatalogRepository = Depends(get_catalog_repository)):
    return repo.activity()
