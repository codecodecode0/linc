from __future__ import annotations

from typing import List

from pydantic import Field

from .base import CamelModel
from .connection import Platform


class Creator(CamelModel):
    id: str
    name: str
    handle: str
    niche: str
    location: str
    followers: str  # display string, e.g. "480K"
    engagement: str  # display string, e.g. "4.8%"
    match_score: int
    avatar: str
    certified: bool
    rate: int  # starting rate per video, in rupees
    # Which platforms this creator has linked — derived at read time.
    connected_platforms: List[Platform] = Field(default_factory=list)
