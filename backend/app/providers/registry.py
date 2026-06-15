"""Maps a Platform to its provider. The one lookup the rest of the app uses."""

from __future__ import annotations

from typing import Dict, List

from ..models import Platform
from .base import SocialProvider, UnknownPlatform


class ProviderRegistry:
    def __init__(self, providers: List[SocialProvider]) -> None:
        self._by_platform: Dict[Platform, SocialProvider] = {
            p.platform: p for p in providers
        }

    def get(self, platform: Platform) -> SocialProvider:
        provider = self._by_platform.get(platform)
        if provider is None:
            raise UnknownPlatform(str(platform))
        return provider

    def platforms(self) -> List[Platform]:
        return list(self._by_platform.keys())

    def modes(self) -> Dict[str, str]:
        return {
            p.value: ("mock" if prov.is_mock else "live")
            for p, prov in self._by_platform.items()
        }
