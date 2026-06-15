"""Creator & brand account CRUD (in-memory)."""

from __future__ import annotations

import uuid
from typing import Optional

from ..models import (
    Brand,
    BrandCreate,
    BrandUpdate,
    Creator,
    CreatorCreate,
    CreatorUpdate,
)
from ..repositories import BrandRepository, CreatorRepository


class DuplicateAccount(Exception):
    pass


class AccountNotFound(Exception):
    pass


def _avatar(name: str) -> str:
    parts = [p for p in name.split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def _handle(name: str) -> str:
    slug = "".join(ch for ch in name.lower() if ch.isalnum())
    return f"@{slug}" if slug else f"@user{uuid.uuid4().hex[:6]}"


class AccountService:
    def __init__(
        self, creators: CreatorRepository, brands: BrandRepository
    ) -> None:
        self._creators = creators
        self._brands = brands

    # -- Creators -----------------------------------------------------------
    def create_creator(self, data: CreatorCreate) -> Creator:
        if self._creators.get_by_email(data.email):
            raise DuplicateAccount("A creator with this email already exists.")
        if self._creators.get_by_phone(data.phone):
            raise DuplicateAccount("A creator with this phone already exists.")

        creator = Creator(
            id=str(uuid.uuid4()),
            name=data.name,
            email=data.email,
            phone=data.phone,
            handle=_handle(data.name),
            niche=data.niche or "",
            city=data.city,
            country=data.country,
            bio=data.bio,
            avatar=_avatar(data.name),
            status="onboarding",
        )
        return self._creators.create(creator)

    def update_creator(self, creator_id: str, data: CreatorUpdate) -> Creator:
        creator = self._creators.get(creator_id)
        if not creator:
            raise AccountNotFound(creator_id)
        patch = data.model_dump(exclude_none=True)
        updated = creator.model_copy(update=patch)
        return self._creators.save(updated)

    # -- Brands -------------------------------------------------------------
    def create_brand(self, data: BrandCreate) -> Brand:
        if self._brands.get_by_email(data.email):
            raise DuplicateAccount("A brand with this email already exists.")
        if self._brands.get_by_phone(data.phone):
            raise DuplicateAccount("A brand with this phone already exists.")

        brand = Brand(
            id=str(uuid.uuid4()),
            name=data.name,
            email=data.email,
            phone=data.phone,
            category=data.category,
            website=data.website,
            status="active",
        )
        return self._brands.create(brand)

    def get_brand(self, brand_id: str) -> Brand:
        brand = self._brands.get(brand_id)
        if not brand:
            raise AccountNotFound(brand_id)
        return brand

    def update_brand(self, brand_id: str, data: BrandUpdate) -> Brand:
        brand = self.get_brand(brand_id)
        patch = data.model_dump(exclude_none=True)
        updated = brand.model_copy(update=patch)
        return self._brands.save(updated)
