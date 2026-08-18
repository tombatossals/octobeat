from __future__ import annotations

import argparse
from pathlib import Path

from octobeat.io import write_dataset
from octobeat.io.songmap import read_songmap
from octobeat.naming import export_stem
from octobeat.pipeline.builder import analyse_sng
from octobeat.ui import console


def run(args: argparse.Namespace) -> int:
    """
    Export a SongMap dataset.

    ``args.songmap`` may be a SongMap JSON document or an SNG container
    (in which case the SongMap is generated from the embedded chart).
    """

    songmap_path = Path(args.songmap)

    if songmap_path.suffix.lower() == ".sng":
        result = analyse_sng(
            songmap_path,
        )

        songmap = result.songmap
    else:
        songmap = read_songmap(
            songmap_path,
        )

    destination = write_dataset(
        songmap,
        Path(args.destination),
        metronome=args.metronome,
        no_drums=args.no_drums,
        click_volume=args.click_volume,
        audio_path=(
            Path(args.audio)
            if args.audio is not None
            else None
        ),
    )

    exported = destination / f"{export_stem(songmap)}.mp3"

    features = []

    if args.no_drums:
        features.append("no drums")

    if args.metronome:
        features.append("metronome")

    suffix = (
        f" ({', '.join(features)})"
        if features
        else ""
    )

    console.success(
        f"Exported {exported.name} to {destination}{suffix}"
    )

    return 0