from __future__ import annotations

import argparse
import traceback
from pathlib import Path

from octobeat.charts import (
    _normalise,
    chart_search_dirs,
)
from octobeat.config import (
    ensure_workspace,
)
from octobeat.config.model import Config
from octobeat.io.resource import CATALOG_FILE
from octobeat.pipeline import build_dataset
from octobeat.ui import console


def run(args: argparse.Namespace) -> int:
    """
    Build a complete dataset from a source.
    """

    config = ensure_workspace()

    try:
        input_source = _resolve_source(
            _strip_surrounding_quotes(
                args.input,
            ),
            config=config,
        )
    except SourceNotFoundError as error:
        _report_source_not_found(error)
        return 1

    output = (
        args.output.expanduser().resolve()
        if args.output is not None
        else config.datasets_dir()
    )

    catalog = (
        args.catalog.expanduser().resolve()
        if args.catalog is not None
        else output / CATALOG_FILE
    )

    try:
        result = build_dataset(
            input_source,
            output=output,
            catalog=catalog,
            dataset_id=args.id,
            include_cover=(
                not args.no_cover
            ),
            update_catalog=(
                config.catalog.auto_rebuild
            ),
            offset=args.offset,
        )
    except Exception:
        traceback.print_exc()
        return 1

    resources: list[tuple[str, object]] = [
        ("Audio", result.audio),
    ]

    if result.cover_source is not None:
        resources.append(
            ("Cover", result.cover_source),
        )

    console.table_report(
        [
            (
                "Dataset",
                [
                    ("Artist", result.artist or "-"),
                    ("Title", result.title or "-"),
                ],
            ),
            (
                "Resources",
                resources,
            ),
            (
                "Analysis",
                [
                    ("Duration", f"{result.duration:.1f} s"),
                    ("Tempo", f"{result.bpm:.0f} BPM"),
                    ("Beats", result.beats),
                    (
                        "Confidence",
                        f"{result.confidence:.2f}",
                    ),
                ],
            ),
            (
                "Output",
                [
                    ("Dataset", result.dataset_dir),
                    ("SongMap", result.songmap_path),
                    ("Metadata", result.metadata_path),
                    ("Catalog", result.catalog_path),
                    (
                        "Catalog entries",
                        result.catalog_entries,
                    ),
                ],
            ),
        ],
    )

    console.success(
        "Dataset built.",
    )

    return 0


_QUOTES = {
    '"',
    "'",
    "\u201c",  # "
    "\u201d",  # "
    "\u2018",  # '
    "\u2019",  # '
}


def _strip_surrounding_quotes(
    value: str,
) -> str:
    """
    Remove surrounding quote characters (straight or typographic)
    that may have been copied along with the argument.
    """

    stripped = value.strip()

    while (
        len(stripped) >= 2
        and stripped[0] in _QUOTES
        and stripped[-1] in _QUOTES
    ):
        stripped = stripped[1:-1].strip()

    return stripped


class SourceNotFoundError(Exception):
    """
    Raised when a local source or chart file cannot be located.

    Carries the directories that were searched and any charts with a
    similar name, so the error can be reported helpfully.
    """

    def __init__(
        self,
        source: str,
        *,
        searched_dirs: list[Path],
        candidates: list[Path] | None = None,
    ) -> None:
        super().__init__(source)
        self.source = source
        self.searched_dirs = list(searched_dirs)
        self.candidates = list(candidates or [])


def _resolve_source(
    source: str,
    *,
    config: Config,
) -> str:
    """
    Resolve a source argument to a filesystem path.

    When the value is an existing path it is returned as-is. Otherwise
    the source is treated as a bare chart file name and looked up in
    the configured charts directories (falling back to the repo's
    ``sng/`` directory).

    When a local file or chart cannot be located, a
    :class:`SourceNotFoundError` is raised carrying the searched
    directories and any similarly-named charts.
    """

    path = Path(source).expanduser()

    if path.exists():
        return str(path)

    dirs = chart_search_dirs(config)

    for directory in dirs:
        candidate = directory / source

        if candidate.is_file():
            return str(candidate)

    if _looks_like_local_file(source):
        raise SourceNotFoundError(
            source,
            searched_dirs=dirs,
            candidates=_similar_charts(
                source,
                config=config,
            ),
        )

    return source


def _looks_like_local_file(source: str) -> bool:
    """
    Whether ``source`` references a local file rather than a remote
    resource (URL or bare search term).
    """

    if source.startswith(("http://", "https://")):
        return False

    path = Path(source)

    if path.suffix:
        return True

    return "/" in source or "\\" in source


def _similar_charts(
    source: str,
    *,
    config: Config,
) -> list[Path]:
    """
    Find charts whose normalised name contains every meaningful token
    of ``source``, so a mistyped or mangled file name still surfaces
    the intended chart.
    """

    needles = [
        token
        for token in _normalise(
            Path(source).stem,
        ).split()
        if len(token) >= 3
    ]

    if not needles:
        return []

    matches: list[Path] = []

    for directory in chart_search_dirs(config):
        if not directory.is_dir():
            continue

        for pattern in (
            "*.sng",
            "*.mid",
            "*.chart",
        ):
            for path in sorted(
                directory.glob(pattern)
            ):
                if all(
                    needle in _normalise(path.stem)
                    for needle in needles
                ):
                    matches.append(path)

    return matches[:5]


def _report_source_not_found(
    error: SourceNotFoundError,
) -> None:
    console.error(
        f"Source not found: {error.source}",
    )

    console.info("")

    console.info(
        "Searched directories:",
    )

    for directory in error.searched_dirs:
        console.info(
            f"  {directory}",
        )

    if error.candidates:
        console.info("")

        console.info(
            "Similar charts found:",
        )

        for candidate in error.candidates:
            console.info(
                f"  {candidate}",
            )
