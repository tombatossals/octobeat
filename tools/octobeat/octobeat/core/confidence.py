"""Confidence metrics for BeatEngine.

Independent quality metrics computed from the analysis evidence:

- Tempo confidence: how much better the chosen BPM explains the
  onsets than its best alternative.
- Beat confidence: how well the beats align with the onsets.
- Grid stability: how regular the beat intervals are.
- Overall confidence: a weighted combination of the above.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .onset import onset_coverage, onset_frames
from .phase import best_phase_frames
from .tempo import (
    DEFAULT_HOP_LENGTH,
    MAX_BPM,
    MIN_BPM,
    TEMPO_VARIANTS,
    score_tempo,
)

# Tolerance around a beat (fraction of the beat period) within which
# an onset counts as covered.
COVERAGE_WINDOW_RATIO = 0.3

# Weight of each metric in the overall score.
TEMPO_WEIGHT = 0.5
BEAT_WEIGHT = 0.25
GRID_WEIGHT = 0.25


@dataclass(frozen=True, slots=True)
class Confidence:
    tempo: float
    beat: float
    grid: float
    overall: float


def analyse_confidence(
    onset_envelope: np.ndarray,
    sr: int,
    bpm: float,
    beat_times: np.ndarray,
    *,
    hop_length: int = DEFAULT_HOP_LENGTH,
) -> Confidence:
    tempo = tempo_confidence(
        onset_envelope,
        sr,
        bpm,
        hop_length=hop_length,
    )

    beat = beat_confidence(
        onset_envelope,
        sr,
        bpm,
        beat_times,
        hop_length=hop_length,
    )

    grid = grid_stability(
        beat_times,
    )

    overall = (
        TEMPO_WEIGHT * tempo
        + BEAT_WEIGHT * beat
        + GRID_WEIGHT * grid
    )

    return Confidence(
        tempo=_clamp01(tempo),
        beat=_clamp01(beat),
        grid=_clamp01(grid),
        overall=_clamp01(overall),
    )


def tempo_confidence(
    onset_envelope: np.ndarray,
    sr: int,
    bpm: float,
    *,
    hop_length: int = DEFAULT_HOP_LENGTH,
) -> float:
    """Confidence in the chosen BPM.

    Measures how much better ``bpm`` explains the onsets than its best
    alternative variant (half/double). A track with an unambiguous
    pulse scores close to 1; an ambiguous one scores low.
    """

    chosen = score_tempo(
        onset_envelope,
        sr,
        bpm,
        hop_length=hop_length,
    )

    if chosen <= 0:
        return 0.0

    runner_up = 0.0

    for factor in TEMPO_VARIANTS:
        if abs(factor - 1.0) < 1e-9:
            continue

        variant = bpm * factor

        if variant <= 0:
            continue

        if MIN_BPM <= variant <= MAX_BPM:
            runner_up = max(
                runner_up,
                score_tempo(
                    onset_envelope,
                    sr,
                    variant,
                    hop_length=hop_length,
                ),
            )

    margin = 1.0 - (runner_up / chosen) ** 2

    return _clamp01(margin)


def beat_confidence(
    onset_envelope: np.ndarray,
    sr: int,
    bpm: float,
    beat_times: np.ndarray,
    *,
    hop_length: int = DEFAULT_HOP_LENGTH,
) -> float:
    """Confidence in the beat alignment.

    Fraction of the detected onsets that fall within a beat window.
    High when the musical onsets coincide with the grid.
    """

    if bpm <= 0:
        return 0.0

    period_frames = (
        60.0 / bpm * sr / hop_length
    )

    if period_frames < 2:
        return 0.0

    onsets = onset_frames(
        onset_envelope,
        sr,
        hop_length=hop_length,
    )

    if onsets.size == 0:
        return 0.0

    phase = best_phase_frames(
        onset_envelope,
        period_frames,
    )

    n = int(onset_envelope.size)

    beats = (
        phase
        + np.arange(0, n, period_frames)
    )

    beats = beats[beats < n]

    if beats.size == 0:
        return 0.0

    window = period_frames * COVERAGE_WINDOW_RATIO

    return onset_coverage(
        onsets,
        beats,
        window,
    )


def grid_stability(
    beat_times: np.ndarray,
) -> float:
    """Regularity of the beat grid.

    Based on the coefficient of variation of the beat intervals and a
    penalty for abnormally wide gaps (which indicate removed or
    duplicated beats).
    """

    if beat_times.size < 2:
        return 0.0

    diffs = np.diff(
        beat_times,
    )

    mean = float(np.mean(diffs))

    if mean <= 0:
        return 0.0

    cv = float(np.std(diffs)) / mean

    max_ratio = float(
        np.max(diffs),
    ) / mean

    gap_penalty = max(
        0.0,
        max_ratio - 1.0,
    )

    return _clamp01(
        1.0 - cv - 0.5 * gap_penalty,
    )


def _clamp01(
    value: float,
) -> float:
    return float(
        max(
            0.0,
            min(1.0, value),
        ),
    )
