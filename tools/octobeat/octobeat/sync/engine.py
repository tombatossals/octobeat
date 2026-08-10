"""Video offset detection via cross-correlation of spectral features.

Given reference features (the audio the SongMap was built from) and
video features (audio extracted from the video), finds the offset at
which the reference song starts inside the video:

    videoOffset  =  the video time where reference time 0 lands
    videoTime    =  songTime + videoOffset
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from octobeat.models.songmap import SongMap
from octobeat.sync.features import FEATURE_SECONDS, AudioFeatures

# Confidence thresholds.
AUTO_CONFIDENCE = 0.90
WARN_CONFIDENCE = 0.70

# Ratio of the best peak to the second-best peak below which the match
# is considered ambiguous.
PEAK_DOMINANCE_RATIO = 1.15


@dataclass(frozen=True, slots=True)
class VideoSyncResult:
    """
    Result of synchronising a video with a reference audio.
    """

    offset: float

    confidence: float

    @property
    def status(self) -> str:
        if self.confidence >= AUTO_CONFIDENCE:
            return "auto"
        if self.confidence >= WARN_CONFIDENCE:
            return "warn"
        return "review"


def sync_video(
    reference: AudioFeatures,
    video: AudioFeatures,
) -> VideoSyncResult:
    """
    Estimate the offset at which the reference song starts in the video.

    ``offset`` is the video time corresponding to reference time 0:

    ``videoTime = songTime + offset``
    """

    offset, confidence = _cross_correlate(
        reference.features,
        video.features,
    )

    return VideoSyncResult(
        offset=round(float(offset), 3),
        confidence=round(float(confidence), 2),
    )


def attach_video_to_songmap(
    songmap: SongMap,
    *,
    video_file: str,
    video_offset: float,
    sync_confidence: float,
) -> SongMap:
    """
    Attach a synchronized video to a SongMap (returns a new SongMap).

    The timing is never modified: only ``media.video`` is set.
    """

    from octobeat.models.songmap import Media, VideoMedia

    media = Media(
        video=VideoMedia(
            file=video_file,
            offset=round(float(video_offset), 3),
            syncConfidence=round(float(sync_confidence), 2),
        ),
    )

    return songmap.model_copy(update={"media": media})


def _cross_correlate(
    reference: np.ndarray,
    video: np.ndarray,
) -> tuple[float, float]:
    """Cross-correlate feature columns and return (offset, confidence).

    The reference (n_mels, n_ref) is correlated against the video
    (n_mels, n_video) column by column. For each possible lag the
    overlap similarity is summed over the mel bands, producing a
    correlation curve. The best lag is the offset; confidence is derived
    from how dominant the peak is.
    """

    n_mels, n_ref = reference.shape
    _n_mels, n_video = video.shape

    # Normalise each column of both feature sets (unit L2) so the
    # correlation is invariant to volume.
    ref_norm = _normalise_columns(reference)
    video_norm = _normalise_columns(video)

    scores = np.full(n_video, -np.inf)

    # Number of lags to try: the reference may start anywhere inside
    # the video (including an intro). We try every lag where the
    # reference fits entirely inside the video.
    min_lag = 0
    max_lag = max(0, n_video - n_ref)

    for lag in range(min_lag, max_lag + 1):
        video_slice = video_norm[:, lag : lag + n_ref]

        overlap = video_slice.shape[1]
        if overlap < 1:
            break

        # Correlation: mean over columns of the dot product of the
        # aligned mel bands.
        dot = np.sum(
            ref_norm[:, :overlap] * video_slice[:, :overlap],
            axis=0,
        )

        scores[lag] = float(np.mean(dot))

    valid = scores[np.isfinite(scores)]

    if valid.size == 0:
        return 0.0, 0.0

    best_lag = int(np.argmax(valid))
    # Re-map the index: argmax(valid) is relative to the filtered array.
    best_lag = int(np.flatnonzero(np.isfinite(scores))[best_lag])

    confidence = _peak_confidence(
        scores,
        best_lag,
    )

    # Sub-sample refinement: parabolic interpolation around the best lag.
    refined = _refine_lag(scores, best_lag)

    offset = refined * FEATURE_SECONDS

    return offset, confidence


def _normalise_columns(features: np.ndarray) -> np.ndarray:
    """Center each column (subtract the mean) then normalise to unit L2.

    Centering measures spectral *pattern* similarity instead of absolute
    gain, so different songs correlate low while the same song (even
    compressed or at different volume) correlates high.
    """

    centered = features - np.mean(features, axis=0, keepdims=True)

    norms = np.linalg.norm(centered, axis=0, keepdims=True)
    norms[norms == 0] = 1.0

    return np.asarray(centered / norms, dtype=np.float32)


def _peak_confidence(
    scores: np.ndarray,
    best_lag: int,
) -> float:
    """Confidence from the height and dominance of the correlation peak.

    Two signals combine:

    - the absolute peak height (how much the spectral patterns match) —
      the strongest discriminator between the same song and a different
      one;
    - how much the peak dominates the other lags (uniqueness).
    """

    best = float(scores[best_lag])

    if not np.isfinite(best) or best <= 0:
        return 0.0

    # Height component: map a correlation peak in [0.4, 0.95] to
    # confidence [0, 1]. Same-song matches score ~0.9+; mismatches <0.6.
    height = max(0.0, min(1.0, (best - 0.40) / 0.55))

    # Second-best peak, excluding a small window around the best lag.
    others = np.full_like(scores, -np.inf)
    lo = max(0, best_lag - 5)
    hi = min(len(scores), best_lag + 6)
    others[lo:hi] = -np.inf

    finite_others = others[np.isfinite(others)]

    if finite_others.size == 0:
        dominance = 1.0
    else:
        second_best = float(np.max(finite_others))

        if not np.isfinite(second_best) or second_best <= 0:
            dominance = 1.0
        else:
            ratio = best / second_best
            dominance = max(0.0, min(1.0, (ratio - 1.0) / 0.25))

    # The height dominates; uniqueness refines.
    confidence = 0.75 * height + 0.25 * dominance

    return max(0.0, min(1.0, confidence))


def _refine_lag(
    scores: np.ndarray,
    best_lag: int,
) -> float:
    """Parabolic interpolation of the correlation peak."""

    if (
        best_lag <= 0
        or best_lag + 1 >= scores.size
    ):
        return float(best_lag)

    left = float(scores[best_lag - 1])
    center = float(scores[best_lag])
    right = float(scores[best_lag + 1])

    if not (
        np.isfinite(left)
        and np.isfinite(center)
        and np.isfinite(right)
    ):
        return float(best_lag)

    denominator = left - 2 * center + right

    if abs(denominator) < 1e-12:
        return float(best_lag)

    offset = 0.5 * (left - right) / denominator

    if offset < -1.0 or offset > 1.0:
        return float(best_lag)

    return float(best_lag + offset)
