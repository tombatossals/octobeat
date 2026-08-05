from __future__ import annotations

import argparse
import traceback
from pathlib import Path

from octobeat.core.analyser import analyse_recording
from octobeat.io.resource import (
    CATALOG_FILE,
    COVER_FILE,
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
from octobeat.providers.cover import DeezerCoverProvider
from octobeat.providers.factory import get_provider
from octobeat.providers.youtube import YouTubeProvider
from octobeat.ui import console

DEFAULT_CATALOG = Path(CATALOG_FILE)


def run(args: argparse.Namespace) -> int:
    """
    Acquire media, analyse it and write a complete resource dataset.
    """

    provider = get_provider(args.input)

    recording = provider.load(args.input)

    try:
        result = analyse_recording(
            recording,
            provider=type(provider).__name__,
            source=args.input,
        )

        dataset_id = (
            args.id or dataset_slug(recording)
        )

        dataset_dir = (
            args.output
            / dataset_id
        )

        video_path: Path | None = None
        cover_path: Path | None = None
        cover_source: str | None = None

        if isinstance(
            provider,
            YouTubeProvider,
        ):
            video_path = (
                provider.download_video(
                    args.input,
                    dataset_dir
                    / "video.mp4",
                )
            )

            cover_path, cover_source = (
                _download_cover(
                    recording,
                    dataset_dir
                    / COVER_FILE,
                    provider,
                    args.input,
                )
            )

        metadata = _build_metadata(
            recording,
            dataset_id,
            result,
            video_path,
        )

        write_resource(
            dataset_dir,
            songmap=result.songmap,
            metadata=metadata,
            audio=recording.path,
            video=video_path,
            cover=cover_path,
        )

        catalog_path = (
            args.catalog
            or args.output
            / DEFAULT_CATALOG
        )

        entries = upsert_catalog(
            catalog_path,
            metadata,
        )

        console.title("octobeat Resource")
        console.field(
            "Dataset",
            dataset_id,
        )
        console.field(
            "Directory",
            dataset_dir,
        )
        console.field(
            "Catalog",
            catalog_path,
        )
        console.field(
            "Catalog entries",
            len(entries),
        )
        console.field(
            "SongMap",
            dataset_dir / SONGMAP_FILE,
        )
        console.field(
            "Metadata",
            dataset_dir / METADATA_FILE,
        )

        if video_path is not None:
            console.field(
                "Video",
                video_path.name,
            )

        if cover_source is not None:
            console.field(
                "Cover",
                cover_source,
            )

        console.blank()
        console.success(
            "Resource generated.",
        )

        return 0

    except Exception:
        traceback.print_exc()

        return 1

    finally:
        recording.cleanup()


def _build_metadata(
    recording: Recording,
    dataset_id: str,
    result: AnalysisResult,
    video_path: Path | None,
) -> CatalogMetadata:
    """
    Build catalogue metadata from the analysis result.
    """

    songmap = result.songmap

    youtube_id = (
        songmap.metadata.source.id
        if songmap.metadata.source.type
        == "youtube"
        else None
    )

    return CatalogMetadata(
        id=dataset_id,
        title=recording.title
        or songmap.metadata.title,
        artist=recording.artist or "",
        bpm=songmap.timing.bpm,
        duration=songmap.metadata.duration,
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


def _download_cover(
    recording: Recording,
    destination: Path,
    youtube: YouTubeProvider,
    source: str,
) -> tuple[Path, str]:
    """
    Download the best available album cover.

    Prefers the Deezer album artwork (higher quality, square) and
    falls back to the YouTube video thumbnail when it is missing.
    """

    if recording.artist and recording.title:
        try:
            return (
                DeezerCoverProvider().download(
                    recording.artist,
                    recording.title,
                    destination,
                ),
                "deezer",
            )
        except Exception:
            pass

    return (
        youtube.download_thumbnail(
            source,
            destination,
        ),
        "youtube",
    )
