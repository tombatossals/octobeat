from __future__ import annotations

import json

import pytest

from octobeat.fixtures import build_video_sync_fixtures
from octobeat.sync import (
    AUTO_CONFIDENCE,
    compute_features,
    sync_video,
)


@pytest.fixture
def fixtures(tmp_path):
    build_video_sync_fixtures(tmp_path)
    return tmp_path


def _sync(fixtures, name: str):
    directory = fixtures / name

    reference = compute_features(directory / "reference.wav")
    video = compute_features(directory / "video.wav")

    return sync_video(reference, video)


def test_manifest_exists(fixtures):
    manifest = fixtures / "manifest.json"
    assert manifest.exists()

    entries = json.loads(manifest.read_text(encoding="utf-8"))
    names = {entry["name"] for entry in entries}

    assert {
        "exact-match",
        "intro",
        "silent-intro",
        "compressed",
        "different-volume",
        "offset",
        "count-in",
        "mismatch",
        "no-audio",
    } <= names


@pytest.mark.parametrize(
    "name,expected_offset",
    [
        ("exact-match", 0.0),
        ("intro", 2.0),
        ("silent-intro", 3.0),
        ("different-volume", 2.0),
        ("offset", 1.5),
    ],
)
def test_offset_detection(fixtures, name, expected_offset):
    result = _sync(fixtures, name)

    assert abs(result.offset - expected_offset) < 0.15
    assert result.confidence >= 0.90


def test_compressed_audio_still_detected(fixtures):
    result = _sync(fixtures, "compressed")

    assert abs(result.offset - 2.0) < 0.15
    # Compression degrades the correlation, so confidence is lower but
    # still acceptable.
    assert result.confidence >= 0.60
    assert result.status != "review"


def test_count_in_reference_aligns_with_song_start(fixtures):
    """A reference with a count-in the video lacks aligns once the
    lead-in is accounted for, producing a negative video offset."""

    directory = fixtures / "count-in"

    reference = compute_features(
        directory / "reference.wav",
    )
    video = compute_features(
        directory / "video.wav",
    )

    result = sync_video(
        reference,
        video,
        song_start=2.0,
    )

    assert abs(result.offset - (-2.0)) < 0.15
    assert result.confidence >= 0.90


def test_mismatch_has_low_confidence(fixtures):
    result = _sync(fixtures, "mismatch")

    # A different song must not be trusted as a match.
    assert result.confidence < AUTO_CONFIDENCE


def test_sync_status_thresholds():
    from octobeat.sync import VideoSyncResult

    auto = VideoSyncResult(offset=1.0, confidence=0.95)
    warn = VideoSyncResult(offset=1.0, confidence=0.80)
    review = VideoSyncResult(offset=1.0, confidence=0.50)

    assert auto.status == "auto"
    assert warn.status == "warn"
    assert review.status == "review"


def test_confidence_bounds(fixtures):
    for name in (
        "exact-match",
        "intro",
        "mismatch",
        "compressed",
    ):
        result = _sync(fixtures, name)
        assert 0.0 <= result.confidence <= 1.0
        assert result.offset >= 0.0


def test_no_audio_returns_low_confidence(fixtures):
    result = _sync(fixtures, "no-audio")
    assert result.confidence < AUTO_CONFIDENCE


def test_fixture_generation_is_deterministic(tmp_path):
    build_video_sync_fixtures(tmp_path / "a")
    build_video_sync_fixtures(tmp_path / "b")

    a = (tmp_path / "a" / "intro" / "reference.wav").read_bytes()
    b = (tmp_path / "b" / "intro" / "reference.wav").read_bytes()

    assert a == b
