from __future__ import annotations

import sys
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

    def prompt(
        self,
        message: str,
        *,
        default: str | None = None,
        allow_empty: bool = False,
    ) -> str:
        """
        Ask the user for a single line of input.

        Returns the entered value, or the default when the input is
        empty and a default is provided.
        """

        suffix = (
            f" [{default}]"
            if default is not None
            else ""
        )

        while True:
            value = input(
                f"{message}{suffix}: ",
            ).strip()

            if value:
                return value

            if default is not None:
                return default

            if allow_empty:
                return ""

            print(
                "Please enter a value.",
            )

    def choose(
        self,
        message: str,
        options: list[str],
        *,
        allow_skip: bool = True,
    ) -> int | None:
        """
        Let the user pick one option from a numbered list.

        Returns the selected index, ``None`` when the user skips.
        """

        print()
        print(message)

        for index, option in enumerate(
            options,
            start=1,
        ):
            print(f"  {index}. {option}")

        prompt_text = (
            f"Select [1-{len(options)}"
            f"{', 0 = skip' if allow_skip else ''}]"
        )

        while True:
            value = input(
                f"{prompt_text}: ",
            ).strip()

            if not value and allow_skip:
                return None

            if value == "0" and allow_skip:
                return None

            try:
                choice = int(value)
            except ValueError:
                print(
                    "Please enter a number.",
                )
                continue

            if 1 <= choice <= len(options):
                return choice - 1

            print(
                f"Select a number between 1 and {len(options)}.",
            )

    def interactive(self) -> bool:
        """
        Whether the terminal is interactive (stdin is a TTY).
        """

        return (
            sys.stdin is not None
            and sys.stdin.isatty()
        )

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
                        (
                            "Tempo confidence",
                            f"{report.tempo_confidence:.2%}",
                        ),
                        (
                            "Beat confidence",
                            f"{report.beat_confidence:.2%}",
                        ),
                        (
                            "Grid stability",
                            f"{report.grid_stability:.2%}",
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

    def debug_report(
        self,
        report: AnalysisReport,
    ) -> None:
        """
        Render detailed diagnostics for an analysis.
        """

        print()

        self.title("Diagnostics")

        self.section("Tempo candidates")
        print()

        if report.tempo_candidates:
            selected_bpm = min(
                report.tempo_candidates,
                key=lambda item: abs(
                    item[0] - report.bpm
                ),
            )[0]

            for bpm, score in sorted(
                report.tempo_candidates,
                key=lambda item: item[1],
                reverse=True,
            ):
                marker = (
                    "  ← selected"
                    if abs(
                        bpm - selected_bpm
                    )
                    < 0.05
                    else ""
                )

                self.field(
                    f"{bpm:.2f} BPM",
                    f"{score:.2f}{marker}",
                )
        else:
            self.info("(no candidates)")

        print()

        self.section("Phase / grid")
        print()

        self.field(
            "Phase",
            (
                f"{report.phase:.3f} s"
                if report.phase is not None
                else "-"
            ),
        )

        self.field(
            "Beats",
            report.beats,
        )

        self.field(
            "Beat interval",
            (
                f"{report.beat_interval:.4f} s"
                if report.beat_interval is not None
                else "-"
            ),
        )

        self.field(
            "Downbeat shift",
            (
                str(report.downbeat_shift)
                if report.downbeat_shift is not None
                else "-"
            ),
        )

        if report.tempo_map:
            print()

            self.section("Tempo map")
            print()

            for start, bpm in report.tempo_map:
                self.field(
                    f"{start:7.3f} s",
                    f"{bpm:.2f} BPM",
                )

        print()

        self.section("Confidence")
        print()

        self.field(
            "Tempo",
            f"{report.tempo_confidence:.2%}",
        )

        self.field(
            "Beats",
            f"{report.beat_confidence:.2%}",
        )

        self.field(
            "Grid",
            f"{report.grid_stability:.2%}",
        )

        self.field(
            "Overall",
            f"{report.confidence:.2%}",
        )

        print()

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
