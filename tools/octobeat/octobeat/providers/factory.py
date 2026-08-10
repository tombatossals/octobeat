from __future__ import annotations

from octobeat.providers.base import SourceProvider
from octobeat.providers.local import LocalFileProvider
from octobeat.providers.sng import SngSourceProvider
from octobeat.providers.youtube import YouTubeProvider

_PROVIDERS: list[type[SourceProvider]] = [
    SngSourceProvider,
    LocalFileProvider,
    YouTubeProvider,
]


def get_provider(source: str) -> SourceProvider:
    """
    Return the first provider that supports the given source.
    """

    for provider_cls in _PROVIDERS:
        if provider_cls.supports(source):
            return provider_cls()

    raise ValueError(f"No provider found for '{source}'.")