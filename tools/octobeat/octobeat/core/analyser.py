from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from urllib.parse import urlencode
from urllib.request import urlopen

import librosa
import numpy as np

from octobeat.cache.audio import AudioCache
from octobeat.core.grid import build_beat_grid
from octobeat.core.onset import compute_onset_envelope
from octobeat.core.phase import estimate_phase
from octobeat.core.tempo import estimate_tempo
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
    LyricLine,
    SongMap,
    SongMetadata,
    Source,
    Timing,
)
from octobeat.version import __version__

DEFAULT_TIME_SIGNATURE = "4/4"
BEATS_PER_BAR = 4

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

    bpm = estimate_tempo(
        onset_envelope,
        sr,
    )

    if bpm <= 0 and duration > 0:
        bpm = 120.0

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
    )

    if (
        len(beat_times) == 0
        and duration > 0
    ):
        beat_times = _fallback_grid(
            duration,
            bpm,
        )

    confidence = _estimate_confidence(
        onset_envelope,
        beat_times,
        sr,
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
        Beat(
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

    songmap = SongMap(
        version=SONGMAP_VERSION,
        schema=SCHEMA_ID,
        generatedBy=f"octobeat {__version__}",
        createdAt=datetime.now(
            UTC,
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
            offset=round(music_start, 3),
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
                confidence,
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
                    "duration", 0
                )
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


def _estimate_confidence(
    onset_envelope: np.ndarray,
    beat_times: np.ndarray,
    sr: int,
) -> float:
    if len(beat_times) == 0:
        return 0.0

    if len(onset_envelope) == 0:
        return 0.0

    beat_frames = librosa.time_to_frames(
        beat_times,
        sr=sr,
    )

    peak_energy = float(
        np.percentile(
            onset_envelope,
            95,
        ),
    )

    if peak_energy <= 0:
        return 0.0

    # Sample the maximum onset energy in a small window around each
    # beat: onset detection backtracks to the start of the attack,
    # where the envelope may still be near zero.
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
            continue

        energies.append(
            float(
                np.max(
                    onset_envelope[low:high],
                ),
            ),
        )

    if not energies:
        return 0.0

    beat_energy = float(
        np.mean(energies),
    )

    return max(
        0.0,
        min(
            1.0,
            beat_energy / peak_energy,
        ),
    )