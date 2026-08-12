from __future__ import annotations

import argparse
from pathlib import Path

import pytest

import octobeat.commands.add as add_cmd
from octobeat.config.model import Config, PathsConfig


@pytest.fixture
def charts_dir(tmp_path):
    directory = tmp_path / "charts"
    directory.mkdir()

    (directory / ".38 Special - Caught Up in You (Harmonix).sng").write_bytes(
        b"fake"
    )
    (directory / "Weezer - Say It Ain't So (Harmonix).sng").write_bytes(
        b"fake"
    )

    return directory


def _config(charts: Path) -> Config:
    return Config(
        paths=PathsConfig(charts=str(charts)),
    )


def test_resolve_existing_path(tmp_path):
    source = tmp_path / "song.sng"
    source.write_bytes(b"fake")

    assert add_cmd._resolve_source(
        str(source),
        config=Config(),
    ) == str(source)


def test_resolve_exact_chart_name(charts_dir):
    config = _config(charts_dir)

    resolved = add_cmd._resolve_source(
        "Weezer - Say It Ain't So (Harmonix).sng",
        config=config,
    )

    assert resolved == str(
        charts_dir / "Weezer - Say It Ain't So (Harmonix).sng"
    )


def test_resolve_missing_chart_raises_with_candidates(
    charts_dir,
):
    config = _config(charts_dir)

    with pytest.raises(
        add_cmd.SourceNotFoundError,
    ) as excinfo:
        add_cmd._resolve_source(
            "Special - Caught Up in You (Harmonix).sng",
            config=config,
        )

    error = excinfo.value

    assert error.source == (
        "Special - Caught Up in You (Harmonix).sng"
    )
    assert charts_dir in error.searched_dirs

    assert error.candidates == [
        charts_dir / ".38 Special - Caught Up in You (Harmonix).sng"
    ]


def test_resolve_missing_chart_without_candidates(
    charts_dir,
):
    config = _config(charts_dir)

    with pytest.raises(
        add_cmd.SourceNotFoundError,
    ) as excinfo:
        add_cmd._resolve_source(
            "Zzzy Band - Qqqq Song (Harmonix).sng",
            config=config,
        )

    assert excinfo.value.candidates == []


def test_resolve_url_passes_through():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    assert add_cmd._resolve_source(
        url,
        config=Config(),
    ) == url


def test_run_reports_clean_error_and_returns_1(
    monkeypatch,
    charts_dir,
    capsys,
):
    monkeypatch.setattr(
        add_cmd,
        "ensure_workspace",
        lambda: _config(charts_dir),
    )

    result = add_cmd.run(
        argparse.Namespace(
            input="Special - Caught Up in You (Harmonix).sng",
        )
    )

    assert result == 1

    output = capsys.readouterr().out

    assert "ERROR: Source not found" in output
    assert "Searched directories:" in output
    assert "Similar charts found:" in output
    assert (
        ".38 Special - Caught Up in You (Harmonix).sng"
        in output
    )
