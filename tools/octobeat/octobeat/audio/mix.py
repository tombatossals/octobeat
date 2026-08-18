from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import numpy as np


def mix_tracks_to_wav(
    tracks: list[tuple[str, bytes]],
    destination: Path,
) -> Path:
    """
    Decode the audio tracks and sum them into a single mix WAV.

    Each track is decoded to 48 kHz mono float32 PCM, then all of them
    are added together and peak-normalised so the mix does not clip.
    """

    destination = destination.expanduser().resolve()
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with tempfile.TemporaryDirectory(
        prefix="octobeat-mix-",
    ) as tmp:
        tmp_dir = Path(tmp)

        decoded: list[np.ndarray] = []

        for name, audio_bytes in tracks:
            source = tmp_dir / f"{name}.ogg"
            source.write_bytes(audio_bytes)

            decoded.append(
                _decode_to_pcm(source),
            )

        if not decoded:
            raise ValueError(
                "No audio tracks to mix.",
            )

        length = min(
            len(samples)
            for samples in decoded
        )

        mix = np.zeros(
            length,
            dtype=np.float32,
        )

        for samples in decoded:
            mix += samples[:length]

        peak = float(
            np.max(
                np.abs(mix),
            )
        )

        if peak > 0:
            mix = mix * (0.95 / peak)

        pcm_path = tmp_dir / "mix.f32"

        pcm_path.write_bytes(
            mix.astype(
                np.float32,
            ).tobytes(),
        )

        _write_pcm_to_wav(
            pcm_path,
            destination,
        )

    return destination


def _decode_to_pcm(path: Path) -> np.ndarray:
    """Decode an audio file to 48 kHz mono float32 samples."""

    result = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "48000",
            "-c:a",
            "pcm_f32le",
            "-f",
            "f32le",
            "pipe:1",
        ],
        check=True,
        capture_output=True,
    )

    return np.frombuffer(
        result.stdout,
        dtype=np.float32,
    )


def _write_pcm_to_wav(
    pcm_path: Path,
    destination: Path,
) -> None:
    """Wrap raw float32 PCM in a 48 kHz mono float32 WAV."""

    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "f32le",
            "-ar",
            "48000",
            "-ac",
            "1",
            "-i",
            str(pcm_path),
            "-c:a",
            "pcm_f32le",
            str(destination),
        ],
        check=True,
    )
