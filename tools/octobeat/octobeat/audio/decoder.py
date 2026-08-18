import shutil
import subprocess
import tempfile
from pathlib import Path


def decode_to_wav(
    input_path: Path,
    output_path: Path,
) -> None:
    """
    Decode an audio file to a
    48 kHz mono float32 WAV.
    """

    if not input_path.exists():
        raise FileNotFoundError(input_path)

    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg not found in PATH.",
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(input_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "48000",
            "-c:a",
            "pcm_f32le",
            str(output_path),
        ],
        check=True,
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
        prefix="octobeat-audio-",
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


def encode_to_mp3(
    input_path: Path,
    output_path: Path,
    *,
    bitrate: str = "192k",
) -> None:
    """
    Encode an audio file to an MP3 suitable for streaming.
    """

    if not input_path.exists():
        raise FileNotFoundError(input_path)

    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg not found in PATH.",
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(input_path),
            "-vn",
            "-c:a",
            "libmp3lame",
            "-b:a",
            bitrate,
            str(output_path),
        ],
        check=True,
    )