from __future__ import annotations

import json
import shutil
from pathlib import Path

from octobeat.audio import encode_to_webm
from octobeat.io.songmap import write_songmap
from octobeat.models.metadata import CatalogMetadata
from octobeat.models.songmap import SongMap

RECORDING_WAV = "recording.wav"
RECORDING_WEBM = "recording.webm"
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
    video: Path | None = None,
    cover: Path | None = None,
    include_webm: bool = True,
) -> Path:
    """
    Write a complete resource dataset into `dataset_dir`.

    Produces the canonical OctoBeat layout:

        songmap.json
        metadata.json
        recording.wav
        recording.webm
        video.<ext>
        cover.jpg

    `audio` is copied as recording.wav and (optionally) encoded to
    recording.webm. `video` and `cover` are copied when provided.
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

    shutil.copy2(
        audio,
        dataset_dir / RECORDING_WAV,
    )

    if include_webm:
        encode_to_webm(
            audio,
            dataset_dir / RECORDING_WEBM,
        )

    if video is not None:
        video_target = (
            dataset_dir / video.name
        )

        if (
            video.resolve()
            != video_target.resolve()
        ):
            shutil.copy2(
                video,
                video_target,
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
