from __future__ import annotations

import argparse
from typing import Any

from octobeat.config import ensure_workspace
from octobeat.models.metadata import CatalogMetadata
from octobeat.pipeline.datasets import list_datasets
from octobeat.pipeline.reanalyse import reanalyse_datasets
from octobeat.ui import console


def run(args: argparse.Namespace) -> int:
    """
    Manage datasets.
    """

    if args.dataset_command == "reanalyse":
        return _reanalyse(args)

    if args.dataset_command == "list":
        return _list(args)

    console.failure(
        f"dataset {args.dataset_command} is not implemented.",
    )

    return 1


def _list(args: argparse.Namespace) -> int:
    """
    List every dataset in the workspace.
    """

    config = ensure_workspace()

    output = (
        args.output.expanduser().resolve()
        if args.output is not None
        else config.datasets_dir()
    )

    entries = list_datasets(output)

    if args.incomplete:
        entries = [
            entry
            for entry in entries
            if entry.incomplete()
        ]

    if not entries:
        if args.incomplete:
            console.warning(
                "No incomplete datasets found.",
            )
        else:
            console.warning(
                f"No datasets found in {output}.",
            )

        return 0

    rows: list[
        tuple[str, list[tuple[str, Any]]]
    ] = [
        (
            (
                f"Incomplete datasets ({len(entries)})"
                if args.incomplete
                else f"Datasets ({len(entries)})"
            ),
            [
                (
                    entry.dataset_id,
                    (
                        _describe(entry.metadata)
                        if entry.metadata is not None
                        else "(no metadata)"
                    ),
                )
                for entry in entries
            ],
        ),
    ]

    console.table_report(
        rows,
        title="octobeat dataset list",
    )

    if args.incomplete:
        console.blank()
        console.section("Missing")

        for entry in entries:
            console.field(
                entry.dataset_id,
                ", ".join(entry.missing()),
            )

    return 0


def _describe(
    metadata: CatalogMetadata,
) -> str:
    parts = [
        metadata.artist or "?",
        metadata.title or "?",
    ]

    if metadata.album:
        parts.append(
            f"({metadata.album})",
        )

    if metadata.year:
        parts.append(
            f"[{metadata.year}]",
        )

    return " - ".join(parts)


def _reanalyse(args: argparse.Namespace) -> int:
    """
    Re-analyse every dataset in the workspace.
    """

    config = ensure_workspace()

    output = (
        args.output.expanduser().resolve()
        if args.output is not None
        else config.datasets_dir()
    )

    summary = reanalyse_datasets(
        output,
        offset=args.offset,
    )

    rows: list[
        tuple[str, list[tuple[str, Any]]]
    ] = [
        (
            "Re-analysis",
            [
                (
                    "Reanalysed",
                    len(summary.reanalysed),
                ),
                (
                    "Failed",
                    len(summary.failed),
                ),
            ],
        ),
    ]

    if summary.reanalysed:
        rows.insert(
            0,
            (
                "Datasets",
                [
                    (
                        str(result.dataset_id),
                        (
                            f"{result.bpm:.2f} BPM · "
                            f"{result.beats} beats · "
                            f"{result.confidence:.0%}"
                            + (
                                ""
                                if result.changed
                                else " (unchanged)"
                            )
                        ),
                    )
                    for result in summary.reanalysed
                ],
            ),
        )

    console.table_report(
        rows,
        title="octobeat dataset reanalyse",
    )

    if summary.failed:
        console.blank()
        console.section("Failures")

        for dataset_id, error in summary.failed:
            console.field(
                dataset_id,
                error,
            )

        console.blank()
        console.failure(
            f"{len(summary.failed)} dataset(s) failed.",
        )

        return 1

    console.success(
        "Re-analysis completed.",
    )

    return 0
