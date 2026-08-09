"""Tempo estimation for BeatEngine.

Generates a set of tempo candidates and scores each one against the
onset evidence, resolving half-time/double-time ambiguity by selecting
the candidate whose pulse train aligns best with the onsets.
"""

from __future__ import annotations

import numpy as np

from .onset import onset_coverage, onset_frames
from .phase import best_phase_frames

DEFAULT_HOP_LENGTH = 512

MIN_BPM = 40.0
MAX_BPM = 300.0

# Octave factors evaluated for every candidate.
TEMPO_VARIANTS = (0.5, 1.0, 2.0)

# Tolerance around a beat (as a fraction of the beat period) within
# which an onset counts as "covered".
COVERAGE_WINDOW_RATIO = 0.3


def estimate_tempo(
    onset_envelope: np.ndarray,
    sr: int,
    *,
    hop_length: int = DEFAULT_HOP_LENGTH,
    min_bpm: float = MIN_BPM,
    max_bpm: float = MAX_BPM,
) -> float:
    """Estimate the musical tempo (BPM) of the recording.

    The best candidate and its half/double variants are compared and
    the one with the highest ``score_tempo`` is returned.
    """

    candidates = estimate_tempo_candidates(
        onset_envelope,
        sr,
        hop_length=hop_length,
        min_bpm=min_bpm,
        max_bpm=max_bpm,
    )

    variants: set[float] = set()

    for candidate in candidates:
        for factor in TEMPO_VARIANTS:
            variant = candidate * factor

            if min_bpm <= variant <= max_bpm:
                variants.add(
                    round(variant, 2),
                )

    if not variants:
        return 0.0

    best_bpm = 0.0
    best_score = -1.0

    for variant in variants:
        refined, score = _refine_tempo(
            onset_envelope,
            sr,
            variant,
            hop_length=hop_length,
        )

        if score > best_score:
            best_bpm = refined
            best_score = score

    return best_bpm


# Tempo map estimation.
#
# The recording is scanned with a sliding window; each window is
# scored against a set of candidate tempos and the best local tempo is
# recorded. The resulting (time, bpm) curve is simplified to a
# polyline whose vertices become the tempo map anchors. Between
# anchors the tempo is interpolated linearly, so the map represents
# both constant passages and continuous ramps (accelerando,
# ritardando).

WINDOW_SECONDS = 4.0
WINDOW_HOP_SECONDS = 2.0

# RDP simplification tolerance (in BPM), relative to the global tempo.
TEMPO_MAP_TOLERANCE = 0.03

# BPM difference below which two consecutive anchors are collapsed
# into a single constant segment.
TEMPO_COLLAPSE_RATIO = 0.01


def estimate_tempo_map(
    onset_envelope: np.ndarray,
    sr: int,
    *,
    hop_length: int = DEFAULT_HOP_LENGTH,
    global_bpm: float | None = None,
) -> list[tuple[float, float]]:
    """Detect the tempo curve as ``(time, bpm)`` anchors.

    The map is a polyline: between consecutive anchors the tempo is
    interpolated linearly, supporting constant tempo, discrete changes
    and gradual ramps. The map always starts at 0.0.
    """

    if global_bpm is None:
        global_bpm = estimate_tempo(
            onset_envelope,
            sr,
            hop_length=hop_length,
        )

    if global_bpm <= 0:
        return []

    n = int(onset_envelope.size)

    frames_per_second = sr / hop_length

    window_frames = int(
        WINDOW_SECONDS * frames_per_second,
    )

    hop_frames = int(
        WINDOW_HOP_SECONDS * frames_per_second,
    )

    if n < window_frames:
        return [(0.0, round(global_bpm, 2))]

    points: list[tuple[float, float]] = []

    for start in range(
        0,
        n - window_frames + 1,
        hop_frames,
    ):
        window = onset_envelope[
            start : start + window_frames
        ]

        bpm = _window_tempo(
            window,
            sr,
            global_bpm,
            hop_length=hop_length,
        )

        if bpm <= 0:
            continue

        time = start / frames_per_second

        points.append(
            (time, bpm),
        )

    if not points:
        return [(0.0, round(global_bpm, 2))]

    tolerance = max(
        1.5,
        global_bpm * TEMPO_MAP_TOLERANCE,
    )

    anchors = _rdp_simplify(
        points,
        tolerance,
    )

    return _finalize_anchors(
        anchors,
        global_bpm,
    )


