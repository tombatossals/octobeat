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
    """Build a tiny constant-amplitude mono WAV (48 kHz)."""
    sr = 48000
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


def _make_wav_lead(amplitude: float) -> bytes:
    """Constant-amplitude burst followed by silence (like a count-in)."""
    sr = 48000
    frames = int(sr * 0.1)
    burst = frames // 2
    buffer = BytesIO()

    with wave.open(buffer, "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(sr)
        file.writeframes(
            b"".join(
                struct.pack("<h", int(amplitude * 32767))
                for _ in range(burst)
            )
            + b"\x00\x00" * (frames - burst)
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
            "song.wav": _make_wav_lead(0.1),
        },
    )


def _multitrack_sng_with_drums() -> bytes:
    from octobeat.fixtures.sng import (
        _build_notes_mid,
        _build_sng_container,
        _constant_tempo,
    )

    return _build_sng_container(
        {
            "name": "Drums",
            "artist": "Fixture Band",
            "song_length": "5000",
        },
        {
            "notes.mid": _build_notes_mid(_constant_tempo()),
            "guitar.opus": _make_wav(0.5),
            "drums.opus": _make_wav(0.3),
            "drums_1.opus": _make_wav(0.2),
            "vocals.opus": _make_wav(0.4),
        },
    )


def test_is_drum_stem():
    from octobeat.timing.sng import is_drum_stem

    assert is_drum_stem("drums.opus")
    assert is_drum_stem("drums.ogg")
    assert is_drum_stem("drums.mp3")
    assert is_drum_stem("drums.wav")
    assert is_drum_stem("drums_1.opus")
    assert is_drum_stem("drums_3.wav")

    assert not is_drum_stem("guitar.opus")
    assert not is_drum_stem("vocals.ogg")
    assert not is_drum_stem("song.wav")


def test_extract_stems_without_drums():
    from octobeat.timing.sng import (
        extract_stems,
        extract_stems_without_drums,
    )

    data = _multitrack_sng_with_drums()

    assert [name for name, _ in extract_stems(data)] == [
        "drums.opus",
        "drums_1.opus",
        "guitar.opus",
        "vocals.opus",
    ]

    without = extract_stems_without_drums(data)

    assert [name for name, _ in without] == [
        "guitar.opus",
        "vocals.opus",
    ]


def test_extract_stems_lists_instrument_tracks():
    from octobeat.timing.sng import extract_stems

    stems = extract_stems(_multitrack_sng())

    assert [name for name, _ in stems] == [
        "guitar.opus",
        "vocals.opus",
    ]


def test_extract_full_mix_returns_song_track():
    from octobeat.timing.sng import extract_full_mix

    name, audio = extract_full_mix(_multitrack_sng())

    assert name == "song.wav"
    assert audio


def test_extract_full_mix_none_without_song_track():
    from octobeat.fixtures.sng import (
        _build_notes_mid,
        _build_sng_container,
        _constant_tempo,
    )
    from octobeat.timing.sng import extract_full_mix

    data = _build_sng_container(
        {
            "name": "No Mix",
            "artist": "Fixture Band",
            "song_length": "5000",
        },
        {
            "notes.mid": _build_notes_mid(_constant_tempo()),
            "guitar.opus": _make_wav(0.5),
            "vocals.opus": _make_wav(0.3),
        },
    )

    assert extract_full_mix(data) is None


def test_extract_stems_empty_for_single_track(tmp_path):
    from octobeat.fixtures.sng import _constant_tempo, build_sng_fixture
    from octobeat.timing.sng import extract_stems

    path = tmp_path / "single.sng"
    build_sng_fixture(path, _constant_tempo())

    assert extract_stems(path.read_bytes()) == []


def test_load_mixes_stems_with_song_track(tmp_path):
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
        half = len(samples) // 2

        # guitar (0.5) + vocals (0.3) + song (0.1 burst then silence),
        # summed and peak-normalised to 0.95. The `song.wav` full-mix
        # track is part of the mix, so the trailing half stays below the
        # stems-only level while the leading half peaks at 0.95.
        assert samples.min() > 0
        assert abs(float(samples[:half].mean()) - 0.95) < 0.01
        assert 0.80 <= float(samples[half:].mean()) <= 0.90
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


# --------------------------------------------------------------------------
# Count-in click detection
# --------------------------------------------------------------------------


def _write_wav(samples: np.ndarray, sr: int = 48000) -> bytes:
    """Pack float samples into a mono 16-bit WAV."""
    buffer = BytesIO()

    with wave.open(buffer, "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(sr)
        pcm = np.clip(
            samples * 32767,
            -32768,
            32767,
        ).astype(np.int16)
        file.writeframes(
            pcm.tobytes(),
        )

    return buffer.getvalue()


def _clicks_wav() -> bytes:
    """Silence, sparse quiet clicks, then a loud sustained tone.

    Mimics an SNG mix where the count-in clicks are buried under the
    song's dynamic range (the blur/Beetlebum case).
    """

    sr = 48000
    duration = 4.0
    samples = np.zeros(
        int(sr * duration),
        dtype=np.float64,
    )

    for time in (0.5, 1.0, 1.5):
        start = int(time * sr)
        samples[
            start : start + int(0.05 * sr)
        ] = 0.05

    samples[int(2.5 * sr):] = 1.0

    return _write_wav(samples)


def test_detect_music_lead_in_catches_quiet_count_in(tmp_path):
    from octobeat.core.analyser import detect_music_lead_in

    path = tmp_path / "lead.wav"
    path.write_bytes(_clicks_wav())

    count_in, song_start = detect_music_lead_in(
        path,
    )

    # The quiet clicks are the first audible content; the song starts at
    # the loud sustained tone.
    assert 0.4 <= count_in <= 0.6
    assert 2.4 <= song_start <= 2.6


def test_detect_count_in_clicks_finds_click_times(tmp_path):
    from octobeat.core.analyser import detect_count_in_clicks

    path = tmp_path / "clicks.wav"
    path.write_bytes(_clicks_wav())

    clicks = detect_count_in_clicks(
        path,
        limit=2.0,
    )

    assert len(clicks) == 3
    assert 0.48 <= clicks[0] <= 0.53
    assert 0.98 <= clicks[1] <= 1.03
    assert 1.48 <= clicks[2] <= 1.53


def test_load_records_count_in_clicks(tmp_path):
    """The provider records the individual count-in clicks from song.*."""

    from octobeat.fixtures.sng import (
        _build_notes_mid,
        _build_sng_container,
        _constant_tempo,
    )

    path = tmp_path / "clicks.sng"
    path.write_bytes(
        _build_sng_container(
            {
                "name": "Clicks",
                "artist": "Fixture Band",
                "song_length": "4000",
            },
            {
                "notes.mid": _build_notes_mid(_constant_tempo()),
                "guitar.opus": _write_wav(
                    np.concatenate(
                        [
                            np.zeros(
                                int(48000 * 2.5),
                                dtype=np.float64,
                            ),
                            np.full(
                                int(48000 * 1.5),
                                0.5,
                                dtype=np.float64,
                            ),
                        ]
                    )
                ),
                "song.wav": _clicks_wav(),
            },
        )
    )

    recording = SngSourceProvider().load(str(path))

    try:
        clicks = recording.count_in_clicks

        assert clicks is not None
        assert len(clicks) == 3
        assert 0.48 <= clicks[0] <= 0.53
        assert 0.98 <= clicks[1] <= 1.03
        assert 1.48 <= clicks[2] <= 1.53
        assert (
            recording.count_in_start
            == clicks[0]
        )
    finally:
        recording.cleanup()
