from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from octobeat.charts import find_chart
from octobeat.config.model import Config
from octobeat.core.analyser import (
    analyse_recording,
    analyse_with_chart,
)
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
    TimingProvenance,
)
from octobeat.models.recording import Recording
from octobeat.naming import dataset_slug
from octobeat.providers.deezer import (
    DeezerMetadata,
    DeezerProvider,
)
from octobeat.providers.factory import get_provider
from octobeat.providers.youtube import YouTubeProvider
from octobeat.timing import (
    TimingData,
    TimingError,
    TimingProvider,
    get_timing_provider,
)
from octobeat.ui import console


class DatasetExistsError(Exception):
    """
    Raised when the target dataset directory already exists.

    The default ``add`` behaviour is to never overwrite an existing
    dataset; the caller must explicitly request ``overwrite=True`` to
    replace it. No interactive confirmation is offered.
    """

    def __init__(
        self,
        dataset_dir: Path,
    ) -> None:
        super().__init__(
            f"Dataset directory already exists: {dataset_dir}",
        )
        self.dataset_dir = dataset_dir


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
    include_cover: bool = True,
    update_catalog: bool = True,
    offset: float | None = None,
    overwrite: bool = False,
) -> BuildResult:
    """
    Build a complete dataset from a recording source.

    Runs the full pipeline: acquire the recording, analyse it, fetch
    the cover artwork when the source supports them, write the dataset
    and update the catalog.

    ``offset`` overrides the detected music start (seconds into the
    media where the actual song begins).

    By default an existing dataset directory is never replaced: when
    ``overwrite`` is false and the target directory already exists a
    :class:`DatasetExistsError` is raised without touching anything. No
    interactive prompt is shown.
    """

    provider = get_provider(source)

    recording = provider.load(source)

    deezer = DeezerProvider()

    try:
        dataset_id = (
            dataset_id
            or dataset_slug(recording)
        )

        dataset_dir = (
            output
            / dataset_id
        )

        if not overwrite and dataset_dir.exists():
            raise DatasetExistsError(dataset_dir)

        result = _analyse(recording, source, offset)

        cover_source: str | None = None

        if (
            include_cover
            and isinstance(provider, YouTubeProvider)
        ):
            cover_source = _download_cover(
                recording,
                dataset_dir / "cover.jpg",
                provider,
                source,
                deezer,
            )

        cover_path = (
            _write_embedded_cover(
                recording,
                dataset_dir / "cover.jpg",
            )
            if recording.cover_bytes is not None
            else None
        )

        if cover_path is not None:
            cover_source = "sng"

        songmap = result.songmap

        metadata = _build_metadata(
            recording,
            dataset_id,
            result,
            deezer,
        )

        write_resource(
            dataset_dir,
            songmap=songmap,
            metadata=metadata,
            audio=recording.path,
            cover=cover_path,
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
            audio="recording.mp3",
            cover_source=cover_source,
            duration=result.report.duration,
            bpm=result.report.bpm,
            beats=result.report.beats,
            confidence=result.report.confidence,
        )
    finally:
        recording.cleanup()


def _analyse(
    recording: Recording,
    source: str,
    offset: float | None,
    *,
    config: Config | None = None,
) -> AnalysisResult:
    """
    Analyse a recording, preferring a community chart when one matches.

    Falls back to audio analysis when no chart is found or the chart is
    unusable (the dataset must still build from audio).
    """

    # A provider may attach a chart directly (e.g. an SNG container).
    chart = recording.chart_path

    if chart is None:
        chart = find_chart(
            recording,
            config=config
            or _default_config(),
        )

    if chart is not None:
        console.info(
            f"Found community chart: {chart.name}",
        )

        try:
            chart_timing = _load_chart_timing(chart)
            return analyse_with_chart(
                recording,
                chart_timing,
                provider="chart",
                source=str(chart),
                chart_source=_chart_kind(chart),
            )
        except (TimingError, FileNotFoundError) as error:
            console.warning(
                f"Community chart could not be parsed ({error}); "
                "falling back to audio analysis.",
            )
    else:
        console.info(
            "No community chart found; using audio analysis.",
        )

    return analyse_recording(
        recording,
        provider="local",
        source=source,
        offset=offset,
    )


def _load_chart_timing(chart: Path) -> TimingData:
    provider: TimingProvider = get_timing_provider(str(chart))
    return provider.load(str(chart))


def _chart_kind(chart: Path) -> str:
    suffix = chart.suffix.lower()

    if suffix == ".mid":
        return "midi"

    if suffix == ".chart":
        return "chart"

    return "sng"


def _default_config() -> Config:
    from octobeat.config import ensure_workspace

    return ensure_workspace()


def _write_embedded_cover(
    recording: Recording,
    destination: Path,
) -> Path | None:
    """Write the cover embedded in the source (SNG) as cover.jpg.

    Returns the destination path, or ``None`` when there is no cover.
    """

    if recording.cover_bytes is None:
        return None

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination.write_bytes(
        recording.cover_bytes,
    )

    return destination


def _build_metadata(
    recording: Recording,
    dataset_id: str,
    result: AnalysisResult,
    deezer: DeezerProvider,
) -> CatalogMetadata:
    """
    Build catalogue metadata from the analysis result.
    """

    songmap = result.songmap

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
            and enriched.album
            else recording.album
        ),
        year=(
            enriched.year
            if enriched is not None
            and enriched.year is not None
            else recording.year
        ),
        genres=(
            enriched.genres
            if enriched is not None
            and enriched.genres
            else (recording.genres or [])
        ),
        bpm=songmap.timing.bpm,
        duration=songmap.metadata.duration,
        timeSignature=songmap.timing.timeSignature,
        timing=TimingProvenance(
            source=songmap.timing.source or "audio-analysis",
            confidence=songmap.timing.confidence,
        ),
        tags=(
            enriched.tags
            if enriched is not None
            else []
        ),
        resources=ResourceRefs(
            audio="recording.mp3",
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
