from __future__ import annotations

from octobeat.timing.base import (
    CorruptFileError,
    MissingChartError,
    TimingError,
    TimingProvider,
    UnsupportedVersionError,
)
from octobeat.timing.sng import SNGProvider

_PROVIDERS: list[type[TimingProvider]] = [
    SNGProvider,
]


def get_timing_provider(source: str) -> TimingProvider:
    """
    Return the first timing provider that supports the given source.
    """

    for provider_cls in _PROVIDERS:
        if provider_cls.supports(source):
            return provider_cls()

    raise ValueError(f"No timing provider found for '{source}'.")


def supports_timing_source(source: str) -> bool:
    """True when any registered provider can handle the source."""

    return any(
        provider_cls.supports(source)
        for provider_cls in _PROVIDERS
    )


__all__ = [
    "CorruptFileError",
    "MissingChartError",
    "SNGProvider",
    "TimingError",
    "TimingProvider",
    "UnsupportedVersionError",
    "get_timing_provider",
    "supports_timing_source",
]