def _window_tempo(
    window: np.ndarray,
    sr: int,
    global_bpm: float,
    *,
    hop_length: int,
) -> float:
    """Best-scoring tempo for a single window, octave-locked to the
    global tempo.

    Each window is resolved to the octave variant closest to
    ``global_bpm``, so the tempo map never flickers between a tempo
    and its half/double in adjacent windows.
    """

    candidates = estimate_tempo_candidates(
        window,
        sr,
        hop_length=hop_length,
    )

    variants: set[float] = set()

    for candidate in candidates:
        variant = _lock_to_octave(
            candidate,
            global_bpm,
        )

        if MIN_BPM <= variant <= MAX_BPM:
            variants.add(
                round(variant, 2),
            )

    if not variants:
        return 0.0

    best_bpm = 0.0
    best_score = -1.0

    for variant in variants:
        score = score_tempo(
            window,
            sr,
            variant,
            hop_length=hop_length,
        )

        if score > best_score:
            best_bpm = variant
            best_score = score

    return best_bpm


def _lock_to_octave(
    bpm: float,
    reference: float,
) -> float:
    """Fold ``bpm`` into the octave of ``reference``.

    Repeatedly halves or doubles ``bpm`` until it lies within the
    same octave as ``reference`` (between reference/1.4 and
    reference*1.4).
    """

    if reference <= 0:
        return bpm

    lower = reference / 1.4
    upper = reference * 1.4

    while bpm > upper:
        bpm /= 2.0

    while bpm < lower:
        bpm *= 2.0

    return bpm


def _rdp_simplify(
    points: list[tuple[float, float]],
    epsilon: float,
) -> list[tuple[float, float]]:
    """Ramer–Douglas–Peucker simplification of the tempo curve.

    Keeps the vertices that approximate the curve within ``epsilon``
    BPM, producing a compact polyline that preserves both constant
    passages and gradual ramps.
    """

    if len(points) < 3:
        return points

    start_time, start_bpm = points[0]
    end_time, end_bpm = points[-1]

    best_index = 1
    best_distance = -1.0

    for index in range(1, len(points) - 1):
        time, bpm = points[index]

        if end_time - start_time <= 0:
            distance = abs(bpm - start_bpm)
        else:
            fraction = (
                time - start_time
            ) / (end_time - start_time)

            line_bpm = (
                start_bpm
                + fraction
                * (end_bpm - start_bpm)
            )

            distance = abs(
                bpm - line_bpm,
            )

        if distance > best_distance:
            best_distance = distance
            best_index = index

    if best_distance <= epsilon:
        return [points[0], points[-1]]

    left = _rdp_simplify(
        points[: best_index + 1],
        epsilon,
    )

    right = _rdp_simplify(
        points[best_index:],
        epsilon,
    )

    return left[:-1] + right


def _finalize_anchors(
    anchors: list[tuple[float, float]],
    global_bpm: float,
) -> list[tuple[float, float]]:
    """Normalise anchors: start at 0.0 and collapse flat regions."""

    if not anchors:
        return []

    first_time, first_bpm = anchors[0]

    if first_time > 0:
        anchors.insert(
            0,
            (0.0, first_bpm),
        )

    collapsed: list[tuple[float, float]] = []

    for time, bpm in anchors:
        if not collapsed:
            collapsed.append(
                (round(time, 3), round(bpm, 2)),
            )
            continue

        _prev_time, prev_bpm = collapsed[-1]

        ratio = (
            abs(bpm - prev_bpm)
            / max(prev_bpm, 1e-9)
        )

        if ratio < TEMPO_COLLAPSE_RATIO:
            continue

        collapsed.append(
            (round(time, 3), round(bpm, 2)),
        )

    if not collapsed:
        return [(0.0, round(global_bpm, 2))]

    # A single anchor means constant tempo throughout.
    if len(collapsed) == 1:
        return collapsed

    return collapsed


def _refine_tempo(
    onset_envelope: np.ndarray,
    sr: int,
    bpm: float,
    *,
    hop_length: int,
    radius: float = 6.0,
) -> tuple[float, float]:
    """Locally search BPMs around ``bpm`` and return the best scored one.

    Two passes: a coarse scan (1 BPM steps) followed by a fine scan
    (0.05 BPM steps) around the coarse winner, so the exact tempo peak
    is found even when it does not land on a coarse grid point.
    """

    best_bpm, best_score = _scan_tempo(
        onset_envelope,
        sr,
        bpm - radius,
        bpm + radius,
        1.0,
        hop_length,
    )

    best_bpm, best_score = _scan_tempo(
        onset_envelope,
        sr,
        best_bpm - 1.5,
        best_bpm + 1.5,
        0.05,
        hop_length,
        best_bpm,
        best_score,
    )

    return best_bpm, best_score


def _scan_tempo(
    onset_envelope: np.ndarray,
    sr: int,
    start: float,
    end: float,
    step: float,
    hop_length: int,
    seed_bpm: float | None = None,
    seed_score: float = -1.0,
) -> tuple[float, float]:
    best_bpm = seed_bpm if seed_bpm is not None else start
    best_score = seed_score

    if seed_bpm is None:
        best_score = score_tempo(
            onset_envelope,
            sr,
            best_bpm,
            hop_length=hop_length,
        )

    candidate = start

    while candidate <= end + 1e-9:
        if candidate > 0:
            score = score_tempo(
                onset_envelope,
                sr,
                candidate,
                hop_length=hop_length,
            )

            if score > best_score:
                best_score = score
                best_bpm = candidate

        candidate += step

    return best_bpm, best_score


