from __future__ import annotations

from typing import Any

from octobeat.models.analysis import (
    AnalysisReport,
)

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

    def warning(self, message: str) -> None:
        print(f"WARNING: {message}")

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
        self.title("octobeat")

        self.section("Input")
        self.field("Provider", report.provider)
        self.field("Source", report.source)

        self.blank()

        self.section("Audio")
        self.field("Recording", report.recording)
        self.field("Decoded PCM", report.decoded)

        self.blank()

        self.section("Analysis")
        self.field("Duration", f"{report.duration:.2f}s")
        self.field("BPM", f"{report.bpm:.2f}")
        self.field("Beats", report.beats)
        self.field(
            "Confidence",
            f"{report.confidence:.2%}",
        )

        self.blank()

        self.section("Output")
        self.field(
            "SongMap",
            report.output,
        )

        self.blank()

        self.success("Analysis completed.")