"""Synthetic video-sync fixtures.

Generates reference audio and corresponding "video audio" pairs with a
known ground truth offset, covering the sync scenarios: exact match,
intro, silent intro, compressed, different volume, mismatch, no-audio.
"""

from __future__ import annotations

import json
import wave
from dataclasses import asdict, dataclass
from io import BytesIO
from pathlib import Path

import numpy as np

SR = 22050
DURATION = 6.0

CASE_NAMES = [
    "exact-match",
    "intro",
    "silent-intro",
    "compressed",
    "different-volume",
    "offset",
    "count-in",
    "mismatch",
    "no-audio",
]


@dataclass(frozen=True, slots=True)
class VideoSyncFixture:
    """Ground truth of one video-sync fixture."""

    name: str

    offset: float | None

    # Minimum expected confidence for a valid match; for mismatches this
    # is a maximum (the detection must NOT trust it).
    confidence_floor: float

    @property
    def is_match(self) -> bool:
        return self.offset is not None


def build_video_sync_fixtures(output: Path) -> list[VideoSyncFixture]:
    """Generate all fixtures and a manifest into ``output``."""

    output.mkdir(parents=True, exist_ok=True)

    fixtures = [
        _exact_match(),
        _intro(),
        _silent_intro(),
        _compressed(),
        _different_volume(),
        _offset(),
        _count_in(),
        _mismatch(),
        _no_audio(),
    ]

    manifest = []

    for fixture in fixtures:
        _build_case(output / fixture.name, fixture)
        manifest.append(asdict(fixture))

    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    return fixtures


def _build_case(directory: Path, fixture: VideoSyncFixture) -> None:
    directory.mkdir(parents=True, exist_ok=True)

    song = _make_song(
        DURATION,
        seed=42,
        harmonics=(220, 330, 440, 550),
        beat_interval=0.5,
    )

    offset = fixture.offset or 0.0

    if fixture.name == "count-in":
        # The reference starts with a 2 s stick-click count-in that the
        # video does not have: the video is just the song.
        lead_in = 2.0
        reference_sig = np.concatenate(
            [
                _make_clicks(lead_in),
                song,
            ]
        )
        video_sig = song
    elif fixture.name == "mismatch":
        reference_sig = song
        video_sig = _make_song(
            DURATION,
            seed=7,
            harmonics=(300, 600, 900),
            beat_interval=0.35,
        )
    elif fixture.name == "no-audio":
        reference_sig = song
        video_sig = np.zeros_like(song)
    else:
        reference_sig = song
        video_sig = np.concatenate(
            [
                np.zeros(int(SR * offset)),
                song,
            ]
        )

    if fixture.name == "compressed":
        video_sig = np.clip(video_sig, -0.3, 0.3)

    if fixture.name == "different-volume":
        video_sig = video_sig * 0.15

    if fixture.name == "silent-intro":
        video_sig[: int(SR * offset)] = 0.0

    _write_wav(directory / "reference.wav", reference_sig)
    _write_wav(directory / "video.wav", video_sig)


def _make_clicks(duration: float) -> np.ndarray:
    """Sparse stick-click lead-in (brief clicks, silence between them)."""

    n = int(SR * duration)
    signal = np.zeros(n)

    for beat in np.arange(0, duration, 0.5):
        start = int(beat * SR)
        if start < n:
            signal[start : start + int(0.01 * SR)] = 0.6

    return np.asarray(signal, dtype=np.float32)


def _make_song(
    duration: float,
    *,
    seed: int,
    harmonics: tuple[float, ...],
    beat_interval: float,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(SR * duration)
    t = np.arange(n) / SR

    signal = np.zeros(n)

    for frequency in harmonics:
        signal += np.sin(
            2 * np.pi * frequency * t + rng.uniform(0, 2 * np.pi)
        )

    for beat in np.arange(0, duration, beat_interval):
        start = int(beat * SR)
        if start < n:
            signal[start : start + int(0.02 * SR)] += 2.0

    peak = float(np.max(np.abs(signal)))

    return np.asarray(
        signal / peak * 0.5,
        dtype=np.float32,
    )


def _write_wav(path: Path, signal: np.ndarray) -> None:
    pcm = (signal * 32767).astype(np.int16)

    buffer = BytesIO()

    with wave.open(buffer, "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(SR)
        file.writeframes(pcm.tobytes())

    path.write_bytes(buffer.getvalue())


def _exact_match() -> VideoSyncFixture:
    return VideoSyncFixture(
        name="exact-match",
        offset=0.0,
        confidence_floor=0.90,
    )


def _intro() -> VideoSyncFixture:
    return VideoSyncFixture(
        name="intro",
        offset=2.0,
        confidence_floor=0.90,
    )


def _silent_intro() -> VideoSyncFixture:
    return VideoSyncFixture(
        name="silent-intro",
        offset=3.0,
        confidence_floor=0.90,
    )


def _compressed() -> VideoSyncFixture:
    return VideoSyncFixture(
        name="compressed",
        offset=2.0,
        confidence_floor=0.60,
    )


def _different_volume() -> VideoSyncFixture:
    return VideoSyncFixture(
        name="different-volume",
        offset=2.0,
        confidence_floor=0.90,
    )


def _offset() -> VideoSyncFixture:
    return VideoSyncFixture(
        name="offset",
        offset=1.5,
        confidence_floor=0.90,
    )


def _count_in() -> VideoSyncFixture:
    # Reference has a 2 s count-in the video lacks; the video offset is
    # therefore negative (the video waits at its first frame).
    return VideoSyncFixture(
        name="count-in",
        offset=-2.0,
        confidence_floor=0.90,
    )


def _mismatch() -> VideoSyncFixture:
    # Not a match: confidence must stay below the "auto" threshold.
    return VideoSyncFixture(
        name="mismatch",
        offset=None,
        confidence_floor=0.90,
    )


def _no_audio() -> VideoSyncFixture:
    return VideoSyncFixture(
        name="no-audio",
        offset=None,
        confidence_floor=0.90,
    )