def estimate_tempo_candidates(
    onset_envelope: np.ndarray,
    sr: int,
    *,
    hop_length: int = DEFAULT_HOP_LENGTH,
    min_bpm: float = MIN_BPM,
    max_bpm: float = MAX_BPM,
    top_n: int = 6,
) -> list[float]:
    """Return tempo candidates derived from onset autocorrelation.

    A periodic signal produces autocorrelation peaks at its period and
    at integer multiples of it, which naturally yields the bpm, its
    half and its double as candidates.
    """

    n = int(onset_envelope.size)

    if n < 4:
        return []

    envelope = (
        onset_envelope
        - np.mean(onset_envelope)
    )

    ac = np.correlate(
        envelope,
        envelope,
        "full",
    )[n - 1 :]

    if ac.size == 0 or ac[0] <= 0:
        return []

    ac = ac / ac[0]

    min_lag = max(
        1,
        int(
            60.0
            * sr
            / (hop_length * max_bpm)
        ),
    )

    max_lag = min(
        int(
            60.0
            * sr
            / (hop_length * min_bpm)
        ),
        n - 1,
    )

    if min_lag > max_lag:
        return []

    peaks = _local_maxima(
        ac,
        min_lag,
        max_lag,
    )

    scored: list[tuple[float, float]] = []

    for lag in peaks:
        refined = _refine_lag(
            ac,
            lag,
        )

        bpm = _bpm_for_lag(
            sr,
            hop_length,
            refined,
        )

        if bpm <= 0:
            continue

        scored.append(
            (
                bpm,
                float(ac[lag]),
            )
        )

    scored.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    return [
        bpm
        for bpm, _score in scored[:top_n]
    ]


def _refine_lag(
    ac: np.ndarray,
    lag: int,
) -> float:
    """Parabolic interpolation of an autocorrelation peak."""

    if (
        lag <= 0
        or lag + 1 >= ac.size
    ):
        return float(lag)

    left = float(ac[lag - 1])
    center = float(ac[lag])
    right = float(ac[lag + 1])

    denominator = left - 2 * center + right

    if abs(denominator) < 1e-12:
        return float(lag)

    offset = (
        0.5 * (left - right) / denominator
    )

    if offset < -1.0 or offset > 1.0:
        return float(lag)

    return float(lag + offset)


def _bpm_for_lag(
    sr: int,
    hop_length: int,
    lag: float,
) -> float:
    return 60.0 * sr / (hop_length * lag)


def score_tempo(
    onset_envelope: np.ndarray,
    sr: int,
    bpm: float,
    *,
    hop_length: int = DEFAULT_HOP_LENGTH,
) -> float:
    """Score how well a pulse train at ``bpm`` explains the onsets.

    Combines two complementary measurements:

    - Coverage: the fraction of onsets that fall near a beat. This
      strongly favours the fundamental pulse over its sub-harmonics
      (a bpm/3 grid leaves most onsets uncovered).
    - Contrast: the mean onset energy on beats minus the energy half
      a beat away, normalised by the peak. This favours the pulse
      over its double (a bpm*2 grid puts many beats in the gaps).
    """

    if bpm <= 0:
        return 0.0

    period_frames = (
        60.0 / bpm * sr / hop_length
    )

    n = int(onset_envelope.size)

    if period_frames < 2 or n == 0:
        return 0.0

    peak = float(np.max(onset_envelope))

    if peak <= 0:
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

    beats = (
        phase
        + np.arange(0, n, period_frames)
    )

    beats = beats[beats < n]

    if beats.size == 0:
        return 0.0

    coverage = onset_coverage(
        onsets,
        beats,
        period_frames * COVERAGE_WINDOW_RATIO,
    )

    beat_indices = beats.astype(int)

    mids = (
        beat_indices
        + int(period_frames / 2)
    )

    mids = mids[mids < n]

    if mids.size == 0:
        return coverage

    on_beat = float(
        np.mean(
            onset_envelope[beat_indices],
        ),
    )

    off_beat = float(
        np.mean(
            onset_envelope[mids],
        ),
    )

    contrast = float(
        max(
            0.0,
            (on_beat - off_beat) / peak,
        ),
    )

    return coverage * contrast


def _local_maxima(
    values: np.ndarray,
    min_lag: int,
    max_lag: int,
) -> list[int]:
    peaks: list[int] = []

    for lag in range(
        min_lag + 1,
        max_lag,
    ):
        window = values[
            lag - 1 : lag + 2
        ]

        if (
            values[lag] > 0
            and values[lag] >= window[0]
            and values[lag] > window[2]
        ):
            peaks.append(lag)

    return peaks
