from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from octobeat.commands.analyse import run
from octobeat.fixtures import build_fixtures, build_sng_fixtures
from octobeat.io.songmap import read_songmap


@pytest.fixture
def fixtures(tmp_path):
    build_fixtures(tmp_path / "audio")
    build_sng_fixtures(tmp_path / "sng")
    return tmp_path


def _args(
    input: str,
    *,
    chart: str | None = None,
    output: Path | None = None,
) -> argparse.Namespace:
    return argparse.Namespace(
        input=input,
        chart=Path(chart) if chart else None,
        output=output,
        offset=None,
        debug=False,
    )


def test_analyse_with_chart(fixtures, tmp_path):
    audio = fixtures / "audio" / "constant-tempo.wav"
    chart = fixtures / "sng" / "constant-tempo.sng"
    out = tmp_path / "out.songmap.json"

    code = run(_args(str(audio), chart=str(chart), output=out))

    assert code == 0
    assert out.exists()

    songmap = read_songmap(out)

    # Chart timing: 120 BPM.
    assert abs(songmap.timing.bpm - 120.0) < 1.0
    assert songmap.timing.source == "sng"


def test_analyse_without_chart_is_unchanged(fixtures, tmp_path):
    audio = fixtures / "audio" / "constant-tempo.wav"
    out = tmp_path / "audio.songmap.json"

    code = run(_args(str(audio), output=out))

    assert code == 0
    assert out.exists()

    songmap = read_songmap(out)
    assert songmap.timing.source == "audio-analysis"


def test_analyse_chart_fallback_on_missing_chart(fixtures, tmp_path):
    audio = fixtures / "audio" / "constant-tempo.wav"
    out = tmp_path / "fallback.songmap.json"

    code = run(
        _args(
            str(audio),
            chart=str(fixtures / "sng" / "missing.sng"),
            output=out,
        ),
    )

    assert code == 0
    assert out.exists()

    songmap = read_songmap(out)
    assert songmap.timing.source == "audio-analysis"


def test_analyse_chart_fallback_on_corrupt_chart(fixtures, tmp_path):
    audio = fixtures / "audio" / "constant-tempo.wav"
    corrupt = fixtures / "sng" / "corrupt-chart.sng"
    out = tmp_path / "corrupt.songmap.json"

    code = run(
        _args(
            str(audio),
            chart=str(corrupt),
            output=out,
        ),
    )

    assert code == 0
    assert out.exists()

    songmap = read_songmap(out)
    assert songmap.timing.source == "audio-analysis"


def test_analyse_chart_fallback_on_unsupported_format(fixtures, tmp_path):
    audio = fixtures / "audio" / "constant-tempo.wav"
    out = tmp_path / "fmt.songmap.json"

    code = run(
        _args(
            str(audio),
            chart=str(fixtures / "audio" / "silence.wav"),
            output=out,
        ),
    )

    assert code == 0
    assert out.exists()

    songmap = read_songmap(out)
    assert songmap.timing.source == "audio-analysis"


def test_analyse_chart_keeps_chart_offset(fixtures, tmp_path):
    """The SongMap offset comes from the chart, not the audio.

    Re-writing the offset from audio analysis would desynchronise the
    chart's beats from the chart's own grid.
    """

    audio = fixtures / "audio" / "constant-tempo.wav"
    chart = fixtures / "sng" / "constant-tempo.sng"
    out = tmp_path / "offset.songmap.json"

    code = run(_args(str(audio), chart=str(chart), output=out))

    assert code == 0

    songmap = read_songmap(out)
    assert songmap.timing.offset == 0.0
    assert songmap.beats[0].time == 0.0


def test_analyse_chart_sections_in_songmap(fixtures, tmp_path):
    audio = fixtures / "audio" / "constant-tempo.wav"
    chart = fixtures / "sng" / "sections.sng"
    out = tmp_path / "sections.songmap.json"

    code = run(_args(str(audio), chart=str(chart), output=out))

    assert code == 0

    songmap = read_songmap(out)
    assert songmap.sections is not None
    names = [section.name for section in songmap.sections]
    assert "Intro" in names
    assert "Chorus" in names
