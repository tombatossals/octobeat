from __future__ import annotations

from datetime import datetime, timezone

import librosa
import numpy as np

from octobeat.cache.audio import AudioCache
from octobeat.models.analysis import (
    AnalysisReport,
    AnalysisResult,
)
from octobeat.models.recording import Recording
from octobeat.models.songmap import (
    SCHEMA_ID,
    SONGMAP_VERSION,
    Bar,
    Beat,
    SongMap,
    SongMetadata,
    Source,
    Timing,
)
from octobeat.version import __version__

DEFAULT_TIME_SIGNATURE = "4/4"
BEATS_PER_BAR = 4


def analyse_recording(
    recording: Recording,
    *,
    provider: str,
    source: str,
) -> AnalysisResult:
    """
    Analyse a recording and generate a SongMap plus a display report.
    """

    if not recording.path.exists():
        raise FileNotFoundError(recording.path)

    cache = AudioCache()

    wav = cache.decoded(recording)

    y, sr = librosa.load(
        wav,
        sr=None,
        mono=False,
    )

    duration = float(
        librosa.get_duration(
            y=y,
            sr=sr,
        ),
    )

    onset_envelope = librosa.onset.onset_strength(
        y=y,
        sr=sr,
    )

    tempo_value, beat_frames = librosa.beat.beat_track(
        y=y,
        sr=sr,
        onset_envelope=onset_envelope,
        units="frames",
        trim=False,
    )

    bpm = _as_float(tempo_value)

    beat_times = librosa.frames_to_time(
        beat_frames,
        sr=sr,
    )

    if (
        len(beat_times) == 0
        and duration > 0
        and bpm > 0
    ):
        beat_times = _fallback_grid(
            duration,
            bpm,
        )

    confidence = _estimate_confidence(
        onset_envelope,
        beat_frames,
    )

    offset = (
        float(beat_times[0])
        if len(beat_times)
        else 0.0
    )

    beats = [
        Beat(
            index=index,
            time=round(float(time), 3),
        )
        for index, time in enumerate(
            beat_times,
            start=1,
        )
        if 0 <= float(time) <= duration
    ]

    songmap = SongMap(
        version=SONGMAP_VERSION,
        schema=SCHEMA_ID,
        generatedBy=f"octobeat {__version__}",
        createdAt=datetime.now(
            timezone.utc,
        ).isoformat(),
        metadata=SongMetadata(
            title=recording.title
            or recording.path.stem,
            duration=round(
                duration,
                3,
            ),
            source=recording.source
            or Source(
                type="file",
                id=str(
                    recording.path.resolve(),
                ),
            ),
        ),
        timing=Timing(
            bpm=round(bpm, 2),
            offset=round(offset, 3),
            timeSignature=DEFAULT_TIME_SIGNATURE,
            confidence=round(
                confidence,
                2,
            ),
        ),
        beats=beats,
        bars=_build_bars(
            len(beats),
            BEATS_PER_BAR,
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
                confidence,
                2,
            ),
        ),
    )


def _build_bars(
    n_beats: int,
    beats_per_bar: int,
) -> list[Bar]:
    n_bars = (
        n_beats
        + beats_per_bar
        - 1
    ) // beats_per_bar

    return [
        Bar(
            index=bar_index,
            firstBeat=(
                (bar_index - 1)
                * beats_per_bar
                + 1
            ),
        )
        for bar_index in range(
            1,
            n_bars + 1,
        )
    ]


def _as_float(
    value: object,
) -> float:
    array = np.asarray(value)

    if array.size == 0:
        return 0.0

    return float(
        array.reshape(-1)[0],
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


def _estimate_confidence(
    onset_envelope: np.ndarray,
    beat_frames: np.ndarray,
) -> float:
    if len(beat_frames) == 0:
        return 0.0

    if len(onset_envelope) == 0:
        return 0.0

    clipped_frames = beat_frames[
        (beat_frames >= 0)
        & (beat_frames < len(onset_envelope))
    ]

    if len(clipped_frames) == 0:
        return 0.0

    beat_energy = float(
        np.mean(
            onset_envelope[
                clipped_frames
            ],
        ),
    )

    peak_energy = float(
        np.percentile(
            onset_envelope,
            95,
        ),
    )

    if peak_energy <= 0:
        return 0.0

    return max(
        0.0,
        min(
            1.0,
            beat_energy / peak_energy,
        ),
    )