from __future__ import annotations

import argparse
import json
from pathlib import Path

from octobeat.commands.catalog import run
from octobeat.core.songmap_builder import build_songmap
from octobeat.io.resource import upsert_catalog
from octobeat.io.songmap import write_songmap
from octobeat.models.metadata import CatalogMetadata, ResourceRefs
from octobeat.models.songmap import Source
from octobeat.models.timing import Beat, TempoSegment, TimingData


def _make_dataset(
    directory: Path,
    *,
    dataset_id: str,
    title: str,
    artist: str = "Artist",
) -> None:
    directory.mkdir(parents=True, exist_ok=True)

    timing = TimingData(
        tempos=[TempoSegment(start_beat=1, start_time=0.0, bpm=120.0)],
        beats=[Beat(index=1, time=0.0)],
        time_signatures=[],
        sections=[],
    )

    songmap = build_songmap(
        timing,
        title=title,
        duration=10.0,
        source=Source(type="file", id=dataset_id),
        source_kind="sng",
        generated_by="test",
        created_at="2026-08-10T00:00:00+00:00",
    )

    write_songmap(songmap, directory / "songmap.json")

    metadata = CatalogMetadata(
        id=dataset_id,
        title=title,
        artist=artist,
        bpm=120.0,
        duration=10.0,
        resources=ResourceRefs(
            audio="recording.webm",
        ),
    )

    (directory / "metadata.json").write_text(
        metadata.model_dump_json(indent=2),
        encoding="utf-8",
    )


def _args(
    command: str,
    output: Path,
) -> argparse.Namespace:
    return argparse.Namespace(
        catalog_command=command,
        output=output,
        catalog=None,
    )


def test_catalog_build_scans_datasets(tmp_path):
    _make_dataset(
        tmp_path / "aaa-song-one-1111111111",
        dataset_id="aaa-song-one-1111111111",
        title="Song One",
    )
    _make_dataset(
        tmp_path / "bbb-song-two-2222222222",
        dataset_id="bbb-song-two-2222222222",
        title="Song Two",
    )

    assert run(_args("build", tmp_path)) == 0

    entries = json.loads(
        (tmp_path / "catalog.json").read_text(encoding="utf-8"),
    )

    assert {entry["id"] for entry in entries} == {
        "aaa-song-one-1111111111",
        "bbb-song-two-2222222222",
    }



def test_catalog_build_ignores_removed_datasets(tmp_path):
    _make_dataset(
        tmp_path / "aaa-keep-1111111111",
        dataset_id="aaa-keep-1111111111",
        title="Keep",
    )
    _make_dataset(
        tmp_path / "bbb-remove-2222222222",
        dataset_id="bbb-remove-2222222222",
        title="Remove",
    )

    # A stale catalog that still lists both.
    upsert_catalog(
        tmp_path / "catalog.json",
        CatalogMetadata(
            id="bbb-remove-2222222222",
            title="Remove",
            artist="Artist",
            bpm=120.0,
            duration=10.0,
            resources=ResourceRefs(audio="recording.webm"),
        ),
    )

    # The user removes the second dataset directory.
    import shutil

    shutil.rmtree(tmp_path / "bbb-remove-2222222222")

    assert run(_args("build", tmp_path)) == 0

    entries = json.loads(
        (tmp_path / "catalog.json").read_text(encoding="utf-8"),
    )

    assert {entry["id"] for entry in entries} == {
        "aaa-keep-1111111111",
    }


def test_catalog_verify_detects_stale_entries(tmp_path):
    _make_dataset(
        tmp_path / "aaa-keep-1111111111",
        dataset_id="aaa-keep-1111111111",
        title="Keep",
    )

    # Catalog lists an entry whose dataset directory does not exist.
    upsert_catalog(
        tmp_path / "catalog.json",
        CatalogMetadata(
            id="zzz-gone-9999999999",
            title="Gone",
            artist="Artist",
            bpm=120.0,
            duration=10.0,
            resources=ResourceRefs(audio="recording.webm"),
        ),
    )

    assert run(_args("verify", tmp_path)) == 1


def test_catalog_stats_counts(tmp_path):
    _make_dataset(
        tmp_path / "aaa-song-1111111111",
        dataset_id="aaa-song-1111111111",
        title="Song",
    )

    upsert_catalog(
        tmp_path / "catalog.json",
        CatalogMetadata(
            id="aaa-song-1111111111",
            title="Song",
            artist="Artist",
            bpm=120.0,
            duration=10.0,
            resources=ResourceRefs(audio="recording.webm"),
        ),
    )

    assert run(_args("stats", tmp_path)) == 0


def test_catalog_build_omits_null_optionals(tmp_path):
    """Optional fields must not be serialized as null.

    The web frontend (zod) rejects explicit nulls for optional metadata
    fields, so catalog build must exclude them.
    """

    _make_dataset(
        tmp_path / "aaa-song-1111111111",
        dataset_id="aaa-song-1111111111",
        title="Song",
    )

    # The dataset metadata has unset optional fields.
    (tmp_path / "aaa-song-1111111111" / "metadata.json").write_text(
        CatalogMetadata(
            id="aaa-song-1111111111",
            title="Song",
            artist="Artist",
            bpm=120.0,
            duration=10.0,
            resources=ResourceRefs(audio="recording.webm"),
        ).model_dump_json(indent=2),
        encoding="utf-8",
    )

    assert run(_args("build", tmp_path)) == 0

    entries = json.loads(
        (tmp_path / "catalog.json").read_text(encoding="utf-8"),
    )

    entry = entries[0]
    assert "album" not in entry
    assert "year" not in entry
    assert "difficulty" not in entry
    assert "youtube" not in entry
