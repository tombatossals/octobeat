from __future__ import annotations

import argparse
import traceback
from pathlib import Path

from octobeat.core.analyser import analyse_recording, analyse_with_chart
from octobeat.io.songmap import write_songmap
from octobeat.models.analysis import AnalysisResult
from octobeat.models.recording import Recording
from octobeat.naming import resolve_output_path
from octobeat.providers.factory import get_provider
from octobeat.timing import (
    TimingError,
    get_timing_provider,
    supports_timing_source,
)
from octobeat.ui import console


def run(args: argparse.Namespace) -> int:
    """
    Analyse an audio source and generate a SongMap.
    """

    provider = get_provider(args.input)

    recording = provider.load(args.input)

    try:
        if args.chart is not None:
            result = _analyse_with_chart(recording, args)
        else:
            result = analyse_recording(
                recording,
                provider=type(provider).__name__,
                source=args.input,
                offset=args.offset,
            )

        output = resolve_output_path(
            recording=recording,
            output=args.output,
        )

        write_songmap(
            result.songmap,
            output,
        )

        result.report.output = output

        console.report(result.report)

        if args.debug:
            console.debug_report(result.report)

        return 0

    except Exception:
        traceback.print_exc()

        return 1

    finally:
        recording.cleanup()


def _analyse_with_chart(
    recording: Recording,
    args: argparse.Namespace,
) -> AnalysisResult:
    """
    Analyse using a structured chart for timing and the audio for
    validation. Falls back to audio-only when the chart is unusable.
    """

    chart_path = args.chart

    if not supports_timing_source(str(chart_path)):
        console.warning(
            f"Chart '{chart_path}' is not a supported timing source; "
            "falling back to audio analysis.",
        )
        return analyse_recording(
            recording,
            provider="local",
            source=args.input,
            offset=args.offset,
        )

    provider = get_timing_provider(str(chart_path))

    try:
        chart_timing = provider.load(str(chart_path))
    except (TimingError, FileNotFoundError) as error:
        console.warning(
            f"Chart could not be parsed ({error}); "
            "falling back to audio analysis.",
        )
        return analyse_recording(
            recording,
            provider="local",
            source=args.input,
            offset=args.offset,
        )

    console.info(
        f"Using chart {chart_path} as timing source.",
    )

    return analyse_with_chart(
        recording,
        chart_timing,
        provider="chart",
        source=str(chart_path),
        chart_source=_chart_source_kind(chart_path),
    )


def _chart_source_kind(chart_path: Path) -> str:
    suffix = str(chart_path).lower()

    if suffix.endswith(".mid"):
        return "midi"

    if suffix.endswith(".chart"):
        return "chart"

    return "sng"