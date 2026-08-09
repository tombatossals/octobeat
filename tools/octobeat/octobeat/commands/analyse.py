from __future__ import annotations

import argparse
import traceback

from octobeat.core.analyser import analyse_recording
from octobeat.io.songmap import write_songmap
from octobeat.naming import resolve_output_path
from octobeat.providers.factory import get_provider
from octobeat.ui import console


def run(args: argparse.Namespace) -> int:
    """
    Analyse an audio source and generate a SongMap.
    """

    provider = get_provider(args.input)

    recording = provider.load(args.input)

    try:
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