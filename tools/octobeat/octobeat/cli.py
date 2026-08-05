from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from octobeat.commands.analyse import run as analyse
from octobeat.commands.export import run as export
from octobeat.commands.info import run as info
from octobeat.commands.resource import run as resource
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
        func=not_implemented,
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
    ).set_defaults(func=not_implemented)

    config_commands.add_parser(
        "edit",
        help="Edit the configuration file.",
    ).set_defaults(func=not_implemented)

    config_set = config_commands.add_parser(
        "set",
        help="Update a configuration value.",
    )

    config_set.add_argument("key")
    config_set.add_argument("value")

    config_set.set_defaults(
        func=not_implemented,
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

    add_parser.set_defaults(
        func=resource,
    )

    #
    # dataset
    #

    dataset_parser = commands.add_parser(
        "dataset",
        help="Manage datasets.",
    )

    dataset_commands = (
        dataset_parser.add_subparsers(
            dest="dataset_command",
            required=True,
        )
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
    )

    analyse_parser.add_argument(
        "--title",
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

    metadata_commands = (
        metadata_parser.add_subparsers(
            dest="metadata_command",
            required=True,
        )
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
        func=not_implemented,
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

    catalog_commands.add_parser(
        "build",
        help="Build catalog.json.",
    ).set_defaults(func=not_implemented)

    catalog_commands.add_parser(
        "verify",
        help="Verify the catalog.",
    ).set_defaults(func=not_implemented)

    catalog_commands.add_parser(
        "stats",
        help="Display catalog statistics.",
    ).set_defaults(func=not_implemented)

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

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())