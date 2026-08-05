from __future__ import annotations

from pathlib import Path

from octobeat.models.recording import Recording
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