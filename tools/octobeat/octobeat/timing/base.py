from __future__ import annotations

from abc import ABC, abstractmethod

from octobeat.models.timing import TimingData


class TimingError(Exception):
    """
    Base class for timing-source failures.

    Raised when a structured chart cannot be used. The CLI catches
    these to fall back to audio analysis.
    """


class UnsupportedVersionError(TimingError):
    """The container/chart version is not supported."""


class CorruptFileError(TimingError):
    """The file is corrupt, truncated or not a valid chart."""


class MissingChartError(TimingError):
    """The container does not carry a usable chart file."""


class TimingProvider(ABC):
    """
    Base class for timing providers.

    A TimingProvider parses a structured timing source (SNG, MIDI,
    CHART, Audio) and produces canonical ``TimingData``.

    Providers perform parsing only.
    They never generate a SongMap — that is ``SongMapBuilder``'s job.
    """

    @classmethod
    @abstractmethod
    def supports(cls, source: str) -> bool:
        """
        Return True if this provider can handle the given source.
        """
        raise NotImplementedError

    @abstractmethod
    def load(self, source: str) -> TimingData:
        """
        Parse the source and return canonical ``TimingData``.
        """
        raise NotImplementedError
