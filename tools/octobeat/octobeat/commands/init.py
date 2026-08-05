from __future__ import annotations

import argparse

from octobeat.config import (
    config_path,
    ensure_workspace,
)
from octobeat.ui import console


def run(args: argparse.Namespace) -> int:
    """
    Initialize the OctoBeat workspace.
    """

    config = ensure_workspace()

    console.title("octobeat init")

    console.field(
        "Config",
        config_path(),
    )

    console.field(
        "Datasets",
        config.datasets_dir(),
    )

    console.blank()
    console.success(
        "Workspace initialized.",
    )

    return 0
