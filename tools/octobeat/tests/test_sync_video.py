from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from octobeat.commands.sync_video import run
from octobeat.core.songmap_builder import build_songmap
from octobeat.fixtures.video_sync import build_video_sync_fixtures
from octobeat.io.songmap import write_songmap
from octobeat.models.songmap import Source
from octobeat.models.timing import Beat, TempoSegment, TimingData


def _minimal_songmap(path: Path) -> None:
    timing = TimingData(
        tempos=[TempoSegment(start_beat=1, start_time=0.0, bpm=120.0)],
        beats=[Beat(index=1, time=0.0)],
        time_signatures=[],
        sections=[],
    )

    songmap = build_songmap(
        timing,
        title="Fixture",
        duration=6.0,
        source=Source(type="file", id="fixture"),
        source_kind="audio-analysis",
        generated_by="test",
        created_at="2026-08-10T00:00:00+00:00",
    )

    write_songmap(songmap, path)


@pytest.fixture
def dataset(tmp_path):
    """A minimal dataset directory: songmap.json + recording.wav."""

    build_video_sync_fixtures(tmp_path / "fx")

    import shutil

    shutil.copy(
        tmp_path / "fx" / "intro" / "reference.wav",
        tmp_path / "recording.wav",
    )

    _minimal_songmap(tmp_path / "songmap.json")

    return tmp_path


def test_sync_video_detects_offset(dataset):
    songmap = dataset / "songmap.json"
    video = dataset / "fx" / "intro" / "video.wav"

    args = argparse.Namespace(
        songmap=str(songmap),
        video=str(video),
        offset=None,
        reference=None,
    )

    assert run(args) == 0

    updated = json.loads(songmap.read_text(encoding="utf-8"))
    media = updated["media"]["video"]

    assert media["file"] == "video.wav"
    assert abs(media["offset"] - 2.0) < 0.15
    assert media["syncConfidence"] >= 0.90


def test_sync_video_manual_offset(dataset):
    songmap = dataset / "songmap.json"
    video = dataset / "fx" / "intro" / "video.wav"

    args = argparse.Namespace(
        songmap=str(songmap),
        video=str(video),
        offset=7.42,
        reference=None,
    )

    assert run(args) == 0

    updated = json.loads(songmap.read_text(encoding="utf-8"))
    media = updated["media"]["video"]

    assert media["offset"] == 7.42
    assert media["syncConfidence"] == 1.0


def test_sync_video_missing_files(tmp_path):
    args = argparse.Namespace(
        songmap=str(tmp_path / "nope.json"),
        video=str(tmp_path / "nope.mp4"),
        offset=None,
        reference=None,
    )

    assert run(args) == 1


def test_sync_video_keeps_timing_untouched(dataset):
    songmap = dataset / "songmap.json"
    video = dataset / "fx" / "intro" / "video.wav"

    before = json.loads(songmap.read_text(encoding="utf-8"))

    args = argparse.Namespace(
        songmap=str(songmap),
        video=str(video),
        offset=None,
        reference=None,
    )

    assert run(args) == 0

    after = json.loads(songmap.read_text(encoding="utf-8"))

    assert after["timing"] == before["timing"]
    assert after["beats"] == before["beats"]


def test_sync_video_with_count_in_uses_song_start(tmp_path):
    """A reference with a count-in the video lacks syncs with a negative
    offset when the SongMap carries ``timing.songStart``."""

    import shutil

    from octobeat.models.timing import Beat, TempoSegment, TimingData

    build_video_sync_fixtures(tmp_path / "fx")

    dataset = tmp_path / "count-in-dataset"
    dataset.mkdir(parents=True)

    shutil.copy(
        tmp_path / "fx" / "count-in" / "reference.wav",
        dataset / "recording.wav",
    )

    timing = TimingData(
        tempos=[TempoSegment(start_beat=1, start_time=0.0, bpm=120.0)],
        beats=[Beat(index=1, time=0.0)],
        time_signatures=[],
        sections=[],
    )

    songmap = build_songmap(
        timing,
        title="Count In",
        duration=6.0,
        source=Source(type="file", id="x"),
        source_kind="sng",
        generated_by="test",
        created_at="2026-08-10T00:00:00+00:00",
        song_start=2.0,
        count_in_start=0.5,
    )

    assert songmap.timing.songStart == 2.0
    assert songmap.timing.countInStart == 0.5

    write_songmap(songmap, dataset / "songmap.json")

    video = tmp_path / "fx" / "count-in" / "video.wav"

    args = argparse.Namespace(
        songmap="count-in-dataset",
        video=str(video),
        offset=None,
        reference=None,
        output=tmp_path,
    )

    assert run(args) == 0

    updated = json.loads(
        (dataset / "songmap.json").read_text(encoding="utf-8"),
    )

    media = updated["media"]["video"]
    assert abs(media["offset"] - (-2.0)) < 0.15
    assert media["syncConfidence"] >= 0.90


