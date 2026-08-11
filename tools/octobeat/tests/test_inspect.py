from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from octobeat.commands.inspect import run
from octobeat.fixtures import build_sng_fixtures


@pytest.fixture
def fixtures(tmp_path):
    build_sng_fixtures(tmp_path)
    return tmp_path


def _args(input: str) -> argparse.Namespace:
    return argparse.Namespace(input=input)


def test_inspect_valid_sng(fixtures, capsys):
    code = run(_args(str(fixtures / "constant-tempo.sng")))

    out = capsys.readouterr().out

    assert code == 0
    assert "SNG" in out
    assert "Timing" in out
    assert "Beats" in out
    assert "16" in out
    assert "120.0" in out


def test_inspect_reports_sections(fixtures, capsys):
    run(_args(str(fixtures / "sections.sng")))

    out = capsys.readouterr().out

    assert "intro" in out
    assert "chorus" in out
    assert "outro" in out


def test_inspect_invalid_magic_returns_error(fixtures, capsys):
    code = run(_args(str(fixtures / "invalid-magic.sng")))

    out = capsys.readouterr().out

    assert code == 1
    assert "ERROR" in out


def test_inspect_unsupported_version_returns_error(fixtures, capsys):
    code = run(_args(str(fixtures / "unsupported-version.sng")))

    out = capsys.readouterr().out

    assert code == 1
    assert "ERROR" in out


def test_inspect_truncated_returns_error(fixtures, capsys):
    code = run(_args(str(fixtures / "truncated.sng")))

    out = capsys.readouterr().out

    assert code == 1
    assert "ERROR" in out


def test_inspect_unsupported_format_returns_error(tmp_path, capsys):
    path = tmp_path / "song.wav"
    path.write_bytes(b"RIFF")

    code = run(_args(str(path)))

    out = capsys.readouterr().out

    assert code == 1
    assert "no timing provider" in out.lower()


def test_inspect_missing_file(capsys):
    code = run(_args("/nonexistent/song.sng"))

    out = capsys.readouterr().out

    assert code == 1
    assert "ERROR" in out


def test_real_world_sng_inspects(tmp_path):
    samples = Path(__file__).resolve().parents[3] / "sng"
    if not samples.is_dir():
        pytest.skip("No sng/ samples directory available.")

    for path in sorted(samples.glob("*.sng"))[:3]:
        assert run(_args(str(path))) == 0
