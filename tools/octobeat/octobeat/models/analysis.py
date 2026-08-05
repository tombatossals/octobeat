from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from octobeat.models.songmap import SongMap


@dataclass(slots=True)
class AnalysisReport:
    """
    Human-readable summary of an analysis.
    """

    provider: str

    source: str

    recording: Path

    decoded: Path

    duration: float

    bpm: float

    beats: int

    confidence: float

    output: Path | None = None


@dataclass(slots=True)
class AnalysisResult:
    """
    Result of an analysis: the SongMap plus a display report.
    """

    songmap: SongMap

    report: AnalysisReport
