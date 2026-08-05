from __future__ import annotations

import argparse
import traceback

from octobeat.config import (
    ensure_workspace,
)
from octobeat.io.resource import CATALOG_FILE
from octobeat.pipeline import build_dataset
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

    resources: list[tuple[str, object]] = [
        ("Audio", result.audio),
    ]

    if result.video is not None:
        resources.append(
            ("Video", result.video),
        )

    if result.cover_source is not None:
        resources.append(
            ("Cover", result.cover_source),
        )

    console.table_report(
        [
            (
                "Dataset",
                [
                    ("Artist", result.artist or "-"),
                    ("Title", result.title or "-"),
                ],
            ),
            (
                "Resources",
                resources,
            ),
            (
                "Analysis",
                [
                    ("Duration", f"{result.duration:.1f} s"),
                    ("Tempo", f"{result.bpm:.0f} BPM"),
                    ("Beats", result.beats),
                    (
                        "Confidence",
                        f"{result.confidence:.2f}",
                    ),
                ],
            ),
            (
                "Output",
                [
                    ("Dataset", result.dataset_dir),
                    ("SongMap", result.songmap_path),
                    ("Metadata", result.metadata_path),
                    ("Catalog", result.catalog_path),
                    (
                        "Catalog entries",
                        result.catalog_entries,
                    ),
                ],
            ),
        ],
    )

    console.success(
        "Dataset built.",
    )

    return 0
