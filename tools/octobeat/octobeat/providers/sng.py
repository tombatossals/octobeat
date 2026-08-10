from __future__ import annotations

import tempfile
from pathlib import Path

from octobeat.audio.decoder import decode_to_wav
from octobeat.models.recording import Recording
from octobeat.models.songmap import Source
from octobeat.providers.base import SourceProvider
from octobeat.timing.sng import (
    extract_audio,
    parse_sng_container,
)


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

        # Extract the preferred audio track into a temporary wav.
        _name, audio_bytes = extract_audio(data)

        cleanup = tempfile.TemporaryDirectory(
            prefix="octobeat-sng-",
        )

        audio_path = Path(cleanup.name) / "song.wav"

        try:
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
        )


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
