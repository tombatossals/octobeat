"""Beat grid construction for BeatEngine.

Builds the musical beat grid from a constant tempo and a phase, then
applies limited snapping to the onsets and validates the result so the
grid never contains duplicate or overlapping beats.
"""

from __future__ import annotations

import numpy as np

from .onset import onset_times

DEFAULT_HOP_LENGTH = 512

# Maximum distance (seconds) a beat may be pulled towards an onset.
MAX_SNAP_DISTANCE = 0.05

# Beats closer than this fraction of the beat interval are discarded.
MIN_GAP_RATIO = 0.5


def build_beat_grid(
    onset_envelope: np.ndarray,
    sr: int,
    bpm: float,
    phase: float,
    duration: float,
    *,
    hop_length: int = DEFAULT_HOP_LENGTH,
    max_snap_distance: float = MAX_SNAP_DISTANCE,
) -> np.ndarray:
    """Build the musical beat grid (seconds).

    The grid is computed mathematically from ``bpm`` and ``phase``,
    then each beat may be snapped towards the nearest onset, but only
    within ``max_snap_distance``. Finally the grid is validated to
    discard beats that are too close together.
    """

    if bpm <= 0:
        return np.array([])

    interval = 60.0 / bpm

    if duration <= 0:
        return np.array([])

    grid = _math_grid(
        phase,
        interval,
        duration,
    )

    if grid.size == 0:
        return grid

    onsets = onset_times(
        onset_envelope,
        sr,
        hop_length=hop_length,
    )

    grid = _snap_to_onsets(
        grid,
        onsets,
        max_snap_distance,
    )

    grid = _remove_close_beats(
        grid,
        interval * MIN_GAP_RATIO,
    )

    return grid


def _math_grid(
    phase: float,
    interval: float,
    duration: float,
) -> np.ndarray:
    """Regular grid of beats from ``phase`` to ``duration``."""

    if phase >= duration:
        return np.array([])

    count = int(
        np.ceil(
            (duration - phase)
            / interval
        ),
    )

    return (
        phase
        + np.arange(count) * interval
    )


def _snap_to_onsets(
    grid: np.ndarray,
    onsets: np.ndarray,
    max_distance: float,
) -> np.ndarray:
    if onsets.size == 0:
        return grid

    snapped = grid.copy()

    insertion = np.searchsorted(
        onsets,
        grid,
    )

    for index, beat in enumerate(
        grid,
    ):
        position = insertion[index]

        candidates: list[float] = []

        if position < onsets.size:
            candidates.append(
                onsets[position],
            )

        if position > 0:
            candidates.append(
                onsets[position - 1],
            )

        if not candidates:
            continue

        nearest = min(
            candidates,
            key=lambda onset: abs(
                onset - beat
            ),
        )

        if (
            abs(nearest - beat)
            <= max_distance
        ):
            snapped[index] = nearest

    return snapped


def _remove_close_beats(
    grid: np.ndarray,
    min_gap: float,
) -> np.ndarray:
    if grid.size < 2:
        return grid

    kept = [float(grid[0])]

    for beat in grid[1:]:
        if (
            float(beat) - kept[-1]
            >= min_gap
        ):
            kept.append(
                float(beat),
            )

    return np.asarray(kept)
