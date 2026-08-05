from __future__ import annotations

import argparse

from octobeat.ui import console
from octobeat.validation import validate_songmap


def run(args: argparse.Namespace) -> int:
    """
    Validate a SongMap document.
    """

    try:
        result = validate_songmap(args.input)
    except Exception as exc:
        console.error(str(exc))
        return 1

    if not result.valid:
        console.error("SongMap validation failed.")
        console.blank()

        if result.errors:
            console.section("Errors")
            for error in result.errors:
                console.error(error)
            console.blank()

        if result.warnings:
            console.section("Warnings")
            for warning in result.warnings:
                console.warning(warning)

        return 1

    console.success("SongMap is valid.")

    if result.warnings:
        console.blank()
        console.section("Warnings")
        for warning in result.warnings:
            console.warning(warning)

    return 0