from __future__ import annotations

import argparse
import sys

from octobeat.io.songmap import read_songmap
from octobeat.ui import console


def run(args: argparse.Namespace) -> int:
    """
    Display information about a SongMap.
    """

    try:
        songmap = read_songmap(args.input)
    except Exception as exc:
        print(f"octobeat: {exc}", file=sys.stderr)
        return 1

    console.title("SongMap")

    console.section("Format")
    console.field("Schema", songmap.schema_)
    console.field("Version", songmap.version)
    console.blank()

    console.section("Recording")
    console.field("Title", songmap.metadata.title)
    console.field("Duration", f"{songmap.metadata.duration:.3f} s")
    console.field(
        "Source",
        f"{songmap.metadata.source.type}:{songmap.metadata.source.id}",
    )
    console.blank()

    console.section("Timing")
    console.field("Tempo", f"{songmap.timing.bpm:.2f} BPM")
    console.field("Offset", f"{songmap.timing.offset:.3f} s")
    console.field("Time Signature", songmap.timing.timeSignature)
    console.field("Confidence", f"{songmap.timing.confidence:.2f}")
    console.blank()

    console.section("Structure")
    console.field("Beats", len(songmap.beats))
    console.field("Bars", len(songmap.bars))
    console.blank()

    console.section("Generated")
    console.field("Tool", songmap.generatedBy)
    console.field("Created", songmap.createdAt)

    return 0