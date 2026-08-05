from __future__ import annotations

import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from tqdm import tqdm


@contextmanager
def download_bar(
    total: int | None = None,
    description: str = "Downloading",
) -> Iterator[tqdm]:
    """
    Yield a tqdm progress bar for a download.
    """

    bar = tqdm(
        total=total,
        desc=description,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        leave=True,
    )

    try:
        yield bar
    finally:
        bar.close()


def yt_dlp_progress_hook(
    bar: Any,
) -> Any:
    """
    Build a yt-dlp progress hook that drives a tqdm bar.
    """

    def hook(data: dict[str, Any]) -> None:
        status = data.get("status")

        if status == "downloading":
            total = (
                data.get("total_bytes")
                or data.get("total_bytes_estimate")
                or 0
            )
            downloaded = (
                data.get("downloaded_bytes")
                or 0
            )

            if total:
                bar.total = total

            bar.update(downloaded - bar.n)

        elif status == "finished":
            bar.n = bar.total or bar.n
            bar.refresh()
            bar.close()

    return hook


def download_url(
    url: str,
    destination: Path,
    description: str = "Downloading",
) -> Path:
    """
    Stream a URL into `destination`, reporting progress.
    """

    destination = destination.expanduser().resolve()
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with urllib.request.urlopen(url) as response:
        content_length = (
            response.headers.get(
                "Content-Length",
            )
        )

        total = (
            int(content_length)
            if content_length
            else None
        )

        with download_bar(
            total,
            description,
        ) as bar:
            with destination.open("wb") as out:
                while True:
                    chunk = response.read(
                        65536,
                    )

                    if not chunk:
                        break

                    out.write(chunk)
                    bar.update(
                        len(chunk),
                    )

    return destination
