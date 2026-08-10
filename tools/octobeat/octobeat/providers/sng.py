from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import numpy as np

from octobeat.audio.decoder import decode_to_wav
from octobeat.models.recording import Recording
from octobeat.models.songmap import Source
from octobeat.providers.base import SourceProvider
from octobeat.timing.sng import (
    extract_audio,
    extract_cover,
    extract_stems,
    parse_sng_container,
)
from octobeat.ui import console


class SngSourceProvider(SourceProvider):
    """
    Source provider for SNG containers.

    Extracts the audio track and the chart from an SNG, decoding the
    audio to a temporary WAV for analysis. The chart path is attached to
    the Recording so the pipeline uses it as the timing source.
    """

    @classmethod
    def supports(cls, source: str) -> bool:
        return str(source).lower().endswith(".sng")

    def load(self, source: str) -> Recording:
        path = Path(source).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(path)

        data = path.read_bytes()

        sng = parse_sng_container(data)
        metadata = sng.metadata

        artist = metadata.get("artist")
        title = metadata.get("name")
        album = metadata.get("album")
        year = _parse_year(metadata.get("year"))
        genre = metadata.get("genre")

        # Multitrack containers ship the instrument stems; mix them into
        # the full mix. Otherwise fall back to the single audio track.
        stems = extract_stems(data)

        cleanup = tempfile.TemporaryDirectory(
            prefix="octobeat-sng-",
        )

        audio_path = Path(cleanup.name) / "song.wav"

        try:
            if stems:
                mix_stems_to_wav(
                    stems,
                    audio_path,
                )

                console.info(
                    "SNG is multitrack; mixed "
                    + f"{len(stems)} stems into the full mix.",
                )
            else:
                _name, audio_bytes = extract_audio(data)

                decode_to_wav_from_bytes(
                    audio_bytes,
                    audio_path,
                )
        except Exception:
            cleanup.cleanup()
            raise

        return Recording(
            path=audio_path,
            artist=artist,
            title=title,
            source=Source(
                type="file",
                id=str(path),
            ),
            cleanup_dir=cleanup,
            chart_path=path,
            album=album,
            year=year,
            genres=(
                [genre]
                if genre
                else None
            ),
            cover_bytes=extract_cover(data),
        )


def _parse_year(value: str | None) -> int | None:
    if not value:
        return None

    try:
        return int(value)
    except ValueError:
        return None


def decode_to_wav_from_bytes(
    audio_bytes: bytes,
    destination: Path,
) -> None:
    """
    Decode raw audio bytes (Opus/Ogg/MP3) to a PCM WAV file.
    """

    with tempfile.NamedTemporaryFile(
        suffix=".ogg",
        prefix="octobeat-sng-audio-",
        delete=False,
    ) as temp:
        temp.write(audio_bytes)
        temp_path = Path(temp.name)

    try:
        decode_to_wav(
            temp_path,
            destination,
        )
    finally:
        temp_path.unlink(missing_ok=True)


def mix_stems_to_wav(
    stems: list[tuple[str, bytes]],
    destination: Path,
) -> None:
    """
    Decode the instrument stems and sum them into a single mix WAV.

    Each stem is decoded to 48 kHz mono float32 PCM, then all of them are
    added together and peak-normalised so the full mix does not clip.
    """

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with tempfile.TemporaryDirectory(
        prefix="octobeat-mix-",
    ) as tmp:
        tmp_dir = Path(tmp)

        decoded: list[np.ndarray] = []

        for name, audio_bytes in stems:
            source = tmp_dir / f"{name}.ogg"
            source.write_bytes(audio_bytes)

            decoded.append(
                _decode_to_pcm(source),
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

        peak = float(np.max(np.abs(mix)))

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
