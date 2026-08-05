from __future__ import annotations

import shutil
from pathlib import Path

from octobeat.cache import cache
from octobeat.io.songmap import write_songmap
from octobeat.models.songmap import SongMap


def write_dataset(
    songmap: SongMap,
    destination: Path,
) -> Path:
    """
    Write a SongMap dataset to disk.

    The dataset currently contains:

      - recording.songmap.json
      - recording.wav
    """

    destination = destination.expanduser().resolve()

    destination.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Write SongMap
    write_songmap(
        songmap,
        destination / "recording.songmap.json",
    )

    # Copy recording
    recording = cache.lookup(songmap.metadata.source)

    if recording is None:
        raise FileNotFoundError(
            f"Recording not found in cache: "
            f"{songmap.metadata.source.type}:{songmap.metadata.source.id}"
        )

    shutil.copy2(
        recording,
        destination / "recording.wav",
    )

    return destination