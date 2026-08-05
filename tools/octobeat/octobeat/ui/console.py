from __future__ import annotations

from typing import Any

from rich import box
from rich.console import Console as RichConsole
from rich.table import Table

from octobeat.models.analysis import (
    AnalysisReport,
)

_rich = RichConsole()


class Console:
    """
    Terminal output helper.

    All user-facing output should go through this class so the
    implementation can evolve independently (Rich, Textual, JSON, ...).
    """

    def title(self, text: str) -> None:
        print(text)
        print("=" * len(text))
        print()

    def section(self, text: str) -> None:
        print(text)
        print("-" * len(text))

    def field(self, name: str, value: Any) -> None:
        print(f"{name:.<20} {value}")

    def blank(self) -> None:
        print()

    def info(self, message: str) -> None:
        print(message)

    def error(self, message: str) -> None:
        print(f"ERROR: {message}")

    def success(self, message: str) -> None:
        print(f"✓ {message}")

    def failure(self, message: str) -> None:
        print(f"✗ {message}")

    def warning(self, message: str) -> None:
        print(f"⚠ {message}")

    def report(
        self,
        report: AnalysisReport,
    ) -> None:
        """
        Render an analysis report as a table.
        """

        self.table_report(
            [
                (
                    "Input",
                    [
                        ("Provider", report.provider),
                        ("Source", report.source),
                    ],
                ),
                (
                    "Audio",
                    [
                        ("Recording", report.recording),
                        ("Decoded PCM", report.decoded),
                    ],
                ),
                (
                    "Analysis",
                    [
                        ("Duration", f"{report.duration:.2f}s"),
                        ("BPM", f"{report.bpm:.2f}"),
                        ("Beats", report.beats),
                        (
                            "Confidence",
                            f"{report.confidence:.2%}",
                        ),
                    ],
                ),
                (
                    "Output",
                    [
                        ("SongMap", report.output),
                    ],
                ),
            ],
        )

        self.success("Analysis completed.")

    def table_report(
        self,
        groups: list[
            tuple[
                str,
                list[tuple[str, Any]],
            ]
        ],
        title: str = "octobeat",
    ) -> None:
        """
        Render grouped key/value data as a single table.
        """

        self.title(title)

        table = Table(
            show_header=False,
            box=box.HEAVY,
            padding=(0, 2),
        )
        table.add_column(
            "Key",
            style="bold",
            no_wrap=True,
        )
        table.add_column(
            "Value",
            overflow="fold",
        )

        for index, (label, rows) in enumerate(
            groups
        ):
            if index:
                table.add_section()

            table.add_row(
                label,
                "",
                style="bold cyan",
            )

            for key, value in rows:
                table.add_row(
                    key,
                    _as_text(value),
                )

        _rich.print(table)
        print()


def _as_text(value: Any) -> str:
    if value is None:
        return "-"

    return str(value)
