from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedMetadata:
    """
    Canonical metadata extracted from a recording title.
    """

    artist: str | None
    title: str


_NOISE_PATTERNS = (
    r"\(official video\)",
    r"\[official video\]",
    r"\(official music video\)",
    r"\[official music video\]",
    r"\(lyrics?\)",
    r"\[lyrics?\]",
    r"\(audio\)",
    r"\[audio\]",
    r"\(hd\)",
    r"\(4k\)",
)

_FEATURED_PATTERN = re.compile(
    r"\s+(feat\.?|ft\.?|featuring)\s+.*$",
    flags=re.IGNORECASE,
)


def parse_recording_title(raw_title: str) -> ParsedMetadata:
    """
    Parse a recording title into canonical artist and title metadata.

    This parser intentionally implements only conservative heuristics.
    """

    title = raw_title.strip()

    title = _remove_noise(title)
    title = _remove_featured_artists(title)

    title = re.sub(r"\s+", " ", title).strip()

    if " - " in title:
        artist, song = title.split(" - ", 1)

        return ParsedMetadata(
            artist=artist.strip(),
            title=song.strip(),
        )

    return ParsedMetadata(
        artist=None,
        title=title,
    )


def _remove_noise(title: str) -> str:
    for pattern in _NOISE_PATTERNS:
        title = re.sub(
            pattern,
            "",
            title,
            flags=re.IGNORECASE,
        )

    return title


def _remove_featured_artists(title: str) -> str:
    return _FEATURED_PATTERN.sub("", title).strip()