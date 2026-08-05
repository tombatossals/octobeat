from __future__ import annotations

from pathlib import Path

from octobeat.io import write_dataset
from octobeat.io.songmap import read_songmap
from octobeat.ui import console


def run(args) -> int:
    """
    Export a SongMap dataset.
    """

    songmap = read_songmap(
        Path(args.songmap),
    )

    destination = write_dataset(
        songmap,
        Path(args.destination),
    )

    console.success(
        f"Dataset exported to {destination}"
    )

    return 0