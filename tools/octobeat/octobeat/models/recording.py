from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path

from octobeat.models.songmap import Source


@dataclass
class Recording:
    """
    Represents an audio recording ready for analysis.
    """

    path: Path

    artist: str | None = None
    title: str | None = None

    source: Source | None = None

    cleanup_dir: tempfile.TemporaryDirectory[str] | None = None

    chart_path: Path | None = None

    # Optional musical metadata carried by the source (e.g. an SNG
    # container). Used to enrich dataset metadata without a network
    # provider.
    album: str | None = None
    year: int | None = None
    genres: list[str] | None = None

    # Raw cover artwork bytes extracted from the source, if any.
    cover_bytes: bytes | None = None

    def cleanup(self) -> None:
        if self.cleanup_dir is not None:
            self.cleanup_dir.cleanup()