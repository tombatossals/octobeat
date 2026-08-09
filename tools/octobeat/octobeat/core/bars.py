"""Bar grid and downbeat detection for BeatEngine.

Groups the detected beats into bars according to a time signature and
detects the downbeat (the first beat of each bar) from the onset
evidence, so bars do not simply start at beat 1 when the music begins
on a pickup or an off-beat.
"""

from __future__ import annotations

import librosa
import numpy as np

from octobeat.models.songmap import Bar

DEFAULT_HOP_LENGTH = 512

# Time signature -> beats per bar.
BEATS_PER_BAR_BY_SIGNATURE: dict[str, int] = {
    "2/4": 2,
    "3/4": 3,
    "4/4": 4,
    "6/8": 6,
    "7/8": 7,
    "9/8": 9,
    "12/8": 12,
}

# The default time signature when the input does not map to a known
# signature.
DEFAULT_BEATS_PER_BAR = 4


def beats_per_bar(
    time_signature: str,
) -> int:
    """Beats per bar for a time signature string (e.g. "4/4")."""

    return BEATS_PER_BAR_BY_SIGNATURE.get(
        time_signature,
        DEFAULT_BEATS_PER_BAR,
    )


def detect_downbeat_shift(
    onset_envelope: np.ndarray,
    sr: int,
    beat_times: np.ndarray,
    beats_per_bar: int,
    *,
    hop_length: int = DEFAULT_HOP_LENGTH,
) -> int:
    """Return the residue (0..beats_per_bar-1) of the downbeat beats.

    Beats whose grid index satisfies ``index % beats_per_bar == shift``
    (1-based) are treated as the first beat of their bar.

    When no residue is clearly stronger than the others (uniform click
    track, for example) the shift defaults to 0, so bar 1 starts at
    beat 1.
    """

    if beats_per_bar < 2:
        return 0

    if beat_times.size < beats_per_bar:
        return 0

    beat_frames = librosa.time_to_frames(
        beat_times,
        sr=sr,
        hop_length=hop_length,
    )

    window = 2

    energies: list[float] = []

    for frame in beat_frames:
        low = max(
            0,
            int(frame) - window,
        )

        high = min(
            len(onset_envelope),
            int(frame) + window + 1,
        )

        if low >= high:
            energies.append(0.0)
            continue

        energies.append(
            float(
                np.max(
                    onset_envelope[low:high],
                ),
            ),
        )

    sums = [0.0] * beats_per_bar
    counts = [0] * beats_per_bar

    for index, energy in enumerate(energies):
        residue = index % beats_per_bar

        sums[residue] += energy
        counts[residue] += 1

    means = [
        (sums[r] / counts[r])
        if counts[r] > 0
        else 0.0
        for r in range(beats_per_bar)
    ]

    best = int(
        np.argmax(means),
    )

    # Require the winning residue to be meaningfully stronger than the
    # average, otherwise fall back to beat 1 as the downbeat.
    overall_mean = float(
        np.mean(means),
    )

    if means[best] < overall_mean * 1.15:
        return 0

    return best


def build_bars(
    beat_indices: list[int],
    beats_per_bar: int,
    downbeat_shift: int = 0,
) -> list[Bar]:
    """Group beat indices into bars starting on the downbeat.

    ``downbeat_shift`` is the residue (0-based, relative to beat 1) of
    the beats that begin a bar. The first bar starts on the first
    downbeat at or after the first beat; earlier beats form a pickup.
    """

    if not beat_indices:
        return []

    first_beat = beat_indices[0]

    residue = (first_beat - 1) % beats_per_bar

    advance = (
        downbeat_shift - residue
    ) % beats_per_bar

    first_beat += advance

    bars: list[Bar] = []

    bar_index = 1

    while first_beat <= beat_indices[-1]:
        bars.append(
            Bar(
                index=bar_index,
                firstBeat=first_beat,
            ),
        )

        bar_index += 1

        first_beat += beats_per_bar

    return bars
