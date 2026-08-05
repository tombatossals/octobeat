from __future__ import annotations

import json
import wave
from pathlib import Path

import numpy as np

from octobeat.pipeline import build_dataset


def _make_click_wav(
    path: Path,
    *,
    sr: int = 22050,
    bpm: int = 120,
    seconds: float = 8.0,
) -> Path:
    interval = 60.0 / bpm

    samples = int(sr * seconds)

    track = np.zeros(samples)

    t = 0.0
    while t < seconds:
        start = int(t * sr)
        end = min(
            start + int(0.05 * sr),
            samples,
        )
        track[start:end] += 0.8
        t += interval

    pcm = (
        track * 32767
    ).astype(np.int16)

    with wave.open(str(path), "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(sr)
        file.writeframes(pcm.tobytes())

    return path


def test_build_dataset_from_local_file(
    tmp_path,
) -> None:
    source = _make_click_wav(
        tmp_path / "mxpx-responsibility.wav",
    )

    result = build_dataset(
        str(source),
        output=tmp_path / "datasets",
        include_video=False,
        include_cover=False,
    )

    dataset_dir = (
        tmp_path
        / "datasets"
        / result.dataset_id
    )

    assert dataset_dir.is_dir()

    songmap_path = dataset_dir / "songmap.json"
    metadata_path = dataset_dir / "metadata.json"

    assert songmap_path.exists()
    assert metadata_path.exists()
    assert (dataset_dir / "recording.wav").exists()
    assert (dataset_dir / "recording.webm").exists()

    songmap = json.loads(
        songmap_path.read_text(
            encoding="utf-8",
        )
    )

    assert songmap["timing"]["bpm"] > 0
    assert len(songmap["beats"]) > 0

    metadata = json.loads(
        metadata_path.read_text(
            encoding="utf-8",
        )
    )

    assert metadata["id"] == result.dataset_id
    assert metadata["resources"]["audio"] == "recording.webm"
    assert metadata["resources"].get("video") is None

    catalog_path = (
        tmp_path
        / "datasets"
        / "catalog.json"
    )

    catalog = json.loads(
        catalog_path.read_text(
            encoding="utf-8",
        )
    )

    assert len(catalog) == 1
    assert catalog[0]["id"] == result.dataset_id


def test_build_dataset_skips_catalog_when_disabled(
    tmp_path,
) -> None:
    source = _make_click_wav(
        tmp_path / "song.wav",
    )

    output = tmp_path / "datasets"

    build_dataset(
        str(source),
        output=output,
        include_video=False,
        include_cover=False,
        update_catalog=False,
    )

    assert not (output / "catalog.json").exists()
