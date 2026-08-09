from __future__ import annotations

from dataclasses import dataclass, field
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

    tempo_confidence: float = 0.0

    beat_confidence: float = 0.0

    grid_stability: float = 0.0

    # Debug diagnostics.
    tempo_candidates: list[tuple[float, float]] = field(
        default_factory=list,
    )

    tempo_map: list[tuple[float, float]] = field(
        default_factory=list,
    )

    phase: float | None = None

    beat_interval: float | None = None

    duplicate_beats: int = 0

    output: Path | None = None


@dataclass(slots=True)
class AnalysisResult:
    """
    Result of an analysis: the SongMap plus a display report.
    """

    songmap: SongMap

    report: AnalysisReport
