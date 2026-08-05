from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from octobeat.io.songmap import read_songmap
from octobeat.models.songmap import SongMap


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of validating a SongMap.
    """

    songmap: SongMap

    errors: list[str]

    warnings: list[str]

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0


def validate_songmap(path: Path) -> ValidationResult:
    """
    Validate a SongMap.

    Version 0.1 performs structural validation only by parsing the
    document with the SongMap Pydantic model.

    Semantic validation rules will be added in future versions.
    """

    songmap = read_songmap(path)

    return ValidationResult(
        songmap=songmap,
        errors=[],
        warnings=[],
    )