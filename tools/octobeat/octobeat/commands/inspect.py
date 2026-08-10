from __future__ import annotations

import argparse
from pathlib import Path

from octobeat.io.songmap import read_songmap
from octobeat.models.songmap import VideoMedia
from octobeat.timing import (
    TimingData,
    TimingError,
    TimingProvider,
    get_timing_provider,
    supports_timing_source,
)
from octobeat.ui import console


def run(args: argparse.Namespace) -> int:
    """
    Inspect a structured timing source (SNG/MIDI/CHART) or a dataset
    (SongMap) without building a dataset.
    """

    source = args.input
    path = Path(source)

    if path.suffix.lower() == ".json":
        return _inspect_songmap(path)

    if not supports_timing_source(source):
        console.error(
            f"No timing provider for '{source}'.",
        )
        return 1

    provider = get_timing_provider(source)

    try:
        timing = provider.load(source)
    except (TimingError, FileNotFoundError) as error:
        console.error(str(error))
        return 1

    _report(provider, timing)

    return 0


def _inspect_songmap(path: Path) -> int:
    """Inspect a SongMap document (dataset)."""

    try:
        songmap = read_songmap(path)
    except Exception as error:
        console.error(str(error))
        return 1

    console.title("SongMap")
    console.section("Timing")
    console.field(
        "Source",
        songmap.timing.source or "unknown",
    )
    console.field(
        "BPM",
        f"{songmap.timing.bpm:.1f}",
    )
    console.field(
        "Beats",
        len(songmap.beats),
    )
    console.field(
        "Sections",
        len(songmap.sections or []),
    )

    _report_video(songmap.media.video if songmap.media else None)

    return 0


def _report_video(video: VideoMedia | None) -> None:
    """Print the video synchronization section, if present."""

    console.blank()
    console.section("Video")

    if video is None:
        console.info("(none)")
        return

    console.field("File", video.file)
    console.field("Offset", f"{video.offset:.2f} s")
    console.field("Confidence", f"{video.syncConfidence:.2f}")

    if video.syncConfidence >= 0.90:
        console.success("Audio/video synchronized.")
    elif video.syncConfidence >= 0.70:
        console.warning("Synchronization needs review.")
    else:
        console.warning("Synchronization unreliable.")


def _report(
    provider: TimingProvider,
    timing: TimingData,
) -> None:
    console.title(_format_name(provider))
    console.section("Timing")

    console.field(
        "BPM segments",
        len(timing.tempos),
    )
    console.field(
        "Time signatures",
        len(timing.time_signatures),
    )
    console.field(
        "Beats",
        len(timing.beats),
    )
    console.field(
        "Offset",
        f"{timing.offset:.3f} s",
    )

    if timing.tempos:
        bpm = ", ".join(
            f"{segment.bpm:.1f}"
            for segment in timing.tempos
        )
        console.field("BPM", bpm)

    console.blank()
    console.section("Sections")

    if not timing.sections:
        console.info("(none)")
    else:
        for section in timing.sections:
            console.info(section.name)


def _format_name(provider: TimingProvider) -> str:
    """Format name for the report title."""

    return type(provider).__name__.replace("Provider", "").upper()
