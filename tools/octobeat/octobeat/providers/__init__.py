"""Recording source providers."""

from .base import SourceProvider
from .local import LocalFileProvider
from .youtube import YouTubeProvider

__all__ = [
    "SourceProvider",
    "LocalFileProvider",
    "YouTubeProvider",
]