"""A generic in-memory CRUD store.

One instance backs each resource (campaigns, deals, content, …). Entities must
expose an `id` attribute. When we move to Postgres, each resource gets a
SQLAlchemy-backed repository with the same surface; callers don't change.
"""

from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class InMemoryCrudRepository(Generic[T]):
    def __init__(self) -> None:
        self._items: Dict[str, T] = {}

    def create(self, item: T) -> T:
        self._items[item.id] = item  # type: ignore[attr-defined]
        return item

    def get(self, item_id: str) -> Optional[T]:
        return self._items.get(item_id)

    def list(self, **filters: Any) -> List[T]:
        return [
            item
            for item in self._items.values()
            if all(getattr(item, key, None) == value for key, value in filters.items())
        ]

    def update(self, item: T) -> T:
        self._items[item.id] = item  # type: ignore[attr-defined]
        return item

    def delete(self, item_id: str) -> bool:
        return self._items.pop(item_id, None) is not None
