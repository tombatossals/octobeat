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

    # Detected count-in and song start (seconds into the audio). The
    # count-in is the audible lead-in before the song really kicks in
    # (e.g. Rock Band stick clicks). Only set when the source has one.
    count_in_start: float | None = None
    song_start: float | None = None

    # Times (seconds into the audio) of the individual count-in clicks,
    # when the source carries a click reference track (e.g. song.opus).
    count_in_clicks: list[float] | None = None

    def cleanup(self) -> None:
        if self.cleanup_dir is not None:
            self.cleanup_dir.cleanup()