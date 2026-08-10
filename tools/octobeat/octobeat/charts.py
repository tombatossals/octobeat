"""Community chart lookup.

Searches a charts directory for a structured timing source (SNG/MIDI/
CHART) matching a recording, so the dataset pipeline can prefer a
community chart over audio analysis.
"""

from __future__ import annotations

import unicodedata
from pathlib import Path

from octobeat.config.model import Config
from octobeat.models.recording import Recording

CHART_EXTENSIONS = (
    ".sng",
    ".mid",
    ".chart",
)


def chart_search_dirs(config: Config) -> list[Path]:
    """
    Directories searched for community charts.

    The configured ``paths.charts`` directory when set, plus the repo's
    ``sng/`` directory as a fallback.
    """

    dirs: list[Path] = []

    configured = config.paths.charts_dir()
    if configured is not None:
        dirs.append(configured)

    repo = Path(__file__).resolve().parents[3] / "sng"
    if repo.is_dir() and repo not in dirs:
        dirs.append(repo)

    return dirs


def find_chart(
    recording: Recording,
    *,
    config: Config,
) -> Path | None:
    """
    Search the chart directories for a source matching ``recording``.

    Matching is by artist/title in the file name (``Artist - Title.sng``)
    or by the title alone. Returns the first match, or ``None``.
    """

    if not recording.artist and not recording.title:
        return None

    needles = _search_terms(recording)

    for directory in chart_search_dirs(config):
        if not directory.is_dir():
            continue

        for path in sorted(
            directory.glob("*.sng")
        ):
            if _matches(path, needles):
                return path

        for path in sorted(
            directory.glob("*.mid")
        ):
            if _matches(path, needles):
                return path

        for path in sorted(
            directory.glob("*.chart")
        ):
            if _matches(path, needles):
                return path

    return None


def _search_terms(recording: Recording) -> list[str]:
    terms: list[str] = []

    if recording.title:
        terms.append(_normalise(recording.title))

    if recording.artist:
        terms.append(_normalise(recording.artist))

    return terms


def _matches(path: Path, needles: list[str]) -> bool:
    if not path.is_file():
        return False

    if path.suffix.lower() not in CHART_EXTENSIONS:
        return False

    name = _normalise(path.stem)

    return all(
        needle and needle in name
        for needle in needles
    )


def _normalise(text: str) -> str:
    """Lowercase, strip diacritics and collapse separators."""

    text = unicodedata.normalize(
        "NFKD",
        text,
    )

    text = "".join(
        char
        for char in text
        if not unicodedata.combining(char)
    )

    return (
        text.lower()
        .replace("_", " ")
        .replace("-", " ")
        .replace(".", " ")
        .strip()
    )
