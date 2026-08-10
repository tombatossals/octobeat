"""Chart-vs-audio timing validation.

Even when a community chart exists, we must not assume it is perfect.
This module compares chart-derived ``TimingData`` against the audio
recording and produces a per-check diagnostic:

    Chart/audio validation

    BPM................ 162 ✓
    Duration........... 159.2 s ✓
    Offset............. +12 ms ✓
    Tempo changes...... 0 ✓

Discrepancies produce warnings; an excessive mismatch is never a hard
failure (the dataset must still build from audio).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import librosa
import numpy as np

from octobeat.core.analyser import _detect_music_start
from octobeat.core.onset import compute_onset_envelope
from octobeat.core.tempo import (
    estimate_tempo,
    estimate_tempo_candidates_scored,
    estimate_tempo_map,
)
from octobeat.models.timing import (
    TempoSegment,
    TimingData,
)

# Tolerance windows (configurable per check).

# BPM: relative difference below which two tempos match. Half/double-time
# matches use a looser tolerance because tempo estimation noise is larger
# when the audio resolves to a sub-harmonic.
BPM_TOLERANCE_RATIO = 0.04
BPM_HALF_DOUBLE_TOLERANCE_RATIO = 0.08

# Duration: absolute difference (seconds) below which durations match.
DURATION_TOLERANCE_SECONDS = 2.0

# Offset: absolute difference (ms) below which offsets match. Generous
# (about half a beat) because the audio music-start detector can miss
# the attack of the first beat by a few hundred ms.
OFFSET_TOLERANCE_MS = 500.0

# Tempo changes: allowed difference in the relative tempo span (chart
# vs audio).
TEMPO_CHANGES_TOLERANCE = 0.15

# Onset coverage below which the beat grid is considered displaced.
DRIFT_COVERAGE_THRESHOLD = 0.35

# Autocorrelation score below which the audio is not clearly periodic,
# so the audio tempo estimate is unreliable and the BPM check does not
# penalise the chart.
BPM_SCORE_FLOOR = 0.10


@dataclass(frozen=True, slots=True)
class TimingCheck:
    """
    Result of a single validation check.
    """

    name: str

    ok: bool

    detail: str

    warn: bool = False


@dataclass(frozen=True, slots=True)
class TimingValidation:
    """
    Result of validating a chart against an audio recording.
    """

    checks: list[TimingCheck]

    confidence: float

    corrected_offset: float | None = None

    @property
    def has_warnings(self) -> bool:
        return any(check.warn for check in self.checks)


@dataclass(frozen=True, slots=True)
class AudioMetrics:
    """
    Metrics extracted from the audio recording for validation.
    """

    duration: float

    bpm: float

    bpm_score: float

    tempo_candidates: list[tuple[float, float]]

    tempo_map: list[tuple[float, float]]

    offset: float

    onset_envelope: np.ndarray

    sr: int


def analyse_audio(path: Path) -> AudioMetrics:
    """
    Analyse an audio file for validation purposes.
    """

    y, sr_raw = librosa.load(
        str(path),
        sr=None,
        mono=True,
    )

    sr = int(sr_raw)

    duration = float(
        librosa.get_duration(
            y=y,
            sr=sr,
        ),
    )

    onset_envelope = compute_onset_envelope(
        y=y,
        sr=sr,
    )

    bpm = estimate_tempo(
        onset_envelope,
        sr,
    )

    if bpm <= 0 and duration > 0:
        bpm = 120.0

    candidates = estimate_tempo_candidates_scored(
        onset_envelope,
        sr,
    )

    bpm_score = (
        candidates[0][1]
        if candidates
        else 0.0
    )

    tempo_map = estimate_tempo_map(
        onset_envelope,
        sr,
        global_bpm=bpm,
    )

    offset = _detect_music_start(
        onset_envelope,
        sr,
    )

    return AudioMetrics(
        duration=duration,
        bpm=bpm,
        bpm_score=bpm_score,
        tempo_candidates=candidates,
        tempo_map=tempo_map,
        offset=offset,
        onset_envelope=onset_envelope,
        sr=sr,
    )


def validate_chart(
    chart: TimingData,
    audio: AudioMetrics,
) -> TimingValidation:
    """
    Compare chart-derived timing against the audio metrics.

    Returns per-check results, an overall confidence and (when the chart
    offset differs from the audio) a corrected offset.
    """

    checks = [
        _check_bpm(chart, audio),
        _check_duration(chart, audio),
        _check_offset(chart, audio),
        _check_tempo_changes(chart, audio),
        _check_drift(chart, audio),
    ]

    corrected = _corrected_offset(chart, audio)

    confidence = confidence_from_validation(checks)

    return TimingValidation(
        checks=checks,
        confidence=confidence,
        corrected_offset=corrected,
    )


def validate_chart_file(
    chart: TimingData,
    audio_path: Path,
) -> TimingValidation:
    """
    Validate a chart against an audio file on disk.

    Convenience wrapper around ``analyse_audio`` + ``validate_chart``
    used by the dataset pipeline.
    """

    return validate_chart(
        chart,
        analyse_audio(audio_path),
    )


def _check_bpm(
    chart: TimingData,
    audio: AudioMetrics,
) -> TimingCheck:
    chart_bpm = chart.tempos[0].bpm if chart.tempos else audio.bpm
    audio_bpm = audio.bpm

    # When the audio is not clearly periodic, we cannot say the chart is
    # wrong: do not penalise it.
    if audio.bpm_score < BPM_SCORE_FLOOR:
        return TimingCheck(
            name="bpm",
            ok=True,
            detail=(
                f"audio tempo unreliable ({audio.bpm_score:.0%})"
            ),
        )

    if _bpm_matches(chart_bpm, audio_bpm):
        return TimingCheck(
            name="bpm",
            ok=True,
            detail=f"{audio_bpm:.0f} BPM",
        )

    # Half/double-time may still match; use a looser tolerance because
    # resolving the correct octave from the audio is noisy.
    for factor in (0.5, 2.0):
        if _bpm_matches(
            chart_bpm,
            audio_bpm * factor,
            tolerance=BPM_HALF_DOUBLE_TOLERANCE_RATIO,
        ):
            return TimingCheck(
                name="bpm",
                ok=True,
                detail=(
                    f"chart {chart_bpm:.0f} vs audio "
                    f"{audio_bpm:.0f} BPM (half/double time)"
                ),
            )

    # The audio estimate may pick a sub-harmonic; accept when the chart
    # BPM matches any strong tempo candidate.
    for candidate_bpm, score in audio.tempo_candidates:
        if score < BPM_SCORE_FLOOR:
            continue

        if _bpm_matches(chart_bpm, candidate_bpm):
            return TimingCheck(
                name="bpm",
                ok=True,
                detail=(
                    f"chart {chart_bpm:.0f} matches audio candidate "
                    f"{candidate_bpm:.0f} BPM"
                ),
            )

        for factor in (0.5, 2.0):
            if _bpm_matches(
                chart_bpm,
                candidate_bpm * factor,
                tolerance=BPM_HALF_DOUBLE_TOLERANCE_RATIO,
            ):
                return TimingCheck(
                    name="bpm",
                    ok=True,
                    detail=(
                        f"chart {chart_bpm:.0f} matches audio candidate "
                        f"{candidate_bpm:.0f} BPM (half/double time)"
                    ),
                )

    return TimingCheck(
        name="bpm",
        ok=False,
        warn=True,
        detail=(
            f"chart {chart_bpm:.0f} vs audio {audio_bpm:.0f} BPM"
        ),
    )


def _check_duration(
    chart: TimingData,
    audio: AudioMetrics,
) -> TimingCheck:
    chart_duration = (
        chart.beats[-1].time
        if chart.beats
        else 0.0
    )

    diff = abs(
        chart_duration - audio.duration,
    )

    if diff <= DURATION_TOLERANCE_SECONDS:
        return TimingCheck(
            name="duration",
            ok=True,
            detail=f"{audio.duration:.1f} s",
        )

    return TimingCheck(
        name="duration",
        ok=False,
        warn=True,
        detail=(
            f"chart {chart_duration:.1f} vs audio "
            f"{audio.duration:.1f} s"
        ),
    )


def _check_offset(
    chart: TimingData,
    audio: AudioMetrics,
) -> TimingCheck:
    chart_offset = chart.offset
    diff_ms = (
        audio.offset - chart_offset
    ) * 1000.0

    if abs(diff_ms) <= OFFSET_TOLERANCE_MS:
        return TimingCheck(
            name="offset",
            ok=True,
            detail=f"{diff_ms:+.0f} ms",
        )

    return TimingCheck(
        name="offset",
        ok=False,
        warn=True,
        detail=f"{diff_ms:+.0f} ms",
    )


def _check_tempo_changes(
    chart: TimingData,
    audio: AudioMetrics,
) -> TimingCheck:
    """Compare the overall tempo variability of chart and audio.

    Counting tempo *changes* is unreliable: Harmonix charts carry
    recorded micro-variations and the audio tempo map carries estimator
    noise. Instead we compare the relative span of each tempo set, so a
    constant-tempo chart passes even when the audio estimator wanders a
    little, while a chart with a real tempo change still differs.
    """

    chart_span = _tempo_span(_tempo_pairs(chart.tempos))
    audio_span = _tempo_span(list(audio.tempo_map))

    if (
        abs(chart_span - audio_span)
        <= TEMPO_CHANGES_TOLERANCE
    ):
        return TimingCheck(
            name="tempo-changes",
            ok=True,
            detail=f"±{chart_span * 100:.0f}%",
        )

    return TimingCheck(
        name="tempo-changes",
        ok=False,
        warn=True,
        detail=(
            f"chart ±{chart_span * 100:.0f}% vs "
            f"audio ±{audio_span * 100:.0f}%"
        ),
    )


def _tempo_span(
    segments: list[tuple[float, float]],
) -> float:
    """Max relative deviation of the tempos from their mean."""

    if len(segments) < 2:
        return 0.0

    tempos = [bpm for _time, bpm in segments if bpm > 0]

    if not tempos:
        return 0.0

    mean = sum(tempos) / len(tempos)

    return max(
        abs(bpm - mean) / mean
        for bpm in tempos
    )


def _tempo_pairs(
    tempos: list[TempoSegment],
) -> list[tuple[float, float]]:
    """Normalise chart tempo segments to ``(time, bpm)`` pairs."""

    return [
        (segment.start_time, segment.bpm)
        for segment in tempos
    ]


def _check_drift(
    chart: TimingData,
    audio: AudioMetrics,
) -> TimingCheck:
    """Measure how well the chart beats align with the audio onsets.

    A chart from a different recording (or a recording with a large
    edit) will have poor onset coverage; the grid is then considered
    displaced even when BPM and duration match.
    """

    if not chart.beats or chart.tempos[0].bpm <= 0:
        return TimingCheck(
            name="drift",
            ok=True,
            detail="no beats",
        )

    coverage = _onset_coverage_at_beats(
        chart,
        audio,
    )

    if coverage >= DRIFT_COVERAGE_THRESHOLD:
        return TimingCheck(
            name="drift",
            ok=True,
            detail=f"{coverage:.0%} onset coverage",
        )

    return TimingCheck(
        name="drift",
        ok=False,
        warn=True,
        detail=f"{coverage:.0%} onset coverage",
    )


def _onset_coverage_at_beats(
    chart: TimingData,
    audio: AudioMetrics,
) -> float:
    """Fraction of chart beats near an audio onset.

    Uses a generous window (half a beat) so this is a coarse alignment
    check, not a beat-alignment metric.
    """

    beat_times = np.asarray(
        [beat.time for beat in chart.beats],
        dtype=float,
    )

    if beat_times.size == 0:
        return 0.0

    period = 60.0 / chart.tempos[0].bpm

    onset_frames = librosa.onset.onset_detect(
        onset_envelope=audio.onset_envelope,
        sr=audio.sr,
        backtrack=True,
        units="frames",
    )

    if onset_frames.size == 0:
        return 0.0

    onset_times = librosa.frames_to_time(
        onset_frames,
        sr=audio.sr,
    )

    window = max(period / 2.0, 0.05)

    positions = np.searchsorted(
        onset_times,
        beat_times,
    )

    covered = 0

    for index, beat in enumerate(
        beat_times,
    ):
        position = positions[index]

        closest = np.inf

        if position < onset_times.size:
            closest = min(
                closest,
                abs(
                    onset_times[position] - beat,
                ),
            )

        if position > 0:
            closest = min(
                closest,
                abs(
                    onset_times[position - 1] - beat,
                ),
            )

        if closest <= window:
            covered += 1

    return float(covered) / beat_times.size


def _corrected_offset(
    chart: TimingData,
    audio: AudioMetrics,
) -> float | None:
    """Propose the audio offset when the chart differs meaningfully."""

    diff_ms = (
        audio.offset - chart.offset
    ) * 1000.0

    if abs(diff_ms) > OFFSET_TOLERANCE_MS:
        return audio.offset

    return None


def _bpm_matches(
    a: float,
    b: float,
    *,
    tolerance: float = BPM_TOLERANCE_RATIO,
) -> bool:
    if b <= 0:
        return False

    return (
        abs(a - b) / b
        <= tolerance
    )


# --------------------------------------------------------------------------
# Confidence
# --------------------------------------------------------------------------

# Penalty applied per failed check.
BPM_PENALTY = 0.30
DURATION_PENALTY = 0.15
OFFSET_PENALTY = 0.15
TEMPO_CHANGES_PENALTY = 0.10
DRIFT_PENALTY = 0.30

_CHECK_PENALTY = {
    "bpm": BPM_PENALTY,
    "duration": DURATION_PENALTY,
    "offset": OFFSET_PENALTY,
    "tempo-changes": TEMPO_CHANGES_PENALTY,
    "drift": DRIFT_PENALTY,
}


def confidence_from_validation(
    checks: list[TimingCheck],
) -> float:
    """
    Derive a numeric confidence in ``[0, 1]`` from the validation checks.

    A perfect chart scores 1.0; each failed check subtracts its penalty.
    """

    confidence = 1.0

    for check in checks:
        if not check.ok:
            confidence -= _CHECK_PENALTY.get(
                check.name,
                0.10,
            )

    return float(
        max(
            0.0,
            min(1.0, confidence),
        ),
    )
