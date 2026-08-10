from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import cast

from octobeat.commands.add import run as add
from octobeat.commands.analyse import run as analyse
from octobeat.commands.catalog import run as catalog
from octobeat.commands.config import run as config
from octobeat.commands.dataset import run as dataset
from octobeat.commands.export import run as export
from octobeat.commands.info import run as info
from octobeat.commands.init import run as init
from octobeat.commands.inspect import run as inspect
from octobeat.commands.metadata import run as metadata
from octobeat.commands.sync_video import run as sync_video
from octobeat.commands.validate import run as validate
from octobeat.version import __version__


def not_implemented(_: argparse.Namespace) -> int:
    print("Not implemented yet.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="octobeat",
        description="Build and maintain OctoBeat datasets.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    commands = parser.add_subparsers(
        dest="command",
        required=True,
    )

    #
    # init
    #

    init_parser = commands.add_parser(
        "init",
        help="Initialize an OctoBeat workspace.",
    )

    init_parser.set_defaults(
        func=init,
    )

    #
    # config
    #

    config_parser = commands.add_parser(
        "config",
        help="Manage OctoBeat configuration.",
    )

    config_commands = (
        config_parser.add_subparsers(
            dest="config_command",
            required=True,
        )
    )

    config_commands.add_parser(
        "show",
        help="Show the current configuration.",
    ).set_defaults(func=config)

    config_commands.add_parser(
        "edit",
        help="Edit the configuration file.",
    ).set_defaults(func=config)

    config_set = config_commands.add_parser(
        "set",
        help="Update a configuration value.",
    )

    config_set.add_argument("key")
    config_set.add_argument("value")

    config_set.set_defaults(
        func=config,
    )

    #
    # add
    #

    add_parser = commands.add_parser(
        "add",
        help="Create a complete dataset from a source.",
    )

    add_parser.add_argument(
        "input",
        help="YouTube URL or local recording.",
    )

    add_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Datasets directory (defaults to paths.datasets).",
    )

    add_parser.add_argument(
        "--catalog",
        type=Path,
        help="Catalog file (defaults to <output>/catalog.json).",
    )

    add_parser.add_argument(
        "--id",
        help="Override the dataset identifier.",
    )

    add_parser.add_argument(
        "--no-video",
        action="store_true",
        help="Skip downloading the video track.",
    )

    add_parser.add_argument(
        "--no-cover",
        action="store_true",
        help="Skip downloading the cover artwork.",
    )

    add_parser.add_argument(
        "--offset",
        type=float,
        default=None,
        help="Seconds into the media where the song begins "
        "(overrides auto-detection).",
    )

    add_parser.set_defaults(
        func=add,
    )

    #
    # dataset
    #

    dataset_parser = commands.add_parser(
        "dataset",
        help="Manage datasets.",
    )

    dataset_parser.set_defaults(
        func=dataset,
    )

    dataset_commands = (
        dataset_parser.add_subparsers(
            dest="dataset_command",
            required=True,
        )
    )

    dataset_list = (
        dataset_commands.add_parser(
            "list",
            help="List all datasets.",
        )
    )

    dataset_list.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Datasets directory (defaults to paths.datasets).",
    )

    dataset_list.add_argument(
        "--incomplete",
        action="store_true",
        help="List only datasets with missing essential files/fields.",
    )

    dataset_list.set_defaults(
        func=dataset,
    )

    dataset_commands.add_parser(
        "create",
        help="Create a dataset interactively.",
    ).set_defaults(func=not_implemented)

    dataset_update = (
        dataset_commands.add_parser(
            "update",
            help="Update an existing dataset.",
        )
    )

    dataset_update.add_argument(
        "id",
    )

    dataset_update.set_defaults(
        func=not_implemented,
    )

    dataset_rebuild = (
        dataset_commands.add_parser(
            "rebuild",
            help="Rebuild a dataset.",
        )
    )

    dataset_rebuild.add_argument(
        "id",
    )

    dataset_rebuild.set_defaults(
        func=not_implemented,
    )

    dataset_commands.add_parser(
        "verify",
        help="Verify datasets.",
    ).set_defaults(func=not_implemented)

    dataset_commands.add_parser(
        "clean",
        help="Remove temporary artefacts.",
    ).set_defaults(func=not_implemented)

    dataset_reanalyse = (
        dataset_commands.add_parser(
            "reanalyse",
            help="Re-analyse all datasets with the current engine.",
        )
    )

    dataset_reanalyse.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Datasets directory (defaults to paths.datasets).",
    )

    dataset_reanalyse.add_argument(
        "--offset",
        type=float,
        default=None,
        help="Seconds into the media where the song begins "
        "(overrides auto-detection for all datasets).",
    )

    dataset_reanalyse.set_defaults(
        func=dataset,
    )

    #
    # analyse
    #

    analyse_parser = commands.add_parser(
        "analyse",
        help="Generate a SongMap from a recording.",
    )

    analyse_parser.add_argument(
        "input",
    )

    analyse_parser.add_argument(
        "-o",
        "--output",
        type=Path,
    )

    analyse_parser.add_argument(
        "--title",
    )

    analyse_parser.add_argument(
        "--offset",
        type=float,
        default=None,
        help="Seconds into the media where the song begins "
        "(overrides auto-detection).",
    )

    analyse_parser.add_argument(
        "--chart",
        type=Path,
        default=None,
        help="Structured timing source (.sng/.mid/.chart); the audio "
        "is used for validation and the chart for timing.",
    )

    analyse_parser.add_argument(
        "--debug",
        action="store_true",
        help="Print detailed tempo, phase, grid and confidence "
        "diagnostics.",
    )

    analyse_parser.set_defaults(
        func=analyse,
    )

    #
    # metadata
    #

    metadata_parser = commands.add_parser(
        "metadata",
        help="Generate metadata.",
    )

    metadata_parser.set_defaults(
        func=metadata,
    )

    metadata_commands = (
        metadata_parser.add_subparsers(
            dest="metadata_command",
            required=True,
        )
    )

    metadata_fetch = (
        metadata_commands.add_parser(
            "fetch",
            help="Fetch Deezer metadata and cover for a dataset.",
        )
    )

    metadata_fetch.add_argument(
        "dataset",
        help="Dataset id or unique prefix.",
    )

    metadata_fetch.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Datasets directory (defaults to paths.datasets).",
    )

    metadata_fetch.add_argument(
        "--no-interactive",
        action="store_true",
        help="Never ask questions; pick the best match automatically.",
    )

    metadata_fetch.set_defaults(
        func=metadata,
    )

    metadata_youtube = (
        metadata_commands.add_parser(
            "youtube",
            help="Generate metadata from YouTube.",
        )
    )

    metadata_youtube.add_argument(
        "url",
    )

    metadata_youtube.set_defaults(
        func=metadata,
    )

    #
    # extract
    #

    extract_parser = commands.add_parser(
        "extract",
        help="Extract media.",
    )

    extract_commands = (
        extract_parser.add_subparsers(
            dest="extract_command",
            required=True,
        )
    )

    extract_audio = (
        extract_commands.add_parser(
            "audio",
            help="Extract audio.",
        )
    )

    extract_audio.add_argument(
        "input",
    )

    extract_audio.set_defaults(
        func=not_implemented,
    )

    extract_video = (
        extract_commands.add_parser(
            "video",
            help="Extract video.",
        )
    )

    extract_video.add_argument(
        "input",
    )

    extract_video.set_defaults(
        func=not_implemented,
    )

    #
    # cover
    #

    cover_parser = commands.add_parser(
        "cover",
        help="Download artwork.",
    )

    cover_parser.add_argument(
        "input",
    )

    cover_parser.set_defaults(
        func=not_implemented,
    )

    #
    # catalog
    #

    catalog_parser = commands.add_parser(
        "catalog",
        help="Manage the catalog.",
    )

    catalog_commands = (
        catalog_parser.add_subparsers(
            dest="catalog_command",
            required=True,
        )
    )

    catalog_build = catalog_commands.add_parser(
        "build",
        help="Build catalog.json.",
    )
    catalog_build.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Datasets directory (defaults to paths.datasets).",
    )
    catalog_build.add_argument(
        "--catalog",
        type=Path,
        help="Catalog file (defaults to <output>/catalog.json).",
    )
    catalog_build.set_defaults(func=catalog)

    catalog_verify = catalog_commands.add_parser(
        "verify",
        help="Verify the catalog.",
    )
    catalog_verify.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Datasets directory (defaults to paths.datasets).",
    )
    catalog_verify.add_argument(
        "--catalog",
        type=Path,
        help="Catalog file (defaults to <output>/catalog.json).",
    )
    catalog_verify.set_defaults(func=catalog)

    catalog_stats = catalog_commands.add_parser(
        "stats",
        help="Display catalog statistics.",
    )
    catalog_stats.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Datasets directory (defaults to paths.datasets).",
    )
    catalog_stats.add_argument(
        "--catalog",
        type=Path,
        help="Catalog file (defaults to <output>/catalog.json).",
    )
    catalog_stats.set_defaults(func=catalog)

    #
    # validate
    #

    validate_parser = commands.add_parser(
        "validate",
        help="Validate a SongMap.",
    )

    validate_parser.add_argument(
        "input",
        type=Path,
    )

    validate_parser.set_defaults(
        func=validate,
    )

    #
    # info
    #

    info_parser = commands.add_parser(
        "info",
        help="Display SongMap information.",
    )

    info_parser.add_argument(
        "input",
        type=Path,
    )

    info_parser.set_defaults(
        func=info,
    )

    #
    # inspect
    #

    inspect_parser = commands.add_parser(
        "inspect",
        help="Inspect a structured timing source (SNG/MIDI/CHART).",
    )

    inspect_parser.add_argument(
        "input",
        type=Path,
    )

    inspect_parser.set_defaults(
        func=inspect,
    )

    #
    # sync-video
    #

    sync_video_parser = commands.add_parser(
        "sync-video",
        help="Synchronize a video with a SongMap (detect video offset).",
    )

    sync_video_parser.add_argument(
        "songmap",
        help="Dataset id/prefix or songmap.json path.",
    )

    sync_video_parser.add_argument(
        "video",
        help="Local video file or YouTube URL.",
    )

    sync_video_parser.add_argument(
        "--offset",
        type=float,
        default=None,
        help="Manual video offset in seconds (overrides detection).",
    )

    sync_video_parser.add_argument(
        "--reference",
        type=Path,
        default=None,
        help="Reference audio the SongMap was built from.",
    )

    sync_video_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Datasets directory (defaults to paths.datasets).",
    )

    sync_video_parser.set_defaults(
        func=sync_video,
    )

    #
    # export
    #

    export_parser = commands.add_parser(
        "export",
        help="Export a dataset.",
    )

    export_parser.add_argument(
        "songmap",
        type=Path,
    )

    export_parser.add_argument(
        "destination",
        type=Path,
    )

    export_parser.set_defaults(
        func=export,
    )

    return parser


def main(
    argv: Sequence[str] | None = None,
) -> int:
    parser = build_parser()

    args = parser.parse_args(argv)

    return cast(int, args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())