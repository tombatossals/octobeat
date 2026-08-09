"""Test fixtures for BeatEngine.

Synthetic audio recordings that exercise difficult analysis cases,
together with their expected ground truth (BPM, offset, tempo changes).
The fixtures are generated deterministically so the pipeline can be
regression-tested without shipping binary audio.
"""

from __future__ import annotations

import json
import wave
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

SR = 22050
DURATION = 12.0
CLICK_SECONDS = 0.03

# Case identifiers matching the plan's fixture layout.
CASE_NAMES = [
    "constant-tempo",
    "half-time",
    "double-time",
    "tempo-change",
    "syncopated",
    "intro",
    "silence",
]


@dataclass(frozen=True, slots=True)
class Fixture:
    name: str

    bpm: float | None

    offset: float

    tempo_changes: list[dict[str, float]]

    notes: str


def build_fixtures(
    output: Path,
    *,
    sr: int = SR,
) -> list[Fixture]:
    """Generate all fixture recordings and a manifest into ``output``."""

    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    fixtures = [
        _constant_tempo(),
        _half_time(),
        _double_time(),
        _tempo_change(),
        _syncopated(),
        _intro(),
        _silence(),
    ]

    manifest = []

    for fixture in fixtures:
        signal = _render(
            fixture,
            sr=sr,
        )

        path = output / f"{fixture.name}.wav"

        _write_wav(
            path,
            signal,
            sr,
        )

        manifest.append(
            asdict(fixture),
        )

    (output / "manifest.json").write_text(
        json.dumps(
            manifest,
            indent=2,
        ),
        encoding="utf-8",
    )

    return fixtures


def _constant_tempo() -> Fixture:
    return Fixture(
        name="constant-tempo",
        bpm=120.0,
        offset=0.0,
        tempo_changes=[
            {"time": 0.0, "bpm": 120.0},
        ],
        notes="Simple click track at 120 BPM.",
    )


def _half_time() -> Fixture:
    return Fixture(
        name="half-time",
        bpm=80.0,
        offset=0.0,
        tempo_changes=[
            {"time": 0.0, "bpm": 80.0},
        ],
        notes="Clicks on every beat; a naive tracker may report 40 BPM.",
    )


def _double_time() -> Fixture:
    return Fixture(
        name="double-time",
        bpm=160.0,
        offset=0.0,
        tempo_changes=[
            {"time": 0.0, "bpm": 160.0},
        ],
        notes="Clicks on every beat; a naive tracker may report 320 BPM.",
    )


def _tempo_change() -> Fixture:
    return Fixture(
        name="tempo-change",
        bpm=None,
        offset=0.0,
        tempo_changes=[
            {"time": 0.0, "bpm": 120.0},
            {"time": 6.0, "bpm": 150.0},
        ],
        notes="Tempo changes mid-song from 120 to 150 BPM.",
    )


def _syncopated() -> Fixture:
    return Fixture(
        name="syncopated",
        bpm=120.0,
        offset=0.0,
        tempo_changes=[
            {"time": 0.0, "bpm": 120.0},
        ],
        notes="Clicks with off-beat accents to fool greedy beat picking.",
    )


def _intro() -> Fixture:
    return Fixture(
        name="intro",
        bpm=120.0,
        offset=3.0,
        tempo_changes=[
            {"time": 0.0, "bpm": 120.0},
        ],
        notes="Three seconds of silence before the music starts.",
    )


def _silence() -> Fixture:
    return Fixture(
        name="silence",
        bpm=None,
        offset=0.0,
        tempo_changes=[],
        notes="Pure silence: no beats should be detected.",
    )


def _render(
    fixture: Fixture,
    *,
    sr: int,
) -> np.ndarray:
    samples = int(sr * DURATION)

    signal = np.zeros(samples)

    if fixture.name == "silence":
        return signal

    if fixture.name == "tempo-change":
        _render_tempo_change(
            signal,
            sr,
            [(0.0, 120.0), (6.0, 150.0)],
        )

        return signal

    bpm = float(fixture.bpm or 120.0)

    if fixture.name == "syncopated":
        _render_syncopated(
            signal,
            sr,
            bpm,
            fixture.offset,
        )

        return signal

    _render_regular(
        signal,
        sr,
        bpm,
        fixture.offset,
    )

    return signal


def _render_regular(
    signal: np.ndarray,
    sr: int,
    bpm: float,
    start: float,
) -> None:
    interval = 60.0 / bpm

    time = start

    while time < DURATION:
        _add_click(
            signal,
            sr,
            time,
        )

        time += interval


def _render_tempo_change(
    signal: np.ndarray,
    sr: int,
    segments: list[tuple[float, float]],
) -> None:
    time = 0.0

    for cursor, (_start, bpm) in enumerate(
        segments
    ):
        if cursor + 1 < len(segments):
            next_start = segments[cursor + 1][0]
        else:
            next_start = DURATION

        interval = 60.0 / bpm

        while time < next_start:
            _add_click(
                signal,
                sr,
                time,
            )

            time += interval


def _render_syncopated(
    signal: np.ndarray,
    sr: int,
    bpm: float,
    start: float,
) -> None:
    """Regular beats plus extra off-beat accents."""

    interval = 60.0 / bpm

    time = start

    while time < DURATION:
        _add_click(
            signal,
            sr,
            time,
        )

        # Off-beat accent halfway through the bar.
        _add_click(
            signal,
            sr,
            time + interval / 2,
            amplitude=0.4,
        )

        time += interval


def _add_click(
    signal: np.ndarray,
    sr: int,
    time: float,
    *,
    amplitude: float = 0.8,
) -> None:
    start = int(time * sr)

    end = min(
        start + int(CLICK_SECONDS * sr),
        len(signal),
    )

    if start >= len(signal):
        return

    signal[start:end] += amplitude


def _write_wav(
    path: Path,
    signal: np.ndarray,
    sr: int,
) -> None:
    pcm = (
        signal * 32767
    ).astype(np.int16)

    with wave.open(str(path), "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(sr)
        file.writeframes(pcm.tobytes())
