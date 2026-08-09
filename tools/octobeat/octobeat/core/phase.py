"""Phase estimation for BeatEngine.

Determines the temporal position of the beat grid: the phase offset
within one beat period that best aligns the pulse train with the
onsets.
"""

from __future__ import annotations

import numpy as np

DEFAULT_HOP_LENGTH = 512

# Number of phase candidates scanned within one beat period.
N_PHASES = 64


def best_phase_frames(
    onset_envelope: np.ndarray,
    period_frames: float,
    *,
    n_phases: int = N_PHASES,
) -> float:
    """Return the phase (in frames) that best aligns onsets to beats.

    Scans ``n_phases`` offsets inside one beat period and returns the
    offset whose pulse train captures the most onset energy.
    """

    n = int(onset_envelope.size)

    if period_frames < 2 or n == 0:
        return 0.0

    best_phase = 0.0
    best_energy = -1.0

    for step in range(n_phases):
        phase = (
            step
            / n_phases
            * period_frames
        )

        beats = (
            phase
            + np.arange(
                0,
                n,
                period_frames,
            )
        )

        beats = (
            beats[beats < n]
            .astype(int)
        )

        if beats.size == 0:
            continue

        energy = float(
            np.sum(
                onset_envelope[beats],
            ),
        )

        if energy > best_energy:
            best_energy = energy
            best_phase = phase

    return best_phase


def estimate_phase(
    onset_envelope: np.ndarray,
    sr: int,
    bpm: float,
    *,
    hop_length: int = DEFAULT_HOP_LENGTH,
) -> float:
    """Return the best grid phase offset in seconds."""

    if bpm <= 0:
        return 0.0

    period_frames = (
        60.0 / bpm * sr / hop_length
    )

    phase_frames = best_phase_frames(
        onset_envelope,
        period_frames,
    )

    return float(
        phase_frames
        * hop_length
        / sr
    )
