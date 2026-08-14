"""Re-analysis of existing datasets.

Regenerates the SongMap of every dataset in a directory using the
current analysis engine, then refreshes the metadata and the catalog
so the library reflects the new analysis.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from octobeat.core.analyser import analyse_recording
from octobeat.io.resource import (
    CATALOG_FILE,
    METADATA_FILE,
    RECORDING_MP3,
    RECORDING_WAV,
    SONGMAP_FILE,
    upsert_catalog,
    write_metadata,
)
from octobeat.io.songmap import read_songmap, write_songmap
from octobeat.models.analysis import AnalysisResult
from octobeat.models.metadata import CatalogMetadata
from octobeat.models.recording import Recording
from octobeat.models.songmap import Source
from octobeat.providers.factory import get_provider


@dataclass(slots=True)
class ReanalysisResult:
    """
    Result of re-analysing a single dataset.
    """

    dataset_id: str

    dataset_dir: Path

    bpm: float

    beats: int

    confidence: float

    changed: bool


@dataclass(slots=True)
class ReanalysisSummary:
    """
    Summary of a batch re-analysis.
    """

    reanalysed: list[ReanalysisResult]

    failed: list[tuple[str, str]]

    def __post_init__(self) -> None:
        self.reanalysed.sort(
            key=lambda result: result.dataset_id,
        )


def reanalyse_datasets(
    output: Path,
    *,
    catalog: Path | None = None,
    offset: float | None = None,
) -> ReanalysisSummary:
    """
    Re-analyse every dataset inside ``output``.

    Each directory containing a `songmap.json` is re-analysed from its
    decoded audio (`recording.mp3`). The new SongMap is written in
    place, and the dataset metadata plus the catalog are refreshed with
    the updated BPM, duration and confidence.
    """

    output = output.expanduser().resolve()

    catalog_path = (
        catalog.expanduser().resolve()
        if catalog is not None
        else output / CATALOG_FILE
    )

    reanalysed: list[ReanalysisResult] = []
    failed: list[tuple[str, str]] = []

    for dataset_dir in sorted(
        output.iterdir(),
    ):
        if not dataset_dir.is_dir():
            continue

        songmap_path = (
            dataset_dir / SONGMAP_FILE
        )

        if not songmap_path.exists():
            continue

        dataset_id = dataset_dir.name

        try:
            result = _reanalyse_dataset(
                dataset_dir,
                songmap_path,
                catalog_path,
                offset=offset,
            )
        except Exception as error:
            failed.append(
                (dataset_id, str(error)),
            )
            continue

        reanalysed.append(result)

    return ReanalysisSummary(
        reanalysed=reanalysed,
        failed=failed,
    )


def _reanalyse_dataset(
    dataset_dir: Path,
    songmap_path: Path,
    catalog_path: Path,
    *,
    offset: float | None,
) -> ReanalysisResult:
    """
    Re-analyse a single dataset directory.
    """

    dataset_id = dataset_dir.name

    audio_path = (
        dataset_dir / RECORDING_MP3
    )

    if not audio_path.exists():
        audio_path = (
            dataset_dir / RECORDING_WAV
        )

    if not audio_path.exists():
        raise FileNotFoundError(
            f"missing {RECORDING_MP3}",
        )

    provider = get_provider(str(audio_path))

    recording = provider.load(str(audio_path))

    _populate_identity(
        recording,
        dataset_dir,
    )

    try:
        result = analyse_recording(
            recording,
            provider=type(provider).__name__,
            source=str(audio_path),
            offset=offset,
        )

        previous = _read_songmap_bpm(
            songmap_path,
        )

        changed = (
            previous is None
            or abs(
                previous
                - result.songmap.timing.bpm
            )
            > 0.05
        )

        write_songmap(
            result.songmap,
            songmap_path,
        )

        _refresh_metadata(
            dataset_dir,
            dataset_id,
            result,
        )

        _refresh_catalog(
            catalog_path,
            dataset_dir,
            dataset_id,
        )

        return ReanalysisResult(
            dataset_id=dataset_id,
            dataset_dir=dataset_dir,
            bpm=result.report.bpm,
            beats=result.report.beats,
            confidence=result.report.confidence,
            changed=changed,
        )

    finally:
        recording.cleanup()


def _populate_identity(
    recording: Recording,
    dataset_dir: Path,
) -> None:
    """
    Restore artist/title from the dataset metadata.

    The decoded audio is stored as "recording.mp3", so the filename
    carries no musical identity. The dataset metadata is used to
    restore artist and title on the recording before analysis.
    """

    metadata_path = (
        dataset_dir / METADATA_FILE
    )

    if not metadata_path.exists():
        return

    try:
        metadata = CatalogMetadata.model_validate_json(
            metadata_path.read_text(
                encoding="utf-8",
            ),
        )
    except Exception:
        return

    if not recording.artist or not recording.title:
        recording.artist = metadata.artist or None
        recording.title = metadata.title or None

    if recording.title in {
        "recording",
        "audio",
    }:
        recording.title = (
            metadata.title
            or recording.title
        )
        recording.artist = (
            metadata.artist
            or recording.artist
        )

    if not recording.source:
        recording.source = Source(
            type="file",
            id=str(
                dataset_dir
                / RECORDING_MP3
            ),
        )


def _refresh_metadata(
    dataset_dir: Path,
    dataset_id: str,
    result: AnalysisResult,
) -> None:
    """
    Refresh metadata.json with the new analysis values.

    The existing metadata is preserved and only the temporal fields
    (bpm, duration, time signature, confidence) are updated.
    """

    metadata_path = (
        dataset_dir / METADATA_FILE
    )

    metadata = CatalogMetadata.model_validate_json(
        metadata_path.read_text(
            encoding="utf-8",
        ),
    )

    updated = metadata.model_copy(
        update={
            "id": dataset_id,
            "bpm": result.songmap.timing.bpm,
            "duration": (
                result.songmap.metadata.duration
            ),
            "timeSignature": (
                result.songmap.timing.timeSignature
            ),
        },
    )

    write_metadata(
        updated,
        metadata_path,
    )


def _refresh_catalog(
    catalog_path: Path,
    dataset_dir: Path,
    dataset_id: str,
) -> None:
    """
    Upsert the dataset entry into the catalog.

    Uses the freshly written metadata.json as the source of truth.
    """

    if not catalog_path.exists():
        return

    metadata_path = (
        dataset_dir / METADATA_FILE
    )

    metadata = CatalogMetadata.model_validate_json(
        metadata_path.read_text(
            encoding="utf-8",
        ),
    )

    upsert_catalog(
        catalog_path,
        metadata,
    )


def _read_songmap_bpm(
    songmap_path: Path,
) -> float | None:
    try:
        songmap = read_songmap(
            songmap_path,
        )
        return songmap.timing.bpm
    except Exception:
        return None
