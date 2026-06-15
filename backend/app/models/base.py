"""Shared model base.

The frontend speaks camelCase while the Python code stays snake_case.
`CamelModel` bridges the two: fields are defined in snake_case but serialize
to camelCase, and can be populated from either form. Keeping all domain
models free of any ORM details means the same shapes map cleanly onto
SQLAlchemy models when we move to Postgres.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
