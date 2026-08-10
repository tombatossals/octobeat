from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

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
from octobeat.models.songmap import (
    LyricLine,
    Source,
)
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

LRCLIB_API = "https://lrclib.net/api"
LRCLIB_TIMEOUT = 8

LRC_TIMESTAMP = re.compile(
    r"\[(\d{1,2}):(\d{1,2})(?:\.(\d{1,3}))?\]"
)


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
        lyrics=_fetch_lrclib_lyrics(
            recording.artist or "",
            recording.title or "",
            duration,
        ),
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
        lyrics=_fetch_lrclib_lyrics(
            recording.artist or "",
            recording.title or "",
            audio.duration,
        ),
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
    )


def _fetch_lrclib_lyrics(
    artist: str,
    title: str,
    duration: float,
) -> list[LyricLine] | None:
    """
    Best-effort fetch of synced lyrics from LRCLIB.

    Returns ``None`` when the track is not found or on any failure,
    so analysis never fails because of missing lyrics.
    """

    if not artist or not title:
        return None

    params = urlencode(
        {
            "artist_name": artist,
            "track_name": title,
            "album_name": "",
            "duration": str(
                int(round(duration))
            ),
        }
    )

    try:
        with urlopen(
            f"{LRCLIB_API}/get?{params}",
            timeout=LRCLIB_TIMEOUT,
        ) as response:
            data = json.load(
                response
            )
    except Exception:
        data = None

    synced = (
        data.get("syncedLyrics")
        if data
        else None
    )

    if not synced:
        synced = _search_synced_lyrics(
            artist,
            title,
            duration,
        )

    if not synced:
        return None

    return _parse_lrc(synced)


def _search_synced_lyrics(
    artist: str,
    title: str,
    duration: float,
) -> str | None:
    """
    Fall back to the LRCLIB search endpoint and pick the closest
    non-instrumental match that has synced lyrics.
    """

    params = urlencode(
        {
            "artist_name": artist,
            "track_name": title,
        }
    )

    try:
        with urlopen(
            f"{LRCLIB_API}/search?{params}",
            timeout=LRCLIB_TIMEOUT,
        ) as response:
            results = json.load(
                response
            )
    except Exception:
        return None

    candidates = [
        result
        for result in results
        if result.get(
            "syncedLyrics"
        )
        and not result.get(
            "instrumental"
        )
    ]

    if not candidates:
        return None

    best = min(
        candidates,
        key=lambda result: abs(
            float(
                result.get(
                    "duration"
                ) or 0
            )
            - duration
        ),
    )

    synced = best.get(
        "syncedLyrics"
    )

    return (
        str(synced)
        if synced
        else None
    )


def _parse_lrc(lrc: str) -> list[LyricLine]:
    lines: list[LyricLine] = []

    for raw in lrc.splitlines():
        matches = list(
            LRC_TIMESTAMP.finditer(
                raw
            )
        )

        if not matches:
            continue

        text = LRC_TIMESTAMP.sub(
            "", raw
        ).strip()

        if not text:
            continue

        for match in matches:
            minutes = int(
                match.group(1)
            )
            seconds = int(
                match.group(2)
            )
            fraction = (
                int(
                    match.group(3).ljust(
                        3, "0"
                    )
                )
                / 1000
                if match.group(3)
                else 0.0
            )

            lines.append(
                LyricLine(
                    time=(
                        minutes * 60
                        + seconds
                        + fraction
                    ),
                    text=text,
                )
            )

    return sorted(
        lines,
        key=lambda line: line.time,
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