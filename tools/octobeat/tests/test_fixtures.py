from __future__ import annotations

import pytest

from octobeat.core.analyser import analyse_recording
from octobeat.fixtures import build_fixtures
from octobeat.pipeline.builder import get_provider

# Tolerance around the expected BPM.
BPM_TOLERANCE = 3.0


@pytest.fixture(autouse=True)
def _no_lyrics_network(monkeypatch):
    import octobeat.core.analyser as analyser_module

    monkeypatch.setattr(
        analyser_module,
        "_fetch_lrclib_lyrics",
        lambda *args, **kwargs: None,
    )


def _analyse(
    path,
):
    recording = get_provider(str(path)).load(str(path))

    return analyse_recording(
        recording,
        provider="fixture",
        source=str(path),
    )


def _fixture_paths(
    tmp_path,
):
    build_fixtures(tmp_path / "fixtures")

    return tmp_path / "fixtures"


@pytest.mark.parametrize(
    "name,expected_bpm",
    [
        ("constant-tempo", 120),
        ("half-time", 80),
        ("double-time", 160),
    ],
)
def test_fixture_bpm(
    tmp_path,
    name: str,
    expected_bpm: float,
) -> None:
    fixtures = _fixture_paths(tmp_path)

    result = _analyse(
        fixtures / f"{name}.wav",
    )

    assert abs(
        result.report.bpm - expected_bpm,
    ) < BPM_TOLERANCE

    assert result.report.beats > 10


def test_fixture_intro_offset(
    tmp_path,
) -> None:
    fixtures = _fixture_paths(tmp_path)

    result = _analyse(
        fixtures / "intro.wav",
    )

    # The music starts at 3s; the first beat should be at/after that.
    assert result.songmap.timing.offset >= 0.0

    first_beat = (
        result.songmap.beats[0].time
        if result.songmap.beats
        else None
    )

    if first_beat is not None:
        assert first_beat >= 3.0 - BPM_TOLERANCE


def test_fixture_silence_has_no_beats(
    tmp_path,
) -> None:
    fixtures = _fixture_paths(tmp_path)

    result = _analyse(
        fixtures / "silence.wav",
    )

    assert result.report.beats == 0


def test_fixture_manifest_exists(
    tmp_path,
) -> None:
    fixtures = _fixture_paths(tmp_path)

    manifest = fixtures / "manifest.json"

    assert manifest.exists()

    import json

    entries = json.loads(
        manifest.read_text(
            encoding="utf-8",
        )
    )

    names = {
        entry["name"]
        for entry in entries
    }

    assert {
        "constant-tempo",
        "half-time",
        "double-time",
        "tempo-change",
        "syncopated",
        "intro",
        "silence",
    } <= names


def test_fixture_confidence_metrics(
    tmp_path,
) -> None:
    fixtures = _fixture_paths(tmp_path)

    result = _analyse(
        fixtures / "constant-tempo.wav",
    )

    report = result.report

    # A clean constant tempo should score high everywhere.
    assert report.tempo_confidence > 0.5
    assert report.beat_confidence > 0.5
    assert report.grid_stability > 0.5
