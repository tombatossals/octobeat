from __future__ import annotations

import json
import wave
from pathlib import Path

import numpy as np
import pytest

import octobeat.core.analyser as analyser_module
from octobeat.io.resource import (
    CATALOG_FILE,
    METADATA_FILE,
    RECORDING_WAV,
    SONGMAP_FILE,
)
from octobeat.pipeline import reanalyse_datasets


@pytest.fixture(autouse=True)
def _no_lyrics_network(monkeypatch):
    monkeypatch.setattr(
        analyser_module,
        "_fetch_lrclib_lyrics",
        lambda *args, **kwargs: None,
    )


def _make_dataset(
    root: Path,
    dataset_id: str,
    *,
    bpm: int,
) -> None:
    dataset_dir = root / dataset_id
    dataset_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    sr = 22050
    seconds = 8.0

    samples = int(sr * seconds)
    wave_track = np.zeros(samples)

    time = 0.0
    while time < seconds:
        index = int(time * sr)
        wave_track[
            index : index + int(0.03 * sr)
        ] += 0.8
        time += 60.0 / bpm

    pcm = (
        wave_track * 32767
    ).astype(np.int16)

    with wave.open(
        str(dataset_dir / RECORDING_WAV),
        "wb",
    ) as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(sr)
        file.writeframes(pcm.tobytes())

    (dataset_dir / METADATA_FILE).write_text(
        json.dumps(
            {
                "id": dataset_id,
                "title": "My Song",
                "artist": "The Artist",
                "genres": ["Rock"],
                "tags": [],
                "bpm": 100.0,
                "duration": seconds,
                "resources": {
                    "audio": RECORDING_WAV,
                },
            }
        ),
        encoding="utf-8",
    )

    (dataset_dir / SONGMAP_FILE).write_text(
        json.dumps(
            {
                "version": 1,
                "schema": "songmap/v1",
                "generatedBy": "old",
                "createdAt": "2026-01-01T00:00:00+00:00",
                "metadata": {
                    "title": dataset_id,
                    "duration": seconds,
                    "source": {
                        "type": "file",
                        "id": "old",
                    },
                },
                "timing": {
                    "bpm": 100.0,
                    "offset": 0.0,
                    "timeSignature": "4/4",
                    "confidence": 0.5,
                },
                "beats": [],
                "bars": [],
            }
        ),
        encoding="utf-8",
    )


def test_reanalyse_updates_songmaps(
    tmp_path,
) -> None:
    _make_dataset(
        tmp_path,
        "test-a",
        bpm=120,
    )

    _make_dataset(
        tmp_path,
        "test-b",
        bpm=150,
    )

    summary = reanalyse_datasets(
        tmp_path,
    )

    assert len(summary.reanalysed) == 2
    assert summary.failed == []

    bpm_by_id = {
        result.dataset_id: result.bpm
        for result in summary.reanalysed
    }

    assert abs(bpm_by_id["test-a"] - 120) < 2
    assert abs(bpm_by_id["test-b"] - 150) < 2


def test_reanalyse_preserves_metadata(
    tmp_path,
) -> None:
    _make_dataset(
        tmp_path,
        "test-a",
        bpm=120,
    )

    reanalyse_datasets(tmp_path)

    metadata = json.loads(
        (
            tmp_path
            / "test-a"
            / METADATA_FILE
        ).read_text(
            encoding="utf-8",
        )
    )

    assert metadata["title"] == "My Song"
    assert metadata["artist"] == "The Artist"
    assert metadata["bpm"] > 100


def test_reanalyse_refreshes_catalog(
    tmp_path,
) -> None:
    _make_dataset(
        tmp_path,
        "test-a",
        bpm=120,
    )

    catalog_path = tmp_path / CATALOG_FILE

    catalog_path.write_text(
        json.dumps(
            [
                {
                    "id": "test-a",
                    "title": "Old",
                    "artist": "Old",
                    "genres": [],
                    "tags": [],
                    "bpm": 100.0,
                    "duration": 8.0,
                    "resources": {
                        "audio": RECORDING_WAV,
                    },
                }
            ]
        ),
        encoding="utf-8",
    )

    reanalyse_datasets(
        tmp_path,
        catalog=catalog_path,
    )

    catalog = json.loads(
        catalog_path.read_text(
            encoding="utf-8",
        )
    )

    entry = next(
        item
        for item in catalog
        if item["id"] == "test-a"
    )

    assert abs(entry["bpm"] - 120) < 2
    assert entry["title"] == "My Song"


def test_reanalyse_reports_failures(
    tmp_path,
) -> None:
    # A directory with a songmap but no audio.
    dataset_dir = tmp_path / "broken"
    dataset_dir.mkdir()

    (dataset_dir / SONGMAP_FILE).write_text(
        "{}",
        encoding="utf-8",
    )

    summary = reanalyse_datasets(
        tmp_path,
    )

    assert len(summary.reanalysed) == 0

    assert len(summary.failed) == 1

    failed_id, _error = summary.failed[0]

    assert failed_id == "broken"


def test_reanalyse_ignores_non_datasets(
    tmp_path,
) -> None:
    # A plain directory without a songmap must be skipped.
    (tmp_path / "not-a-dataset").mkdir()

    summary = reanalyse_datasets(
        tmp_path,
    )

    assert summary.reanalysed == []
    assert summary.failed == []
