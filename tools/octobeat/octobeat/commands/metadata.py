from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from octobeat.config import ensure_workspace
from octobeat.io.resource import (
    COVER_FILE,
    METADATA_FILE,
    upsert_catalog,
    write_metadata,
)
from octobeat.models.metadata import (
    CatalogMetadata,
    ResourceRefs,
)
from octobeat.pipeline.datasets import (
    catalog_path,
    find_dataset,
)
from octobeat.providers.deezer import (
    DeezerMetadata,
    DeezerProvider,
)
from octobeat.ui import console


def run(args: argparse.Namespace) -> int:
    """
    Generate metadata.
    """

    if args.metadata_command == "fetch":
        return _fetch(args)

    if args.metadata_command == "youtube":
        console.failure(
            "metadata youtube is not implemented.",
        )

        return 1

    console.failure(
        f"metadata {args.metadata_command} is not implemented.",
    )

    return 1


def _fetch(args: argparse.Namespace) -> int:
    """
    Fetch Deezer metadata and album cover for a dataset.

    The dataset identity comes from its metadata.json; when the
    artist/title are missing or ambiguous, the user is asked to
    confirm or correct them interactively.
    """

    config = ensure_workspace()

    output = (
        args.output.expanduser().resolve()
        if args.output is not None
        else config.datasets_dir()
    )

    dataset_dir = find_dataset(
        output,
        args.dataset,
    )

    if dataset_dir is None:
        console.failure(
            f"Dataset '{args.dataset}' not found in {output}.",
        )

        return 1

    provider = DeezerProvider()

    try:
        return _fetch_for_dataset(
            dataset_dir,
            provider,
            interactive=(
                not args.no_interactive
            ),
        )
    except KeyboardInterrupt:
        console.blank()
        console.failure("Aborted.")
        return 1


def _fetch_for_dataset(
    dataset_dir: Path,
    provider: DeezerProvider,
    *,
    interactive: bool,
) -> int:
    """
    Fetch and write metadata + cover for a single dataset.
    """

    dataset_id = dataset_dir.name

    metadata = _load_metadata(
        dataset_dir,
    )

    artist, title = _identity(
        metadata,
        interactive,
    )

    if not artist or not title:
        console.failure(
            "No artist/title available for "
            f"'{dataset_id}'.",
        )

        return 1

    tracks = provider.tracks(
        artist,
        title,
    )

    track = _pick_track(
        tracks,
        artist,
        interactive,
    )

    if track is None:
        console.warning(
            f"No matching track found for "
            f"{artist} - {title}.",
        )

        return 1

    enriched = provider.metadata_for_track(
        track,
    )

    if enriched is None:
        console.failure(
            "Deezer returned no metadata.",
        )

        return 1

    updated = _merge_metadata(
        metadata,
        enriched,
        dataset_id,
    )

    write_metadata(
        updated,
        dataset_dir / METADATA_FILE,
    )

    cover = _fetch_cover(
        provider,
        track,
        dataset_dir / COVER_FILE,
    )

    console.table_report(
        [
            (
                "Dataset",
                [
                    ("ID", dataset_id),
                    ("Artist", updated.artist),
                    ("Title", updated.title),
                    ("Album", updated.album or "-"),
                    ("Year", updated.year or "-"),
                    ("Genres", ", ".join(updated.genres) or "-"),
                ],
            ),
            (
                "Output",
                [
                    ("Metadata", dataset_dir / METADATA_FILE),
                    (
                        "Cover",
                        cover if cover is not None else "-",
                    ),
                ],
            ),
        ],
        title=f"octobeat metadata fetch ({dataset_id})",
    )

    upsert_catalog(
        catalog_path(dataset_dir.parent),
        updated,
    )

    console.success(
        "Metadata updated.",
    )

    return 0


def _load_metadata(
    dataset_dir: Path,
) -> CatalogMetadata:
    metadata_path = (
        dataset_dir / METADATA_FILE
    )

    if metadata_path.exists():
        try:
            return CatalogMetadata.model_validate_json(
                metadata_path.read_text(
                    encoding="utf-8",
                ),
            )
        except Exception:
            pass

    return _blank_metadata(
        dataset_dir,
    )


def _blank_metadata(
    dataset_dir: Path,
) -> CatalogMetadata:
    return CatalogMetadata(
        id=dataset_dir.name,
        title="",
        artist="",
        genres=[],
        tags=[],
        bpm=120.0,
        duration=0.0,
        resources=ResourceRefs(
            audio="recording.wav",
        ),
    )


