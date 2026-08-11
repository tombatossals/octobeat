from __future__ import annotations

import json
from pathlib import Path

import pytest

from octobeat.charts import find_chart
from octobeat.config.model import Config, PathsConfig
from octobeat.fixtures import build_sng_fixtures
from octobeat.models.recording import Recording
from octobeat.models.songmap import Source


@pytest.fixture
def charts_dir(tmp_path):
    build_sng_fixtures(tmp_path / "charts")

    # Real-world charts are named "Artist - Title.sng".
    source = tmp_path / "charts" / "constant-tempo.sng"
    target = (
        tmp_path
        / "charts"
        / "Fixture Band - Constant Tempo.sng"
    )
    target.write_bytes(source.read_bytes())

    return tmp_path / "charts"


def _recording(artist: str | None, title: str | None) -> Recording:
    return Recording(
        path=Path("/tmp/song.wav"),
        artist=artist,
        title=title,
    )


def _config(charts: Path | None) -> Config:
    return Config(
        paths=PathsConfig(charts=str(charts) if charts else None),
    )


def test_find_chart_by_artist_title(charts_dir):
    config = _config(charts_dir)

    recording = _recording(
        artist="Fixture Band",
        title="Constant Tempo",
    )

    chart = find_chart(recording, config=config)

    assert chart is not None
    assert chart.name == "Fixture Band - Constant Tempo.sng"


def test_find_chart_by_title_only(charts_dir):
    config = _config(charts_dir)

    recording = _recording(None, "Constant Tempo")

    chart = find_chart(recording, config=config)

    assert chart is not None
    assert chart.name == "Fixture Band - Constant Tempo.sng"


def test_find_chart_case_and_separator_insensitive(charts_dir):
    config = _config(charts_dir)

    recording = _recording(
        artist="Fixture_Band",
        title="CONSTANT TEMPO",
    )

    chart = find_chart(recording, config=config)

    assert chart is not None


def test_find_chart_none_when_no_match(charts_dir):
    config = _config(charts_dir)

    recording = _recording(
        artist="Nobody",
        title="Unknown Song",
    )

    assert find_chart(recording, config=config) is None


def test_find_chart_none_without_metadata(charts_dir):
    config = _config(charts_dir)

    recording = _recording(None, None)

    assert find_chart(recording, config=config) is None


def test_find_chart_none_when_dir_missing(tmp_path):
    config = _config(tmp_path / "nope")

    recording = _recording(
        artist="Fixture Band",
        title="Constant Tempo",
    )

    assert find_chart(recording, config=config) is None


def test_find_chart_falls_back_to_repo_sng():
    """When charts dir is unset, the repo sng/ directory is searched."""

    repo_sng = Path(__file__).resolve().parents[3] / "sng"
    if not repo_sng.is_dir():
        pytest.skip("No sng/ samples directory available.")

    config = _config(None)

    recording = _recording(
        artist="Weezer",
        title="Say It Ain't So",
    )

    chart = find_chart(recording, config=config)

    assert chart is not None
    assert chart.suffix == ".sng"


def test_find_chart_diacritics_insensitive(charts_dir):
    """Unaccented search terms match accented file names."""

    config = _config(charts_dir)

    recording = _recording(
        artist="Fixture Band",
        title="Constant-Tempo",
    )

    chart = find_chart(recording, config=config)

    assert chart is not None


def test_build_dataset_uses_matching_chart(monkeypatch, tmp_path):
    """build_dataset prefers a matching community chart."""

    import octobeat.pipeline.builder as builder_module
    from octobeat.pipeline import build_dataset

    # Build a charts directory with a matching "Artist - Title.sng".
    build_sng_fixtures(tmp_path / "charts")
    source = tmp_path / "charts" / "constant-tempo.sng"
    target = (
        tmp_path
        / "charts"
        / "Fixture Band - Constant Tempo.sng"
    )
    target.write_bytes(source.read_bytes())

    config = _config(tmp_path / "charts")

    # A recording whose name matches the chart.
    recording = Recording(
        path=_make_click_wav(
            tmp_path / "fixture_band - constant_tempo.wav",
        ),
        artist="Fixture Band",
        title="Constant Tempo",
        source=Source(type="file", id="fixture"),
    )

    class _FakeProvider:
        @classmethod
        def supports(cls, source: str) -> bool:
            return True

        def load(self, source: str) -> Recording:
            return recording

    monkeypatch.setattr(
        builder_module,
        "get_provider",
        lambda _: _FakeProvider(),
    )
    monkeypatch.setattr(
        builder_module,
        "DeezerProvider",
        lambda: _BrokenDeezer(),
    )
    monkeypatch.setattr(
        builder_module,
        "_default_config",
        lambda: config,
    )

    result = build_dataset(
        "fixture",
        output=tmp_path / "datasets",
        include_cover=False,
    )

    songmap = json.loads(
        (
            tmp_path
            / "datasets"
            / result.dataset_id
            / "songmap.json"
        ).read_text(
            encoding="utf-8",
        )
    )

    assert songmap["timing"]["source"] == "sng"

    metadata = json.loads(
        (
            tmp_path
            / "datasets"
            / result.dataset_id
            / "metadata.json"
        ).read_text(
            encoding="utf-8",
        )
    )

    assert metadata["timing"]["source"] == "sng"


def _make_click_wav(path: Path, *, sr: int = 22050, bpm: int = 120) -> Path:
    import wave

    import numpy as np

    interval = 60.0 / bpm
    seconds = 8.0
    samples = int(sr * seconds)

    track = np.zeros(samples)

    t = 0.0
    while t < seconds:
        start = int(t * sr)
        end = min(start + int(0.05 * sr), samples)
        track[start:end] += 0.8
        t += interval

    pcm = (track * 32767).astype(np.int16)

    with wave.open(str(path), "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(sr)
        file.writeframes(pcm.tobytes())

    return path


class _BrokenDeezer:
    def metadata(self, artist, title):
        raise RuntimeError("network down")
