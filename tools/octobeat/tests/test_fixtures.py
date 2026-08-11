from __future__ import annotations

import pytest

from octobeat.core.analyser import analyse_recording
from octobeat.fixtures import build_fixtures
from octobeat.pipeline.builder import get_provider

# Tolerance around the expected BPM.
BPM_TOLERANCE = 3.0

# Looser tolerance for ramp endpoints: a 4s analysis window averages
# over the ramping tempo, so the measured first/last tempo lags the
# true ramp endpoints.
RAMP_TOLERANCE = 10.0


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
        "accelerando",
        "ritardando",
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


def test_fixture_constant_tempo_single_segment(
    tmp_path,
) -> None:
    fixtures = _fixture_paths(tmp_path)

    result = _analyse(
        fixtures / "constant-tempo.wav",
    )

    assert len(result.report.tempo_map) == 1

    start, bpm = result.report.tempo_map[0]

    assert start == 0.0
    assert abs(bpm - 120) < BPM_TOLERANCE


def test_fixture_tempo_change_segments(
    tmp_path,
) -> None:
    fixtures = _fixture_paths(tmp_path)

    result = _analyse(
        fixtures / "tempo-change.wav",
    )

    tempo_map = result.report.tempo_map

    assert len(tempo_map) >= 2

    first_start, first_bpm = tempo_map[0]
    _last_start, last_bpm = tempo_map[-1]

    assert first_start == 0.0
    assert abs(first_bpm - 120) < BPM_TOLERANCE
    assert abs(last_bpm - 150) < BPM_TOLERANCE

    # The songmap serialises the tempo map.
    timing = result.songmap.timing

    assert timing.tempoMap is not None
    assert len(timing.tempoMap) >= 2


def test_fixture_accelerando_ramp(
    tmp_path,
) -> None:
    fixtures = _fixture_paths(tmp_path)

    result = _analyse(
        fixtures / "accelerando.wav",
    )

    tempo_map = result.report.tempo_map

    assert len(tempo_map) >= 2

    first_bpm = tempo_map[0][1]
    last_bpm = tempo_map[-1][1]

    assert first_bpm < last_bpm
    assert abs(first_bpm - 120) < RAMP_TOLERANCE
    assert abs(last_bpm - 150) < RAMP_TOLERANCE


def test_fixture_ritardando_ramp(
    tmp_path,
) -> None:
    fixtures = _fixture_paths(tmp_path)

    result = _analyse(
        fixtures / "ritardando.wav",
    )

    tempo_map = result.report.tempo_map

    assert len(tempo_map) >= 2

    first_bpm = tempo_map[0][1]
    last_bpm = tempo_map[-1][1]

    assert first_bpm > last_bpm
    assert abs(first_bpm - 150) < RAMP_TOLERANCE
    assert abs(last_bpm - 120) < RAMP_TOLERANCE


def test_fixture_tempo_change_beat_grid_continuous(
    tmp_path,
) -> None:
    """Beat indices must stay continuous across a tempo change."""

    fixtures = _fixture_paths(tmp_path)

    result = _analyse(
        fixtures / "tempo-change.wav",
    )

    beats = result.songmap.beats

    indices = [beat.index for beat in beats]

    assert indices == list(
        range(1, len(indices) + 1)
    )

    # The spacing must shrink after the tempo change (6s).
    times = [beat.time for beat in beats]

    before = [
        times[i + 1] - times[i]
        for i in range(len(times) - 1)
        if times[i] < 6.0
    ]

    after = [
        times[i + 1] - times[i]
        for i in range(len(times) - 1)
        if times[i] >= 6.0
    ]

    assert before
    assert after

    import statistics

    assert statistics.mean(before) > statistics.mean(after)