def _identity(
    metadata: CatalogMetadata,
    interactive: bool,
) -> tuple[str, str]:
    """
    Determine the artist and title to search for.

    The artist field is authoritative when present; otherwise a
    "Artist: Title" or "Artist - Title" title is split into parts.
    Rip/quality suffixes (e.g. " - DVDrip") are stripped from the
    title. Missing parts are suggested to the user, who can accept
    with an empty input.
    """

    artist = metadata.artist or ""
    title = _strip_rip_suffix(
        metadata.title or "",
    )

    suggested_artist, suggested_title = (
        _suggest_identity(
            CatalogMetadata(
                **{
                    **metadata.model_dump(),
                    "title": title,
                }
            )
        )
    )

    # Only derive the artist from the title when it is missing.
    if not artist and suggested_artist:
        artist = suggested_artist
        title = suggested_title or title

    if (not artist or not title) and interactive:
        console.info(
            f"Dataset '{metadata.id}' has no artist/title.",
        )

        artist = console.prompt(
            "Artist",
            default=artist or None,
        )

        title = console.prompt(
            "Title",
            default=title or None,
        )

    return artist, title


def _strip_rip_suffix(
    title: str,
) -> str:
    """
    Remove rip/quality suffixes from a title, e.g. the "DVDrip" in
    "Anthem Of Our Dying Day - DVDrip".
    """

    return re.sub(
        r"\s*[-–—]\s*(?:(?:DVD|BR|BD|HD|HDTV|WEB|WEBRip|BluRay|CAM|TS|R5)[- ]?Rip|"
        r"1080p|720p|2160p|4K)\s*$",
        "",
        title,
        flags=re.IGNORECASE,
    ).strip()


def _suggest_identity(
    metadata: CatalogMetadata,
) -> tuple[str | None, str | None]:
    """
    Attempt to split "Artist: Title" or "Artist - Title" metadata
    titles into separate artist and title parts.
    """

    title = (metadata.title or "").strip()

    if not title:
        return None, None

    for separator in (
        ": ",
        " — ",
        " - ",
    ):
        if separator in title:
            artist, _, song = title.partition(
                separator,
            )

            artist = artist.strip()
            song = song.strip()

            if artist and song:
                return artist, song

    return None, title or None


def _pick_track(
    tracks: list[dict[str, Any]],
    artist: str,
    interactive: bool,
) -> dict[str, Any] | None:
    """
    Choose the best Deezer track for the recording.

    ``tracks`` is already ordered by popularity with exact artist
    matches first. When interactive and there are multiple plausible
    candidates, the user picks one; otherwise the best match is used.
    """

    if not tracks:
        return None

    if not interactive or len(tracks) == 1:
        return tracks[0]

    options = [
        _track_label(track)
        for track in tracks
    ]

    choice = console.choose(
        "Which track is this?",
        options,
    )

    if choice is None:
        return None

    return tracks[choice]


def _track_label(
    track: dict[str, Any],
) -> str:
    artist = str(
        (
            track.get("artist")
            or {}
        ).get("name")
        or "?"
    )

    title = str(
        track.get("title")
        or "?"
    )

    album = str(
        (
            track.get("album")
            or {}
        ).get("title")
        or ""
    )

    if album:
        return f"{artist} — {title} ({album})"

    return f"{artist} — {title}"


def _merge_metadata(
    metadata: CatalogMetadata,
    enriched: DeezerMetadata,
    dataset_id: str,
) -> CatalogMetadata:
    """
    Merge Deezer enrichment into the existing dataset metadata.

    Deezer values win for artist, title, album, year, genres and
    tags; everything else (bpm, difficulty, resources) is preserved.
    """

    return metadata.model_copy(
        update={
            "id": dataset_id,
            "artist": enriched.artist or metadata.artist,
            "title": enriched.title or metadata.title,
            "album": (
                enriched.album
                or metadata.album
            ),
            "year": (
                enriched.year
                or metadata.year
            ),
            "genres": (
                enriched.genres
                or metadata.genres
            ),
            "tags": (
                enriched.tags
                or metadata.tags
            ),
        },
    )


def _fetch_cover(
    provider: DeezerProvider,
    track: dict[str, Any],
    destination: Path,
) -> Path | None:
    """
    Download the album cover of the chosen track, best effort.
    """

    try:
        return provider.download_cover_for_track(
            track,
            destination,
        )
    except Exception as error:
        console.warning(
            f"Cover download failed: {error}",
        )

        return None
