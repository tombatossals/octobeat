from __future__ import annotations

import tempfile
import wave
from pathlib import Path

import librosa
import numpy as np

from octobeat.audio.decoder import encode_to_mp3
from octobeat.models.songmap import SongMap

# Synthesis constants for the click track.
DEFAULT_SAMPLE_RATE = 48000

# Regular beat click.
BEAT_FREQUENCY = 2200.0
BEAT_VOLUME = 0.35

# Downbeat accent (first beat of each bar).
ACCENT_FREQUENCY = 1100.0
ACCENT_VOLUME = 0.65

# Click length and envelope decay.
CLICK_DURATION = 0.06
CLICK_DECAY = 120.0


def mix_click_track(
    audio_path: Path,
    output_path: Path,
    songmap: SongMap,
    *,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    beat_volume: float = BEAT_VOLUME,
    accent_volume: float = ACCENT_VOLUME,
    volume: float = 1.0,
) -> Path:
    """
    Overlay a metronome click track on the recording and encode the
    result to MP3.

    Every beat of the SongMap gets a short click; the downbeat (first
    beat of each bar) gets a louder, lower-pitched accent so the bar
    structure is audible. The original recording keeps its full level
    and the clicks are added on top, making the track suitable for
    practicing an instrument by ear.

    ``volume`` scales both the beat and accent click levels
    (``1.0`` is the default; ``2.0`` makes the clicks twice as loud).
    """

    audio, _ = librosa.load(
        str(audio_path),
        sr=sample_rate,
        mono=True,
    )

    if audio.size == 0:
        raise ValueError(
            "Recording is empty.",
        )

    peak = float(
        np.max(
            np.abs(audio),
        ),
    )

    if peak > 0.0:
        audio = audio / peak

    beat_volume = beat_volume * volume
    accent_volume = accent_volume * volume

    clicks = np.zeros_like(audio)

    downbeats = {
        bar.firstBeat
        for bar in songmap.bars
    }

    for beat in songmap.beats:
        start = int(
            beat.time * sample_rate,
        )

        if start >= clicks.size:
            continue

        if beat.index in downbeats:
            click = _click(
                sample_rate,
                frequency=ACCENT_FREQUENCY,
                amplitude=accent_volume,
            )
        else:
            click = _click(
                sample_rate,
                frequency=BEAT_FREQUENCY,
                amplitude=beat_volume,
            )

        end = start + click.size

        if end > clicks.size:
            click = click[: clicks.size - start]
            end = clicks.size

        clicks[start:end] += click

    mixed = np.clip(
        audio + clicks,
        -1.0,
        1.0,
    )

    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with tempfile.TemporaryDirectory(
        prefix="octobeat-metronome-",
    ) as tmp:
        mixed_wav = Path(tmp) / "mixed.wav"

        _write_wav_int16(
            mixed_wav,
            mixed,
            sample_rate,
        )

        encode_to_mp3(
            mixed_wav,
            output_path,
        )

    return output_path


def _click(
    sample_rate: int,
    *,
    frequency: float,
    amplitude: float,
    duration: float = CLICK_DURATION,
    decay: float = CLICK_DECAY,
) -> np.ndarray:
    """Synthesize a short, fast-decaying sine click."""

    samples = int(
        sample_rate * duration,
    )

    time = (
        np.arange(samples)
        / sample_rate
    )

    envelope = np.exp(
        -time * decay,
    )

    return (
        amplitude
        * np.sin(
            2.0
            * np.pi
            * frequency
            * time
        )
        * envelope
    )


def _write_wav_int16(
    path: Path,
    data: np.ndarray,
    sample_rate: int,
) -> None:
    """Write a mono int16 PCM WAV from a float array in [-1, 1]."""

    pcm = (
        np.clip(
            data,
            -1.0,
            1.0,
        )
        * 32767.0
    ).astype(
        np.int16,
    )

    with wave.open(
        str(path),
        "wb",
    ) as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(sample_rate)
        file.writeframes(
            pcm.tobytes(),
        )
