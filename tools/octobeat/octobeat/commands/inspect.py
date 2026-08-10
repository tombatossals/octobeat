from __future__ import annotations

import argparse

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
    Inspect a structured timing source (SNG/MIDI/CHART) without building
    a dataset.
    """

    source = args.input

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