def test_sync_video_dataset_by_id(tmp_path):
    """Dataset mode: resolve by id/prefix, video copied is not needed
    (a local video path is used directly)."""

    import shutil

    from octobeat.core.songmap_builder import build_songmap
    from octobeat.models.songmap import Source
    from octobeat.models.timing import Beat, TempoSegment, TimingData
    from octobeat.pipeline.datasets import find_dataset

    build_video_sync_fixtures(tmp_path / "fx")

    dataset = tmp_path / "mxpx-responsibility-abcd123456"
    dataset.mkdir(parents=True)

    shutil.copy(
        tmp_path / "fx" / "intro" / "reference.wav",
        dataset / "recording.wav",
    )

    timing = TimingData(
        tempos=[TempoSegment(start_beat=1, start_time=0.0, bpm=120.0)],
        beats=[Beat(index=1, time=0.0)],
        time_signatures=[],
        sections=[],
    )

    songmap = build_songmap(
        timing,
        title="Responsibility",
        duration=6.0,
        source=Source(type="file", id="x"),
        source_kind="sng",
        generated_by="test",
        created_at="2026-08-10T00:00:00+00:00",
    )

    write_songmap(songmap, dataset / "songmap.json")

    # Unique prefix resolution.
    resolved = find_dataset(tmp_path, "mxpx-responsibility")
    assert resolved == dataset.resolve()

    video = tmp_path / "fx" / "intro" / "video.wav"

    args = argparse.Namespace(
        songmap="mxpx-responsibility",
        video=str(video),
        offset=None,
        reference=None,
        output=tmp_path,
    )

    assert run(args) == 0

    updated = json.loads(
        (dataset / "songmap.json").read_text(encoding="utf-8"),
    )

    media = updated["media"]["video"]
    assert abs(media["offset"] - 2.0) < 0.15
    assert media["syncConfidence"] >= 0.90


def test_sync_video_dataset_not_found(tmp_path, capsys):
    args = argparse.Namespace(
        songmap="does-not-exist",
        video="/tmp/x.mp4",
        offset=None,
        reference=None,
        output=tmp_path,
    )

    assert run(args) == 1
    out = capsys.readouterr().out
    assert "not found" in out.lower()


def test_sync_video_updates_metadata_and_catalog(tmp_path):
    """Attaching a video must also reflect in metadata.json + catalog."""

    import shutil

    from octobeat.models.metadata import CatalogMetadata, ResourceRefs

    build_video_sync_fixtures(tmp_path / "fx")

    dataset = tmp_path / "mxpx-responsibility-abcd123456"
    dataset.mkdir(parents=True)

    shutil.copy(
        tmp_path / "fx" / "intro" / "reference.wav",
        dataset / "recording.wav",
    )

    _minimal_songmap(dataset / "songmap.json")

    # Write metadata without a video.
    metadata = CatalogMetadata(
        id="mxpx-responsibility-abcd123456",
        title="Responsibility",
        artist="MxPx",
        bpm=120.0,
        duration=6.0,
        resources=ResourceRefs(
            audio="recording.webm",
        ),
    )

    (dataset / "metadata.json").write_text(
        metadata.model_dump_json(indent=2),
        encoding="utf-8",
    )

    from octobeat.io.resource import upsert_catalog

    upsert_catalog(
        tmp_path / "catalog.json",
        metadata,
    )

    video = tmp_path / "fx" / "intro" / "video.wav"

    args = argparse.Namespace(
        songmap="mxpx-responsibility",
        video=str(video),
        offset=None,
        reference=None,
        output=tmp_path,
    )

    assert run(args) == 0

    md = json.loads(
        (dataset / "metadata.json").read_text(encoding="utf-8"),
    )
    assert md["resources"]["video"] == "video.wav"

    catalog = json.loads(
        (tmp_path / "catalog.json").read_text(encoding="utf-8"),
    )
    assert catalog[0]["resources"]["video"] == "video.wav"
