from __future__ import annotations

import struct
import wave
from io import BytesIO

import numpy as np
import pytest

from octobeat.fixtures import build_sng_fixtures
from octobeat.providers.factory import get_provider
from octobeat.providers.sng import SngSourceProvider


@pytest.fixture
def fixtures(tmp_path):
    build_sng_fixtures(tmp_path)
    return tmp_path


def test_supports_sng():
    assert SngSourceProvider.supports("song.sng")
    assert SngSourceProvider.supports("SONG.SNG")
    assert not SngSourceProvider.supports("song.wav")


def test_factory_resolves_sng_source(fixtures):
    path = fixtures / "constant-tempo.sng"

    provider = get_provider(str(path))

    assert isinstance(provider, SngSourceProvider)


def test_load_extracts_audio_and_chart(fixtures):
    path = fixtures / "constant-tempo.sng"

    provider = SngSourceProvider()
    recording = provider.load(str(path))

    assert recording.path.exists()
    assert recording.path.suffix == ".wav"
    assert recording.chart_path == path.resolve()

    # Metadata from the container.
    assert recording.title == "Constant Tempo"
    assert recording.artist == "Fixture Band"

    recording.cleanup()


def test_cleanup_removes_temp(tmp_path):
    from octobeat.fixtures.sng import _constant_tempo, build_sng_fixture

    path = tmp_path / "fixture.sng"
    build_sng_fixture(path, _constant_tempo())

    provider = SngSourceProvider()
    recording = provider.load(str(path))

    wav = recording.path
    assert wav.exists()

    recording.cleanup()

    assert not wav.exists()


# --------------------------------------------------------------------------
# Multitrack containers: stems are mixed into the full mix
# --------------------------------------------------------------------------


def _make_wav(amplitude: float) -> bytes:
    """Build a tiny constant-amplitude mono WAV."""
    sr = 22050
    frames = int(sr * 0.1)
    buffer = BytesIO()

    with wave.open(buffer, "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(sr)
        file.writeframes(
            b"".join(
                struct.pack("<h", int(amplitude * 32767))
                for _ in range(frames)
            )
        )

    return buffer.getvalue()


def _multitrack_sng() -> bytes:
    from octobeat.fixtures.sng import (
        _build_notes_mid,
        _build_sng_container,
        _constant_tempo,
    )

    return _build_sng_container(
        {
            "name": "Multitrack",
            "artist": "Fixture Band",
            "song_length": "5000",
        },
        {
            "notes.mid": _build_notes_mid(_constant_tempo()),
            "guitar.opus": _make_wav(0.5),
            "vocals.opus": _make_wav(0.3),
            "song.wav": _make_wav(0.1),
        },
    )


def test_extract_stems_lists_instrument_tracks():
    from octobeat.timing.sng import extract_stems

    stems = extract_stems(_multitrack_sng())

    assert [name for name, _ in stems] == [
        "guitar.opus",
        "vocals.opus",
    ]


def test_extract_stems_empty_for_single_track(tmp_path):
    from octobeat.fixtures.sng import _constant_tempo, build_sng_fixture
    from octobeat.timing.sng import extract_stems

    path = tmp_path / "single.sng"
    build_sng_fixture(path, _constant_tempo())

    assert extract_stems(path.read_bytes()) == []


def test_load_mixes_stems_ignoring_song_track(tmp_path):
    import subprocess

    path = tmp_path / "multi.sng"
    path.write_bytes(_multitrack_sng())

    recording = SngSourceProvider().load(str(path))

    try:
        assert recording.path.exists()

        pcm = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(recording.path),
                "-f",
                "f32le",
                "pipe:1",
            ],
            check=True,
            capture_output=True,
        ).stdout

        samples = np.frombuffer(pcm, dtype=np.float32)

        # guitar (0.5) + vocals (0.3) summed and peak-normalised to
        # 0.95 -> constant tone, well above the 0.1 `song.wav` level.
        expected = 0.95
        assert samples.min() > 0
        assert abs(float(samples.mean()) - expected) < expected * 0.01
    finally:
        recording.cleanup()


def test_load_detects_count_in_and_song_start(tmp_path):
    """The provider detects the count-in / song start of the recording."""

    from octobeat.core.analyser import detect_music_lead_in

    path = tmp_path / "multi.sng"
    path.write_bytes(_multitrack_sng())

    recording = SngSourceProvider().load(str(path))

    try:
        assert recording.count_in_start is not None
        assert recording.song_start is not None
        assert 0.0 <= recording.count_in_start <= recording.song_start

        # The detection is reusable on any audio file.
        count_in, song_start = detect_music_lead_in(
            recording.path,
        )
        assert count_in >= 0.0
        assert song_start >= count_in
    finally:
        recording.cleanup()
