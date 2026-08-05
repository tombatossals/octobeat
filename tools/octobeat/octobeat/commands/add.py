from __future__ import annotations

import argparse
import traceback

from octobeat.config import (
    ensure_workspace,
)
from octobeat.io.resource import CATALOG_FILE
from octobeat.pipeline import (
    BuildResult,
    build_dataset,
)
from octobeat.ui import console


def run(args: argparse.Namespace) -> int:
    """
    Build a complete dataset from a source.
    """

    config = ensure_workspace()

    output = (
        args.output.expanduser().resolve()
        if args.output is not None
        else config.datasets_dir()
    )

    catalog = (
        args.catalog.expanduser().resolve()
        if args.catalog is not None
        else output / CATALOG_FILE
    )

    try:
        result = build_dataset(
            args.input,
            output=output,
            catalog=catalog,
            dataset_id=args.id,
            include_video=(
                not args.no_video
            ),
            include_cover=(
                not args.no_cover
            ),
            update_catalog=(
                config.catalog.auto_rebuild
            ),
        )
    except Exception:
        traceback.print_exc()
        return 1

    _report(result)

    return 0


def _report(result: BuildResult) -> None:
    console.title("octobeat")

    console.section("Dataset")
    console.field(
        "Artist",
        result.artist or "-",
    )
    console.field(
        "Title",
        result.title or "-",
    )

    console.blank()
    console.section("Resources")
    console.field(
        "Audio",
        result.audio,
    )

    if result.video is not None:
        console.field(
            "Video",
            result.video,
        )

    if result.cover_source is not None:
        console.field(
            "Cover",
            result.cover_source,
        )

    console.blank()
    console.section("Analysis")
    console.field(
        "Duration",
        f"{result.duration:.1f} s",
    )
    console.field(
        "Tempo",
        f"{result.bpm:.0f} BPM",
    )
    console.field(
        "Beats",
        result.beats,
    )
    console.field(
        "Confidence",
        f"{result.confidence:.2f}",
    )

    console.blank()
    console.section("Output")
    console.field(
        "Dataset",
        result.dataset_dir,
    )
    console.field(
        "SongMap",
        result.songmap_path,
    )
    console.field(
        "Metadata",
        result.metadata_path,
    )
    console.field(
        "Catalog",
        result.catalog_path,
    )
    console.field(
        "Catalog entries",
        result.catalog_entries,
    )

    console.blank()
    console.success(
        "Dataset built.",
    )
