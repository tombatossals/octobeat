from __future__ import annotations

from abc import ABC, abstractmethod

from octobeat.models.recording import Recording


class SourceProvider(ABC):
    """
    Base class for recording source providers.

    A SourceProvider is responsible for acquiring a recording from a
    particular source (local filesystem, YouTube, Spotify, etc.) and
    returning it as a Recording.

    Providers perform acquisition only.
    They never perform musical analysis.
    """

    @classmethod
    @abstractmethod
    def supports(cls, source: str) -> bool:
        """
        Return True if this provider can handle the given source.
        """
        raise NotImplementedError

    @abstractmethod
    def load(self, source: str) -> Recording:
        """
        Acquire the recording and return it.

        Implementations may download remote media, create temporary files
        or perform any other acquisition steps required by the provider.
        """
        raise NotImplementedError