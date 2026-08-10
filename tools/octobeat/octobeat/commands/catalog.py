from __future__ import annotations

import argparse
import json
from pathlib import Path

from octobeat.config import ensure_workspace
from octobeat.io.resource import (
    CATALOG_FILE,
    METADATA_FILE,
    SONGMAP_FILE,
    metadata_to_json,
)
from octobeat.models.metadata import CatalogMetadata
from octobeat.ui import console


def run(args: argparse.Namespace) -> int:
    """
    Manage the catalog.
    """

    if args.catalog_command == "build":
        return _build(args)

    if args.catalog_command == "verify":
        return _verify(args)

    if args.catalog_command == "stats":
        return _stats(args)

    console.failure(
        f"catalog {args.catalog_command} is not implemented.",
    )

    return 1


def _build(args: argparse.Namespace) -> int:
    """
    Rebuild catalog.json from the datasets in the output directory.

    Scans every dataset directory (identified by a songmap.json),
    reads its metadata.json and rebuilds the catalog from scratch.
    This is the correct command after adding, moving or removing
    datasets.
    """

    config = ensure_workspace()

    output = (
        args.output.expanduser().resolve()
        if args.output is not None
        else config.datasets_dir()
    )

    catalog_path = (
        args.catalog.expanduser().resolve()
        if args.catalog is not None
        else output / CATALOG_FILE
    )

    entries = _scan_datasets(output)

    # A clean rebuild: write the scanned entries, replacing whatever was
    # in the catalog (so removed datasets disappear). exclude_none keeps
    # absent optional fields out of the document.
    catalog_path.parent.mkdir(parents=True, exist_ok=True)

    catalog_path.write_text(
        json.dumps(
            [
                json.loads(metadata_to_json(entry))
                for entry in entries
            ],
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    console.success(
        f"Catalog rebuilt with {len(entries)} "
        f"dataset{'s' if len(entries) != 1 else ''}.",
    )

    return 0


def _verify(args: argparse.Namespace) -> int:
    """
    Verify that every dataset directory has a catalog entry.
    """

    config = ensure_workspace()

    output = (
        args.output.expanduser().resolve()
        if args.output is not None
        else config.datasets_dir()
    )

    catalog_path = (
        args.catalog.expanduser().resolve()
        if args.catalog is not None
        else output / CATALOG_FILE
    )

    entries = _scan_datasets(output)

    catalog_ids = _catalog_ids(catalog_path)

    missing = [
        entry.id
        for entry in entries
        if entry.id not in catalog_ids
    ]

    stale = [
        dataset_id
        for dataset_id in catalog_ids
        if not (output / dataset_id).is_dir()
    ]

    if missing or stale:
        for dataset_id in missing:
            console.warning(
                f"Dataset '{dataset_id}' is missing from the catalog.",
            )

        for dataset_id in stale:
            console.warning(
                f"Catalog entry '{dataset_id}' has no dataset "
                "directory.",
            )

        return 1

    console.success("Catalog is in sync with the datasets.")

    return 0


def _stats(args: argparse.Namespace) -> int:
    """
    Display catalog statistics.
    """

    config = ensure_workspace()

    output = (
        args.output.expanduser().resolve()
        if args.output is not None
        else config.datasets_dir()
    )

    catalog_path = (
        args.catalog.expanduser().resolve()
        if args.catalog is not None
        else output / CATALOG_FILE
    )

    entries = _scan_datasets(output)
    catalog_ids = _catalog_ids(catalog_path)

    console.field("Datasets", len(entries))
    console.field("Catalog entries", len(catalog_ids))
    console.field("Missing from catalog", len(entries) - len(catalog_ids))

    return 0


def _scan_datasets(output: Path) -> list[CatalogMetadata]:
    """Return the metadata of every dataset directory in ``output``."""

    entries: list[CatalogMetadata] = []

    if not output.is_dir():
        return entries

    for dataset_dir in sorted(output.iterdir()):
        if not dataset_dir.is_dir():
            continue

        songmap_path = dataset_dir / SONGMAP_FILE
        metadata_path = dataset_dir / METADATA_FILE

        if not songmap_path.exists():
            continue

        if not metadata_path.exists():
            continue

        try:
            metadata = CatalogMetadata.model_validate_json(
                metadata_path.read_text(
                    encoding="utf-8",
                ),
            )
        except Exception:
            console.warning(
                f"Could not read metadata for "
                f"'{dataset_dir.name}'.",
            )
            continue

        entries.append(metadata)

    return entries


def _catalog_ids(catalog_path: Path) -> set[str]:
    if not catalog_path.exists():
        return set()

    try:
        entries = json.loads(
            catalog_path.read_text(
                encoding="utf-8",
            ),
        )
    except Exception:
        return set()

    return {
        str(entry["id"])
        for entry in entries
        if isinstance(entry, dict)
    }
