from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from octobeat.config import ensure_workspace
from octobeat.io.resource import SONGMAP_FILE
from octobeat.io.songmap import read_songmap, write_songmap
from octobeat.pipeline.datasets import find_dataset
from octobeat.providers.youtube import YouTubeProvider
from octobeat.sync import (
    AUTO_CONFIDENCE,
    VideoSyncError,
    VideoSyncResult,
    compute_features,
    extract_video_audio,
    sync_video,
)
from octobeat.sync.engine import attach_video_to_songmap
from octobeat.ui import console

# Reference audio file names inside a dataset.
REFERENCE_AUDIO = (
    "recording.wav",
    "recording.webm",
)


def run(args: argparse.Namespace) -> int:
    """
    Synchronize a video with a SongMap by detecting the video offset.

    Accepts either:
      octobeat sync-video <dataset> <video.mp4|youtube-url>
      octobeat sync-video <songmap.json> <video.mp4>
    """

    songmap_path, dataset_dir = _resolve_songmap(args)

    if songmap_path is None:
        return 1

    video_path = _resolve_video(
        args.video,
        dataset_dir,
    )

    if video_path is None:
        return 1

    songmap = read_songmap(songmap_path)

    reference_path = _reference_audio(dataset_dir or songmap_path.parent)

    if reference_path is None:
        console.error(
            "Could not find the reference audio. Pass --reference.",
        )
        return 1

    console.info("Extracting video audio...")
    try:
        result = _detect(
            reference_path,
            video_path,
            manual_offset=args.offset,
            song_start=(
                songmap.timing.songStart
                or 0.0
            ),
        )
    except VideoSyncError as error:
        console.error(str(error))
        return 1

    console.blank()
    console.section("Video synchronization")
    console.field("Offset", f"{result.offset:.2f} s")
    console.field("Confidence", f"{result.confidence:.2f}")
    console.blank()

    if result.confidence >= AUTO_CONFIDENCE:
        console.success("Video synchronized automatically.")
    elif args.offset is not None:
        console.info("Manual offset applied.")
    else:
        console.warning(
            "Low confidence; review the offset manually.",
        )

    updated = attach_video_to_songmap(
        songmap,
        video_file=video_path.name,
        video_offset=result.offset,
        sync_confidence=result.confidence,
    )

    write_songmap(updated, songmap_path)

    console.success("SongMap updated.")

    if dataset_dir is not None:
        _update_dataset_metadata(
            dataset_dir,
            video_file=video_path.name,
        )

    return 0


def _update_dataset_metadata(
    dataset_dir: Path,
    *,
    video_file: str,
) -> None:
    """Reflect the new video in metadata.json and the catalog.

    The frontend decides whether to render a video player from
    ``metadata.resources.video``, so attaching a video must update it
    too (the SongMap alone is not enough).
    """

    from octobeat.io.resource import (
        CATALOG_FILE,
        METADATA_FILE,
        upsert_catalog,
        write_metadata,
    )
    from octobeat.pipeline.datasets import _read_metadata

    metadata = _read_metadata(dataset_dir)

    if metadata is None:
        return

    from octobeat.models.metadata import ResourceRefs

    metadata = metadata.model_copy(
        update={
            "resources": ResourceRefs(
                audio=metadata.resources.audio,
                video=video_file,
            ),
        },
    )

    write_metadata(
        metadata,
        dataset_dir / METADATA_FILE,
    )

    catalog = (
        dataset_dir.parent
        / CATALOG_FILE
    )

    if catalog.exists():
        upsert_catalog(
            catalog,
            metadata,
        )


def _resolve_songmap(
    args: argparse.Namespace,
) -> tuple[Path | None, Path | None]:
    """Resolve the SongMap path and its dataset directory.

    When the first argument is an existing ``.json`` file it is used
    directly. Otherwise it is treated as a dataset id/prefix resolved
    inside the datasets directory.
    """

    candidate = Path(args.songmap)

    if candidate.suffix.lower() == ".json":
        songmap_path = candidate.expanduser().resolve()
        if not songmap_path.exists():
            console.error(f"SongMap not found: {songmap_path}")
            return None, None
        return songmap_path, songmap_path.parent

    config = ensure_workspace()

    output = (
        args.output.expanduser().resolve()
        if args.output is not None
        else config.datasets_dir()
    )

    dataset_dir = find_dataset(
        output,
        args.songmap,
    )

    if dataset_dir is None:
        console.error(
            f"Dataset '{args.songmap}' not found in {output}.",
        )
        return None, None

    songmap_path = dataset_dir / SONGMAP_FILE

    if not songmap_path.exists():
        console.error(
            f"Dataset '{args.songmap}' has no {SONGMAP_FILE}.",
        )
        return None, None

    return songmap_path, dataset_dir


def _resolve_video(
    video: str,
    dataset_dir: Path | None,
) -> Path | None:
    """Resolve the video argument to a local file.

    A YouTube URL is downloaded into the dataset directory; a local
    path is used as-is. Returns the final local video path.
    """

    url = video.strip()

    if url.startswith(("https://www.youtube.com/", "https://youtu.be/")):
        if dataset_dir is None:
            console.error(
                "A dataset directory is required to download a "
                "YouTube video.",
            )
            return None

        provider = YouTubeProvider()
        destination = dataset_dir / "video.mp4"

        console.info("Downloading video...")

        try:
            provider.download_video(url, destination)
        except Exception as error:
            console.error(
                f"Could not download the video: {error}",
            )
            return None

        return destination

    path = Path(video).expanduser().resolve()

    if not path.exists():
        console.error(f"Video not found: {path}")
        return None

    return path


def _detect(
    reference_path: Path,
    video_path: Path,
    *,
    manual_offset: float | None,
    song_start: float = 0.0,
) -> VideoSyncResult:
    """Detect the offset, or use the manual value when provided."""

    if manual_offset is not None:
        return VideoSyncResult(
            offset=float(manual_offset),
            confidence=1.0,
        )

    with tempfile.TemporaryDirectory(
        prefix="octobeat-video-sync-",
    ) as tmp:
        video_audio = extract_video_audio(
            video_path,
            Path(tmp) / "video.wav",
        )

        console.info("Analysing audio...")

        reference = compute_features(reference_path)
        video_features = compute_features(video_audio)

        console.info("Finding offset...")

        return sync_video(
            reference,
            video_features,
            song_start=song_start,
        )


def _reference_audio(directory: Path) -> Path | None:
    """Locate the reference audio inside a dataset directory."""

    for name in REFERENCE_AUDIO:
        candidate = directory / name

        if candidate.exists():
            return candidate

    return None
