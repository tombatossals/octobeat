"""Video synchronization.

Detects where a song starts inside an external video by comparing the
video's audio track against the reference audio the SongMap was built
from. The result is a ``videoOffset`` used as:

    videoTime = songTime + videoOffset

The engine works on robust spectral features (mel spectrogram), not raw
waveforms, so it tolerates compression, volume, EQ and mix differences.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import librosa
import numpy as np

from octobeat.audio.decoder import decode_to_wav

# Feature extraction parameters.
SR = 22050
N_MELS = 64
N_FFT = 2048
HOP_LENGTH = 512

# Feature column duration (seconds).
FEATURE_SECONDS = HOP_LENGTH / SR


@dataclass(frozen=True, slots=True)
class AudioFeatures:
    """
    Normalized spectral features of one audio stream.
    """

    # (n_mels, n_frames) log-mel spectrogram, normalised per frame.
    features: np.ndarray

    sr: int

    @property
    def n_frames(self) -> int:
        return int(self.features.shape[1])

    @property
    def duration(self) -> float:
        return self.n_frames * FEATURE_SECONDS


class VideoSyncError(Exception):
    """A video could not be synchronized (e.g. no audio track)."""


def extract_video_audio(
    video_path: Path,
    destination: Path,
) -> Path:
    """
    Extract the audio track of a video into a PCM WAV file.

    Raises ``VideoSyncError`` when the video has no usable audio track.
    """

    destination = destination.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        decode_to_wav(video_path, destination)
    except Exception as error:
        raise VideoSyncError(
            f"Could not extract audio from {video_path}: {error}"
        ) from error

    return destination


def compute_features(
    audio_path: Path,
    *,
    sr: int = SR,
    n_mels: int = N_MELS,
    hop_length: int = HOP_LENGTH,
) -> AudioFeatures:
    """
    Compute normalised log-mel features of an audio file.

    The spectrogram is converted to log magnitude and normalised per
    frame, making it robust to volume and gain differences.
    """

    y, loaded_sr = librosa.load(
        str(audio_path),
        sr=sr,
        mono=True,
    )

    sr_out = int(loaded_sr)

    spectrogram = librosa.feature.melspectrogram(
        y=y,
        sr=sr_out,
        n_mels=n_mels,
        n_fft=N_FFT,
        hop_length=hop_length,
    )

    # Log magnitude with a floor to avoid -inf.
    log_mel = librosa.power_to_db(
        spectrogram,
        ref=np.max,
        top_db=80.0,
    )

    # Normalise each frame to unit max so overall volume does not
    # affect the correlation.
    frame_max = np.max(log_mel, axis=0, keepdims=True)
    frame_max[frame_max == 0] = 1.0

    features = log_mel / frame_max

    return AudioFeatures(
        features=np.asarray(features, dtype=np.float32),
        sr=sr_out,
    )
