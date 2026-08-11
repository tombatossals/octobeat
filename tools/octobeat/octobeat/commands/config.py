from __future__ import annotations

import argparse
import os
import subprocess

from octobeat.config import (
    config_path,
    load_config,
    save_config,
    set_value,
)
from octobeat.ui import console


def run(args: argparse.Namespace) -> int:
    """
    Manage the workspace configuration.
    """

    if args.config_command == "show":
        return _show()

    if args.config_command == "edit":
        return _edit()

    return _set(
        args.key,
        args.value,
    )


def _show() -> int:
    config = load_config()

    console.title("octobeat config")
    console.field(
        "File",
        config_path(),
    )

    console.blank()
    console.section("[paths]")
    console.field(
        "datasets",
        config.paths.datasets,
    )

    console.blank()
    console.section("[download]")
    console.field(
        "audio_format",
        config.download.audio_format,
    )

    console.blank()
    console.section("[catalog]")
    console.field(
        "auto_rebuild",
        str(
            config.catalog.auto_rebuild
        ).lower(),
    )

    return 0


def _edit() -> int:
    path = config_path()

    if not path.exists():
        save_config(
            load_config(),
            path,
        )

    editor = (
        os.environ.get("EDITOR")
        or os.environ.get("VISUAL")
    )

    if not editor:
        console.error(
            "No EDITOR set.",
        )
        return 1

    subprocess.call(
        [
            editor,
            str(path),
        ]
    )

    return 0


def _set(
    key: str,
    value: str,
) -> int:
    config = load_config()

    try:
        updated = set_value(
            config,
            key,
            value,
        )
    except ValueError as exc:
        console.error(
            str(exc),
        )
        return 1

    save_config(updated)

    console.success(
        f"config: {key} = {value}",
    )

    return 0
