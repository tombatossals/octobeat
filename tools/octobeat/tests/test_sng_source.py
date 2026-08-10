from __future__ import annotations

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
