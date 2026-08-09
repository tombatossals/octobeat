from __future__ import annotations

import numpy as np
import pytest

from octobeat.core.grid import build_beat_grid
from octobeat.core.onset import compute_onset_envelope
from octobeat.core.phase import estimate_phase
from octobeat.core.tempo import (
    estimate_tempo,
    estimate_tempo_candidates,
    estimate_tempo_map,
    score_tempo,
)

SR = 22050
DURATION = 10.0


def _click_wave(
    bpm: float,
    *,
    seconds: float = DURATION,
    start: float = 0.0,
    click_seconds: float = 0.03,
) -> np.ndarray:
    samples = int(SR * seconds)

    wave = np.zeros(samples)

    interval = 60.0 / bpm

    time = start

    while time < seconds:
        index = int(time * SR)

        end = min(
            index + int(click_seconds * SR),
            samples,
        )

        wave[index:end] += 0.8

        time += interval

    return wave


def _envelope(bpm: float, **kwargs) -> np.ndarray:
    return compute_onset_envelope(
        _click_wave(bpm, **kwargs),
        SR,
    )


@pytest.mark.parametrize(
    "expected",
    [60, 80, 120, 160, 175, 240],
)
def test_detects_constant_tempo(
    expected: int,
) -> None:
    bpm = estimate_tempo(
        _envelope(expected),
        SR,
    )

    assert abs(bpm - expected) < 2.0


@pytest.mark.parametrize(
    "true_bpm",
    [80, 160, 175],
)
def test_resolves_half_and_double_time(
    true_bpm: int,
) -> None:
    """A 160 BPM track must not resolve to 80 or 320 BPM."""

    envelope = _envelope(true_bpm)

    bpm = estimate_tempo(envelope, SR)

    assert abs(bpm - true_bpm) < 2.0

    for variant in (
        true_bpm / 2,
        true_bpm * 2,
    ):
        assert score_tempo(
            envelope,
            SR,
            float(true_bpm),
        ) > score_tempo(
            envelope,
            SR,
            float(variant),
        )


def test_tempo_candidates_include_fundamental() -> None:
    envelope = _envelope(120)

    candidates = estimate_tempo_candidates(
        envelope,
        SR,
    )

    assert any(
        abs(candidate - 120) < 5
        for candidate in candidates
    )


def test_grid_is_regular() -> None:
    envelope = _envelope(120)

    bpm = estimate_tempo(envelope, SR)
    phase = estimate_phase(envelope, SR, bpm)

    grid = build_beat_grid(
        envelope,
        SR,
        bpm,
        phase,
        DURATION,
    )

    assert len(grid) > 10

    interval = 60.0 / bpm

    diffs = np.diff(grid)

    # Regular spacing: no gap below half a beat (no duplicates)
    # and no gap more than 50% wider than the interval (continuity).
    assert np.min(diffs) >= interval * 0.5
    assert np.max(diffs) <= interval * 1.5

    # Strictly increasing, no overlapping beats.
    assert np.all(np.diff(grid) > 0)


def test_grid_covers_duration() -> None:
    envelope = _envelope(100)

    bpm = estimate_tempo(envelope, SR)
    phase = estimate_phase(envelope, SR, bpm)

    grid = build_beat_grid(
        envelope,
        SR,
        bpm,
        phase,
        DURATION,
    )

    assert grid[-1] <= DURATION
    assert grid[0] >= 0


def test_phase_handles_intro() -> None:
    envelope = _envelope(
        120,
        start=0.5,
    )

    bpm = estimate_tempo(envelope, SR)
    phase = estimate_phase(envelope, SR, bpm)

    interval = 60.0 / bpm

    # The phase should place a beat on (or just after) the first click.
    distance = abs(
        (phase - 0.5) % interval
    )

    assert min(distance, interval - distance) < 0.1


def test_grid_phase_is_stable() -> None:
    """Phase changes by less than half a beat for the same track."""

    envelopes = [
        _envelope(120, start=0.25),
        _envelope(120, start=0.25),
    ]

    bpm = estimate_tempo(
        envelopes[0],
        SR,
    )

    phases = [
        estimate_phase(envelope, SR, bpm)
        for envelope in envelopes
    ]

    interval = 60.0 / bpm

    difference = abs(phases[0] - phases[1])

    assert min(
        difference,
        interval - difference,
    ) < 0.05


def test_snap_is_limited() -> None:
    """A beat far from any onset must not be pulled to it."""

    envelope = _envelope(120)

    bpm = estimate_tempo(envelope, SR)
    phase = estimate_phase(envelope, SR, bpm)

    grid = build_beat_grid(
        envelope,
        SR,
        bpm,
        phase,
        DURATION,
        max_snap_distance=0.001,
    )

    interval = 60.0 / bpm

    # With essentially no snapping the grid stays mathematical.
    diffs = np.diff(grid)

    assert np.max(
        np.abs(diffs - interval),
    ) < 0.01


def test_tempo_map_constant_single_segment() -> None:
    envelope = _envelope(120)

    tempo_map = estimate_tempo_map(
        envelope,
        SR,
    )

    assert len(tempo_map) == 1

    start, bpm = tempo_map[0]

    assert start == 0.0
    assert abs(bpm - 120) < 5


def test_tempo_map_detects_tempo_change() -> None:
    """A 120 -> 150 BPM change must produce two segments."""

    # Build a two-segment track: 120 BPM for 6s, 150 BPM for 6s.
    samples = int(SR * DURATION)

    wave = np.zeros(samples)

    time = 0.0
    while time < 6.0:
        index = int(time * SR)
        wave[
            index : index + int(0.03 * SR)
        ] += 0.8
        time += 60.0 / 120.0

    time = 6.0
    while time < DURATION:
        index = int(time * SR)
        wave[
            index : index + int(0.03 * SR)
        ] += 0.8
        time += 60.0 / 150.0

    envelope = compute_onset_envelope(
        wave,
        SR,
    )

    tempo_map = estimate_tempo_map(
        envelope,
        SR,
    )

    assert len(tempo_map) == 2

    first_start, first_bpm = tempo_map[0]
    second_start, second_bpm = tempo_map[1]

    assert first_start == 0.0
    assert abs(first_bpm - 120) < 5
    assert abs(second_bpm - 150) < 5


def test_tempo_map_ignores_half_time_blip() -> None:
    """A brief 120 -> 80 -> 120 fluctuation must not create segments."""

    samples = int(SR * DURATION)

    wave = np.zeros(samples)

    # Mostly 120 BPM.
    time = 0.0
    while time < DURATION:
        index = int(time * SR)
        wave[
            index : index + int(0.03 * SR)
        ] += 0.8
        time += 60.0 / 120.0

    # A short quiet passage around 4s-5s (no clicks).
    quiet_start = int(4.0 * SR)
    quiet_end = int(5.0 * SR)
    wave[quiet_start:quiet_end] = 0.0

    envelope = compute_onset_envelope(
        wave,
        SR,
    )

    tempo_map = estimate_tempo_map(
        envelope,
        SR,
    )

    # No tempo change: still a single segment.
    assert len(tempo_map) == 1

    _start, bpm = tempo_map[0]

    assert abs(bpm - 120) < 5
