from __future__ import annotations

import json
import shutil
from pathlib import Path

from octobeat.audio import encode_to_mp3
from octobeat.io.lyrics import (
    LYRICS_FILE,
    write_lyrics,
)
from octobeat.io.songmap import write_songmap
from octobeat.models.metadata import CatalogMetadata
from octobeat.models.songmap import SongMap
from octobeat.models.timing import LyricLine

RECORDING_WAV = "recording.wav"
RECORDING_MP3 = "recording.mp3"
SONGMAP_FILE = "songmap.json"
METADATA_FILE = "metadata.json"
COVER_FILE = "cover.jpg"
CATALOG_FILE = "catalog.json"


def write_resource(
    dataset_dir: Path,
    *,
    songmap: SongMap,
    metadata: CatalogMetadata,
    audio: Path,
    cover: Path | None = None,
    lyrics: list[LyricLine] | None = None,
) -> Path:
    """
    Write a complete resource dataset into `dataset_dir`.

    Produces the canonical OctoBeat layout:

        songmap.json
        metadata.json
        recording.mp3
        cover.jpg
        lyrics.json (when the source provides synced lyrics)

    `audio` is encoded to recording.mp3. `cover` is copied when
    provided. `lyrics` is written to lyrics.json when non-empty.
    """

    dataset_dir = dataset_dir.expanduser().resolve()
    dataset_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_songmap(
        songmap,
        dataset_dir / SONGMAP_FILE,
    )

    write_metadata(
        metadata,
        dataset_dir / METADATA_FILE,
    )

    encode_to_mp3(
        audio,
        dataset_dir / RECORDING_MP3,
    )

    if cover is not None:
        cover_target = (
            dataset_dir / COVER_FILE
        )

        if (
            cover.resolve()
            != cover_target.resolve()
        ):
            shutil.copy2(
                cover,
                cover_target,
            )

    if lyrics:
        write_lyrics(
            lyrics,
            dataset_dir / LYRICS_FILE,
        )

    return dataset_dir


def write_metadata(
    metadata: CatalogMetadata,
    destination: Path,
) -> None:
    """
    Write catalogue metadata as formatted JSON.
    """

    destination = destination.expanduser().resolve()
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination.write_text(
        metadata_to_json(metadata) + "\n",
        encoding="utf-8",
    )


def metadata_to_json(metadata: CatalogMetadata) -> str:
    """
    Serialize catalogue metadata into a formatted JSON document.
    """

    return metadata.model_dump_json(
        indent=2,
        by_alias=True,
        exclude_none=True,
    )


def upsert_catalog(
    catalog_path: Path,
    metadata: CatalogMetadata,
) -> list[CatalogMetadata]:
    """
    Add or replace `metadata` inside the catalog document.

    The catalog is a JSON array of metadata entries. Returns the
    resulting list so callers can report on the change.
    """

    catalog_path = catalog_path.expanduser().resolve()
    catalog_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    entries: list[CatalogMetadata] = []

    if catalog_path.exists():
        entries = [
            CatalogMetadata.model_validate(
                entry,
            )
            for entry in json.loads(
                catalog_path.read_text(
                    encoding="utf-8",
                ),
            )
        ]

    entries = [
        entry
        for entry in entries
        if entry.id != metadata.id
    ]

    entries.append(metadata)

    catalog_path.write_text(
        json.dumps(
            [
                json.loads(
                    metadata_to_json(entry),
                )
                for entry in entries
            ],
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return entries
