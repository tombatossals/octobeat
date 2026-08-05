from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from octobeat.core.analyser import analyse_recording
from octobeat.io.resource import (
    CATALOG_FILE,
    METADATA_FILE,
    SONGMAP_FILE,
    upsert_catalog,
    write_resource,
)
from octobeat.models.analysis import AnalysisResult
from octobeat.models.metadata import (
    CatalogMetadata,
    ResourceRefs,
)
from octobeat.models.recording import Recording
from octobeat.naming import dataset_slug
from octobeat.providers.deezer import (
    DeezerMetadata,
    DeezerProvider,
)
from octobeat.providers.factory import get_provider
from octobeat.providers.youtube import YouTubeProvider


@dataclass(slots=True)
class BuildResult:
    """
    Summary of a dataset build.
    """

    provider: str

    source: str

    dataset_id: str

    dataset_dir: Path

    catalog_path: Path

    catalog_entries: int

    songmap_path: Path

    metadata_path: Path

    artist: str | None

    title: str | None

    audio: str

    video: str | None

    cover_source: str | None

    duration: float

    bpm: float

    beats: int

    confidence: float


def build_dataset(
    source: str,
    *,
    output: Path,
    catalog: Path | None = None,
    dataset_id: str | None = None,
    include_video: bool = True,
    include_cover: bool = True,
    update_catalog: bool = True,
) -> BuildResult:
    """
    Build a complete dataset from a recording source.

    Runs the full pipeline: acquire the recording, analyse it, fetch
    the video and cover artwork when the source supports them, write
    the dataset and update the catalog.
    """

    provider = get_provider(source)

    recording = provider.load(source)

    deezer = DeezerProvider()

    try:
        result = analyse_recording(
            recording,
            provider=type(provider).__name__,
            source=source,
        )

        dataset_id = (
            dataset_id
            or dataset_slug(recording)
        )

        dataset_dir = (
            output
            / dataset_id
        )

        video_path: Path | None = None
        cover_source: str | None = None

        if (
            include_video
            and isinstance(provider, YouTubeProvider)
        ):
            video_path = provider.download_video(
                source,
                dataset_dir / "video.mp4",
            )

            if include_cover:
                cover_source = _download_cover(
                    recording,
                    dataset_dir / "cover.jpg",
                    provider,
                    source,
                    deezer,
                )

        metadata = _build_metadata(
            recording,
            dataset_id,
            result,
            video_path,
            deezer,
        )

        write_resource(
            dataset_dir,
            songmap=result.songmap,
            metadata=metadata,
            audio=recording.path,
            video=video_path,
        )

        catalog_path = (
            catalog
            or output / CATALOG_FILE
        )

        catalog_entries = (
            len(
                upsert_catalog(
                    catalog_path,
                    metadata,
                )
            )
            if update_catalog
            else _count_catalog(catalog_path)
        )

        return BuildResult(
            provider=type(provider).__name__,
            source=source,
            dataset_id=dataset_id,
            dataset_dir=dataset_dir,
            catalog_path=catalog_path,
            catalog_entries=catalog_entries,
            songmap_path=dataset_dir / SONGMAP_FILE,
            metadata_path=dataset_dir / METADATA_FILE,
            artist=recording.artist,
            title=recording.title,
            audio="recording.webm",
            video=(
                video_path.name
                if video_path is not None
                else None
            ),
            cover_source=cover_source,
            duration=result.report.duration,
            bpm=result.report.bpm,
            beats=result.report.beats,
            confidence=result.report.confidence,
        )

    finally:
        recording.cleanup()


def _build_metadata(
    recording: Recording,
    dataset_id: str,
    result: AnalysisResult,
    video_path: Path | None,
    deezer: DeezerProvider,
) -> CatalogMetadata:
    """
    Build catalogue metadata from the analysis result.
    """

    songmap = result.songmap

    youtube_id = (
        songmap.metadata.source.id
        if (
            songmap.metadata.source.type
            == "youtube"
        )
        else None
    )

    enriched = _deezer_metadata(
        recording,
        deezer,
    )

    return CatalogMetadata(
        id=dataset_id,
        title=(
            recording.title
            or songmap.metadata.title
        ),
        artist=recording.artist or "",
        album=(
            enriched.album
            if enriched is not None
            else None
        ),
        year=(
            enriched.year
            if enriched is not None
            else None
        ),
        genres=(
            enriched.genres
            if enriched is not None
            else []
        ),
        bpm=songmap.timing.bpm,
        duration=songmap.metadata.duration,
        tags=(
            enriched.tags
            if enriched is not None
            else []
        ),
        youtube=youtube_id,
        resources=ResourceRefs(
            audio="recording.webm",
            video=(
                video_path.name
                if video_path is not None
                else None
            ),
        ),
    )


def _deezer_metadata(
    recording: Recording,
    deezer: DeezerProvider,
) -> DeezerMetadata | None:
    """
    Enrich metadata from Deezer, best effort.
    """

    if not recording.artist or not recording.title:
        return None

    try:
        return deezer.metadata(
            recording.artist,
            recording.title,
        )
    except Exception:
        return None


def _download_cover(
    recording: Recording,
    destination: Path,
    youtube: YouTubeProvider,
    source: str,
    deezer: DeezerProvider,
) -> str:
    """
    Download the best available album cover.

    Prefers the Deezer album artwork (higher quality, square) and
    falls back to the YouTube video thumbnail when it is missing.
    """

    if recording.artist and recording.title:
        try:
            deezer.download_cover(
                recording.artist,
                recording.title,
                destination,
            )
            return "deezer"
        except Exception:
            pass

    youtube.download_thumbnail(
        source,
        destination,
    )

    return "youtube"


def _count_catalog(
    catalog_path: Path,
) -> int:
    if not catalog_path.exists():
        return 0

    return len(
        json.loads(
            catalog_path.read_text(
                encoding="utf-8",
            )
        )
    )
