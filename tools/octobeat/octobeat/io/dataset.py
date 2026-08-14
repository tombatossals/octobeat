from __future__ import annotations

from pathlib import Path

from octobeat.audio import encode_to_mp3
from octobeat.cache import cache
from octobeat.io.songmap import write_songmap
from octobeat.models.songmap import SongMap

RECORDING_MP3 = "recording.mp3"


def write_dataset(
    songmap: SongMap,
    destination: Path,
) -> Path:
    """
    Write a SongMap dataset to disk.

    The dataset currently contains:

      - recording.songmap.json
      - recording.mp3
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

    # Encode recording
    recording = cache.lookup(songmap.metadata.source)

    if recording is None:
        raise FileNotFoundError(
            f"Recording not found in cache: "
            f"{songmap.metadata.source.type}:{songmap.metadata.source.id}"
        )

    encode_to_mp3(
        recording,
        destination / RECORDING_MP3,
    )

    return destination