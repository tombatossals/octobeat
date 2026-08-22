from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import librosa
import numpy as np

from octobeat.cache.audio import AudioCache
from octobeat.core.bars import detect_downbeat_shift
from octobeat.core.confidence import analyse_confidence
from octobeat.core.grid import build_beat_grid
from octobeat.core.onset import compute_onset_envelope
from octobeat.core.phase import estimate_phase
from octobeat.core.songmap_builder import build_songmap
from octobeat.core.tempo import (
    estimate_tempo,
    estimate_tempo_candidates,
    estimate_tempo_map,
    score_tempo,
)
from octobeat.models.analysis import (
    AnalysisReport,
    AnalysisResult,
)
from octobeat.models.recording import Recording
from octobeat.models.songmap import Source
from octobeat.models.timing import (
    Beat as TimingBeat,
)
from octobeat.models.timing import (
    TempoSegment as TimingTempoSegment,
)
from octobeat.models.timing import (
    TimeSignature,
    TimingData,
)
from octobeat.version import __version__

DEFAULT_TIME_SIGNATURE = "4/4"
BEATS_PER_BAR = 4

AUDIO_SOURCE_KIND = "audio-analysis"


def analyse_recording(
    recording: Recording,
    *,
    provider: str,
    source: str,
    offset: float | None = None,
) -> AnalysisResult:
    """
    Analyse a recording and generate a SongMap plus a display report.

    ``offset`` overrides the detected music start (seconds into the
    media where the actual song begins). When omitted, the start is
    estimated from the onset envelope.
    """

    if not recording.path.exists():
        raise FileNotFoundError(recording.path)

    cache = AudioCache()

    wav = cache.decoded(recording)

    y, sr_raw = librosa.load(
        wav,
        sr=None,
        mono=False,
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

    if _is_silence(
        onset_envelope,
    ):
        return _silence_result(
            recording,
            wav,
            duration,
            provider,
            source,
        )

    bpm = estimate_tempo(
        onset_envelope,
        sr,
    )

    if bpm <= 0 and duration > 0:
        bpm = 120.0

    tempo_map = estimate_tempo_map(
        onset_envelope,
        sr,
        global_bpm=bpm,
    )

    phase = estimate_phase(
        onset_envelope,
        sr,
        bpm,
    )

    beat_times = build_beat_grid(
        onset_envelope,
        sr,
        bpm,
        phase,
        duration,
        tempo_map=tempo_map,
    )

    if (
        len(beat_times) == 0
        and duration > 0
    ):
        beat_times = _fallback_grid(
            duration,
            bpm,
        )

    confidence = analyse_confidence(
        onset_envelope,
        sr,
        bpm,
        beat_times,
    )

    tempo_candidates = _score_candidates(
        onset_envelope,
        sr,
        bpm,
    )

    music_start = (
        float(offset)
        if offset is not None
        else _detect_music_start(
            onset_envelope,
            sr,
        )
    )

    music_start = max(
        0.0,
        min(
            music_start,
            duration,
        ),
    )

    beats = [
        TimingBeat(
            index=index,
            time=round(float(time), 3),
        )
        for index, time in enumerate(
            beat_times,
            start=1,
        )
        if 0 <= float(time) <= duration
        and float(time) >= music_start
    ]

    beat_times_for_bars = [
        beat.time
        for beat in beats
    ]

    downbeat_shift = detect_downbeat_shift(
        onset_envelope,
        sr,
        np.asarray(
            beat_times_for_bars,
        ),
        BEATS_PER_BAR,
    )

    timing_data = TimingData(
        tempos=_tempo_segments(
            tempo_map,
            beats,
        ),
        beats=beats,
        time_signatures=[
            _time_signature_at(
                start_beat=1,
            ),
        ],
        sections=[],
    )

    songmap = build_songmap(
        timing_data,
        title=recording.title
        or recording.path.stem,
        artist=recording.artist,
        duration=duration,
        source=recording.source
        or Source(
            type="file",
            id=str(
                recording.path.resolve(),
            ),
        ),
        source_kind=AUDIO_SOURCE_KIND,
        generated_by=f"octobeat {__version__}",
        created_at=datetime.now(
            UTC,
        ).isoformat(),
        offset=music_start,
        confidence=confidence.overall,
        downbeat_shift=downbeat_shift,
    )

    return AnalysisResult(
        songmap=songmap,
        report=AnalysisReport(
            provider=provider,
            source=source,
            recording=recording.path,
            decoded=wav,
            duration=round(
                duration,
                3,
            ),
            bpm=round(bpm, 2),
            beats=len(beats),
            confidence=round(
                confidence.overall,
                2,
            ),
            tempo_confidence=round(
                confidence.tempo,
                2,
            ),
            beat_confidence=round(
                confidence.beat,
                2,
            ),
            grid_stability=round(
                confidence.grid,
                2,
            ),
            tempo_candidates=tempo_candidates,
            tempo_map=tempo_map,
            phase=round(phase, 3),
            beat_interval=round(
                60.0 / bpm,
                3,
            ),
            downbeat_shift=downbeat_shift,
        ),
    )


def _tempo_segments(
    tempo_map: list[tuple[float, float]],
    beats: list[TimingBeat],
) -> list[TimingTempoSegment]:
    """Map audio tempo-map segments to canonical TimingData segments.

    Each segment's ``start_beat`` is the first detected beat at or after
    its start time.
    """

    beat_times = [beat.time for beat in beats]
    segments: list[TimingTempoSegment] = []

    for start, bpm_value in tempo_map:
        start_beat = _first_beat_after(beat_times, start)

        segments.append(
            TimingTempoSegment(
                start_beat=start_beat,
                start_time=round(start, 3),
                bpm=round(bpm_value, 2),
            ),
        )

    return segments


def _first_beat_after(
    beat_times: list[float],
    time: float,
) -> int:
    for index, beat_time in enumerate(beat_times, start=1):
        if beat_time >= time:
            return index
    return len(beat_times) if beat_times else 1


def _time_signature_at(
    start_beat: int,
    *,
    numerator: int = 4,
    denominator: int = 4,
) -> TimeSignature:
    """Build a canonical time signature (default 4/4)."""

    return TimeSignature(
        start_beat=start_beat,
        numerator=numerator,
        denominator=denominator,
    )


def analyse_with_chart(
    recording: Recording,
    chart_timing: TimingData,
    *,
    provider: str,
    source: str,
    chart_source: str = "sng",
) -> AnalysisResult:
    """
    Build a SongMap from a structured chart, validated against the audio.

    The chart provides the timing; the audio is used as a validator
    (offset, duration, BPM, tempo changes, drift). The chart's own
    offset is kept as the SongMap offset: the chart defines the musical
    structure, and re-writing its offset from audio analysis would
    desynchronise the beats. The validation confidence reflects how
    well the chart matches the audio.
    """

    from octobeat.validation.timing import (
        analyse_audio,
        validate_chart,
    )

    if not recording.path.exists():
        raise FileNotFoundError(recording.path)

    audio = analyse_audio(recording.path)

    validation = validate_chart(
        chart_timing,
        audio,
    )

    songmap = build_songmap(
        chart_timing,
        title=recording.title
        or recording.path.stem,
        artist=recording.artist,
        duration=audio.duration,
        source=recording.source
        or Source(
            type="file",
            id=str(
                recording.path.resolve(),
            ),
        ),
        source_kind=chart_source,
        generated_by=f"octobeat {__version__}",
        created_at=datetime.now(
            UTC,
        ).isoformat(),
        offset=chart_timing.offset,
        confidence=validation.confidence,
        count_in_start=recording.count_in_start,
        song_start=recording.song_start,
        count_in_clicks=recording.count_in_clicks,
    )

    return AnalysisResult(
        songmap=songmap,
        report=AnalysisReport(
            provider=provider,
            source=source,
            recording=recording.path,
            decoded=recording.path,
            duration=round(audio.duration, 3),
            bpm=round(audio.bpm, 2),
            beats=len(chart_timing.beats),
            confidence=round(
                validation.confidence,
                2,
            ),
        ),
        lyrics=chart_timing.lyrics,
    )


def _fallback_grid(
    duration: float,
    bpm: float,
) -> np.ndarray:
    interval = 60.0 / bpm

    return np.arange(
        0.0,
        duration,
        interval,
    )


def _score_candidates(
    onset_envelope: np.ndarray,
    sr: int,
    bpm: float,
) -> list[tuple[float, float]]:
    """Tempo candidates with their scores, for diagnostics."""

    candidates = set(
        estimate_tempo_candidates(
            onset_envelope,
            sr,
        ),
    )

    for factor in (0.5, 1.0, 2.0):
        candidates.add(
            bpm * factor,
        )

    scored = []

    for candidate in sorted(
        candidates,
    ):
        if candidate <= 0:
            continue

        scored.append(
            (
                round(candidate, 2),
                round(
                    score_tempo(
                        onset_envelope,
                        sr,
                        candidate,
                    ),
                    3,
                ),
            )
        )

    return scored


def _is_silence(
    onset_envelope: np.ndarray,
    *,
    peak_ratio: float = 0.02,
) -> bool:
    """True when there is no meaningful onset energy."""

    if onset_envelope.size == 0:
        return True

    return float(
        np.max(onset_envelope),
    ) < peak_ratio


def _silence_result(
    recording: Recording,
    wav: Path,
    duration: float,
    provider: str,
    source: str,
) -> AnalysisResult:
    """Build a SongMap for a silent recording (no beats)."""

    songmap = build_songmap(
        TimingData(
            tempos=[],
            beats=[],
            time_signatures=[],
            sections=[],
        ),
        title=recording.title
        or recording.path.stem,
        artist=recording.artist,
        duration=duration,
        source=recording.source
        or Source(
            type="file",
            id=str(
                recording.path.resolve(),
            ),
        ),
        source_kind=AUDIO_SOURCE_KIND,
        generated_by=f"octobeat {__version__}",
        created_at=datetime.now(
            UTC,
        ).isoformat(),
        confidence=0.0,
    )

    return AnalysisResult(
        songmap=songmap,
        report=AnalysisReport(
            provider=provider,
            source=source,
            recording=recording.path,
            decoded=wav,
            duration=round(
                duration,
                3,
            ),
            bpm=0.0,
            beats=0,
            confidence=0.0,
        ),
    )


def _detect_music_start(
    onset_envelope: np.ndarray,
    sr: int,
    *,
    min_sustain_frames: int = 6,
) -> float:
    """
    Estimate the time where the actual music begins.

    Locates the first sustained burst of onset energy above a
    relative threshold, which tolerates quiet intros or a brief
    count-in before the song really kicks in.
    """

    if onset_envelope.size == 0:
        return 0.0

    peak = float(
        np.percentile(
            onset_envelope,
            95,
        )
    )

    if peak <= 0:
        return 0.0

    threshold = peak * 0.2

    run = 0
    start = 0
    sustained = False

    for frame, energy in enumerate(
        onset_envelope
    ):
        if energy >= threshold:
            if run == 0:
                start = frame
            run += 1

            if run >= min_sustain_frames:
                sustained = True
                break
        else:
            run = 0

    if not sustained:
        return 0.0

    return float(
        librosa.frames_to_time(
            start,
            sr=sr,
        )
    )


def detect_music_lead_in(
    audio_path: Path,
) -> tuple[float, float]:
    """
    Detect the count-in and the song start in an audio file.

    Returns ``(count_in_start, song_start)`` seconds into the audio:
    ``count_in_start`` is the first audible content (typically the first
    stick click of a Rock Band count-in) and ``song_start`` is where the
    music truly kicks in — the first sustained burst of energy after any
    quiet count-in. The thresholds are relative to the quiet tail of the
    signal so that faint stick-click count-ins (and quiet intros) are
    still detected; the clicks themselves are transient and never form a
    sustained run, so they do not count as the band entry.
    """

    y, sr_raw = librosa.load(
        str(audio_path),
        sr=None,
        mono=True,
    )

    sr = int(sr_raw)

    # 50 ms non-overlapping windows.
    hop = sr // 20

    rms = librosa.feature.rms(
        y=y,
        frame_length=hop,
        hop_length=hop,
    )[0]

    if rms.size == 0:
        return 0.0, 0.0

    times = librosa.frames_to_time(
        np.arange(rms.size),
        sr=sr,
        hop_length=hop,
    )

    peak = float(
        np.percentile(rms, 98),
    )

    # Low threshold (2% of the 98th percentile) so quiet count-in clicks
    # buried under the mix are still caught as the first audible content.
    count_threshold = max(
        0.002,
        peak * 0.02,
    )

    first_audible = np.flatnonzero(
        rms >= count_threshold,
    )

    count_in_start = (
        float(
            times[
                first_audible[0]
            ]
        )
        if first_audible.size
        else 0.0
    )

    # The count-in clicks are brief transients with silence between them;
    # the band keeps a sustained run of frames above the threshold. The
    # first sustained run after the clicks is the song start.
    sustain = 4
    run = 0
    song_start = 0.0

    for index, energy in enumerate(
        rms
    ):
        if energy >= count_threshold:
            run += 1
            if run >= sustain:
                song_start = float(
                    times[
                        index - sustain + 1
                    ]
                )
                break
        else:
            run = 0

    return (
        round(count_in_start, 3),
        round(
            max(count_in_start, song_start),
            3,
        ),
    )


def detect_count_in_clicks(
    audio_path: Path,
    *,
    limit: float,
) -> list[float]:
    """
    Detect the stick-click count-in transients before ``limit`` seconds.

    Returns the onset times (seconds into the audio) of the count-in
    clicks, in chronological order, or an empty list when the file has
    no discernible click lead-in. ``limit`` bounds the search to the
    lead-in region so the song's own onsets are not mistaken for clicks.
    """

    y, sr_raw = librosa.load(
        str(audio_path),
        sr=None,
        mono=True,
    )

    sr = int(sr_raw)

    hop = 512

    envelope = librosa.onset.onset_strength(
        y=y,
        sr=sr,
        hop_length=hop,
    )

    times = librosa.frames_to_time(
        np.arange(envelope.size),
        sr=sr,
        hop_length=hop,
    )

    peak = float(np.max(envelope))

    if peak <= 0:
        return []

    threshold = peak * 0.05

    clicks: list[float] = []

    for index in range(1, envelope.size - 1):
        time = float(times[index])

        if time >= limit:
            break

        if (
            envelope[index] >= threshold
            and envelope[index]
            >= envelope[index - 1]
            and envelope[index]
            > envelope[index + 1]
        ):
            # A single click can ring into several adjacent onset frames;
            # keep one hit per click.
            if (
                not clicks
                or time - clicks[-1]
                > 0.1
            ):
                clicks.append(
                    round(time, 3),
                )

    return clicks