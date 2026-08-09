"""Dataset discovery helpers.

Utilities for listing and locating datasets inside a datasets
directory, shared by the `dataset` commands.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from octobeat.io.resource import (
    CATALOG_FILE,
    COVER_FILE,
    METADATA_FILE,
    SONGMAP_FILE,
)
from octobeat.models.metadata import CatalogMetadata


@dataclass(frozen=True, slots=True)
class DatasetEntry:
    """
    A dataset found in the datasets directory.
    """

    dataset_id: str

    dataset_dir: Path

    metadata: CatalogMetadata | None

    def missing(self) -> list[str]:
        """
        Return the missing essential files/fields of the dataset.

        An empty list means the dataset is complete.
        """

        missing: list[str] = []

        if not (self.dataset_dir / METADATA_FILE).exists():
            missing.append("metadata.json")

        if not (self.dataset_dir / COVER_FILE).exists():
            missing.append("cover.jpg")

        if not (self.dataset_dir / SONGMAP_FILE).exists():
            missing.append("songmap.json")

        if self.metadata is not None:
            if not self.metadata.artist:
                missing.append("artist")

            if not self.metadata.title:
                missing.append("title")

        return missing

    def incomplete(self) -> bool:
        """
        Whether the dataset is known to be incomplete.
        """

        return bool(self.missing())


def list_datasets(
    output: Path,
) -> list[DatasetEntry]:
    """
    Return every dataset directory inside ``output``.

    A directory counts as a dataset when it contains a `metadata.json`
    or a `songmap.json`.
    """

    output = output.expanduser().resolve()

    entries: list[DatasetEntry] = []

    for dataset_dir in sorted(
        output.iterdir(),
    ):
        if not dataset_dir.is_dir():
            continue

        has_metadata = (
            dataset_dir / METADATA_FILE
        ).exists()

        has_songmap = (
            dataset_dir / SONGMAP_FILE
        ).exists()

        if not has_metadata and not has_songmap:
            continue

        metadata = _read_metadata(
            dataset_dir,
        )

        entries.append(
            DatasetEntry(
                dataset_id=dataset_dir.name,
                dataset_dir=dataset_dir,
                metadata=metadata,
            ),
        )

    return entries


def find_dataset(
    output: Path,
    dataset_id: str,
) -> Path | None:
    """
    Locate a dataset directory by id inside ``output``.

    Accepts either the exact id or a unique prefix.
    """

    output = output.expanduser().resolve()

    exact = output / dataset_id

    if exact.is_dir():
        return exact

    matches = [
        entry.dataset_dir
        for entry in list_datasets(output)
        if entry.dataset_id.startswith(
            dataset_id,
        )
    ]

    if len(matches) == 1:
        return matches[0]

    return None


def catalog_path(
    output: Path,
) -> Path:
    """
    Resolve the catalog path inside the datasets directory.
    """

    return (
        output.expanduser().resolve()
        / CATALOG_FILE
    )


def _read_metadata(
    dataset_dir: Path,
) -> CatalogMetadata | None:
    metadata_path = (
        dataset_dir / METADATA_FILE
    )

    if not metadata_path.exists():
        return None

    try:
        return CatalogMetadata.model_validate_json(
            metadata_path.read_text(
                encoding="utf-8",
            ),
        )
    except Exception:
        return None
