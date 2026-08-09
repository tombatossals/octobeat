from __future__ import annotations

import argparse
from typing import Any

from octobeat.config import ensure_workspace
from octobeat.pipeline.reanalyse import reanalyse_datasets
from octobeat.ui import console


def run(args: argparse.Namespace) -> int:
    """
    Manage datasets.
    """

    if args.dataset_command == "reanalyse":
        return _reanalyse(args)

    console.failure(
        f"dataset {args.dataset_command} is not implemented.",
    )

    return 1


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
