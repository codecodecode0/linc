"""A thin generic CRUD service over `InMemoryCrudRepository`.

Holds the small bits of logic shared by every resource: list with filters,
partial update via `model_copy`, and existence checks. Resource-specific
construction (generating ids, attaching parent ids) happens in the routers,
which know the concrete request/entity shapes.
"""

from __future__ import annotations

from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel

from ..repositories import InMemoryCrudRepository

T = TypeVar("T", bound=BaseModel)


class NotFound(Exception):
    pass


class CrudService(Generic[T]):
    def __init__(self, repo: InMemoryCrudRepository[T]) -> None:
        self._repo = repo

    def create(self, entity: T) -> T:
        return self._repo.create(entity)

    def get(self, entity_id: str) -> T:
        entity = self._repo.get(entity_id)
        if entity is None:
            raise NotFound(entity_id)
        return entity

    def list(self, **filters: Any) -> List[T]:
        return self._repo.list(**filters)

    def update(self, entity_id: str, patch: dict) -> T:
        entity = self.get(entity_id)
        updated = entity.model_copy(update=patch)
        return self._repo.update(updated)

    def delete(self, entity_id: str) -> None:
        if not self._repo.delete(entity_id):
            raise NotFound(entity_id)
