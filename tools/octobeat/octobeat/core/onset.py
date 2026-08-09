"""Onset analysis for BeatEngine.

Extracts the attack information of the audio independently of any
beat tracking. Downstream stages (tempo, phase, grid) consume the
onset envelope as evidence.
"""

from __future__ import annotations

import librosa
import numpy as np

DEFAULT_HOP_LENGTH = 512


def compute_onset_envelope(
    y: np.ndarray,
    sr: int,
    *,
    hop_length: int = DEFAULT_HOP_LENGTH,
) -> np.ndarray:
    """Compute the onset-strength envelope of ``y``.

    The returned envelope is normalised to ``[0, 1]`` so it can be
    compared across songs.
    """

    onset = librosa.onset.onset_strength(
        y=y,
        sr=sr,
        hop_length=hop_length,
    )

    peak = float(
        np.max(onset),
    )

    if peak <= 0:
        return onset

    return onset / peak


def onset_frames(
    onset_envelope: np.ndarray,
    sr: int,
    *,
    hop_length: int = DEFAULT_HOP_LENGTH,
    backtrack: bool = True,
) -> np.ndarray:
    """Return the frames of detected onsets."""

    return librosa.onset.onset_detect(
        onset_envelope=onset_envelope,
        sr=sr,
        hop_length=hop_length,
        backtrack=backtrack,
        units="frames",
    )


def onset_times(
    onset_envelope: np.ndarray,
    sr: int,
    *,
    hop_length: int = DEFAULT_HOP_LENGTH,
    backtrack: bool = True,
) -> np.ndarray:
    """Return the times (seconds) of detected onsets."""

    times = librosa.frames_to_time(
        onset_frames(
            onset_envelope,
            sr,
            hop_length=hop_length,
            backtrack=backtrack,
        ),
        sr=sr,
        hop_length=hop_length,
    )

    return np.asarray(
        times,
        dtype=float,
    )


def envelope_energy_at_frames(
    onset_envelope: np.ndarray,
    frames: np.ndarray,
) -> float:
    """Mean onset energy at ``frames`` (clamped to the envelope)."""

    if onset_envelope.size == 0:
        return 0.0

    clipped = frames[
        (frames >= 0)
        & (frames < onset_envelope.size)
    ]

    if clipped.size == 0:
        return 0.0

    return float(
        np.mean(
            onset_envelope[clipped],
        ),
    )


def onset_coverage(
    onsets: np.ndarray,
    beats: np.ndarray,
    window: float,
) -> float:
    """Fraction of ``onsets`` within ``window`` frames of a beat."""

    if onsets.size == 0 or beats.size == 0:
        return 0.0

    positions = np.searchsorted(
        beats,
        onsets,
    )

    covered = 0

    for index, onset in enumerate(
        onsets,
    ):
        position = positions[index]

        closest = np.inf

        if position < beats.size:
            closest = min(
                closest,
                abs(
                    beats[position]
                    - onset
                ),
            )

        if position > 0:
            closest = min(
                closest,
                abs(
                    beats[position - 1]
                    - onset
                ),
            )

        if closest <= window:
            covered += 1

    return float(covered) / onsets.size
