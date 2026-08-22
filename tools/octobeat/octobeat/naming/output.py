from __future__ import annotations

from pathlib import Path

from octobeat.models.recording import Recording
from octobeat.models.songmap import SongMap
from octobeat.naming.slug import recording_slug


def resolve_output_path(
    recording: Recording,
    output: Path | None = None,
    extension: str = ".songmap.json",
) -> Path:
    """
    Resolve the destination path for a SongMap.

    If an explicit output path is provided, it is returned unchanged.
    Otherwise a canonical filename is generated from the recording
    metadata.
    """

    if output is not None:
        return output.expanduser().resolve()

    filename = f"{recording_slug(recording)}.songmap.json"

    return Path.cwd() / filename


def format_bpm(bpm: float) -> str:
    """
    Format a BPM value for use in a filename.

    ``120.0`` → ``"120"``, ``87.5`` → ``"087.5"``.

    The integer part is zero-padded to three digits so a batch of
    exports sorts by song speed under plain alphabetical ordering
    (``"080"`` before ``"120"`` before ``"180"``).
    """

    rounded = round(bpm)

    if abs(bpm - rounded) < 0.05:
        return f"{rounded:03d}"

    integer, fraction = f"{bpm:.1f}".split(".")

    return f"{int(integer):03d}.{fraction}"


def export_stem(songmap: SongMap) -> str:
    """
    Canonical filename stem for an exported song.

    The stem is prefixed with the song BPM and the group name
    (``"120 - Band - Title"``) so a batch of exports placed in the
    same directory sorts by song speed. The group is omitted when the
    SongMap carries no artist.
    """

    parts = [
        format_bpm(songmap.timing.bpm),
    ]

    if songmap.metadata.artist:
        parts.append(
            _safe_token(songmap.metadata.artist),
        )

    parts.append(
        _safe_token(songmap.metadata.title),
    )

    return " - ".join(parts)


def _safe_token(value: str) -> str:
    """Make an artist/title safe for a filename, preserving its case."""

    safe = value.replace("/", "-").replace("\\", "-").replace(":", "-")

    return safe.strip(" .")