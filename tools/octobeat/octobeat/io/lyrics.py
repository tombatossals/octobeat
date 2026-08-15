from __future__ import annotations

import json
from pathlib import Path

from octobeat.models.timing import LyricLine

LYRICS_FILE = "lyrics.json"


def lyrics_to_json(lyrics: list[LyricLine]) -> str:
    """
    Serialize synced lyrics into a formatted JSON document.

    The document is a top-level array of lyric lines. Fields follow the
    SongMap camelCase convention (``startTime``, ``endTime``).
    """

    return (
        json.dumps(
            [_line_to_dict(line) for line in lyrics],
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )


def _line_to_dict(line: LyricLine) -> dict[str, object]:
    result: dict[str, object] = {
        "index": line.index,
        "text": line.text,
        "startTime": line.start_time,
    }

    if line.end_time is not None:
        result["endTime"] = line.end_time

    if line.syllables:
        result["syllables"] = [
            {
                "text": syllable.text,
                "startTime": syllable.start_time,
            }
            for syllable in line.syllables
        ]

    return result


def write_lyrics(
    lyrics: list[LyricLine],
    destination: Path,
) -> None:
    """
    Write synced lyrics as ``lyrics.json`` inside a dataset.
    """

    destination = (
        destination.expanduser().resolve()
    )
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination.write_text(
        lyrics_to_json(lyrics),
        encoding="utf-8",
    )
