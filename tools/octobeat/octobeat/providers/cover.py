from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

_SEARCH_URL = "https://api.deezer.com/search"

# El CDN de Deezer sirve hasta 1200x1200. La URL cover_xl viene
# a 1000x1000; la pedimos a 1200x1200 sustituyendo el sufijo.
_COVER_SIZE = "1200x1200"
_COVER_URL_SUFFIX = "-000000-80-0-0.jpg"


class DeezerCoverProvider:
    """
    Album cover provider backed by the public Deezer API.

    Searches by artist + track and downloads the square album
    artwork at the maximum resolution the Deezer CDN provides.
    """

    def search(
        self,
        artist: str,
        title: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Return the best-matching Deezer tracks for a recording.
        """

        query = (
            f'artist:"{artist}" '
            f'track:"{title}"'
        )

        url = (
            f"{_SEARCH_URL}?q="
            f"{urllib.parse.quote(query)}"
            f"&limit={limit}"
        )

        with urllib.request.urlopen(url) as response:
            payload = json.loads(
                response.read().decode(
                    "utf-8",
                ),
            )

        return list(payload.get("data") or [])

    def download(
        self,
        artist: str,
        title: str,
        destination: Path,
    ) -> Path:
        """
        Download the highest-quality album cover to `destination`.
        """

        tracks = self.search(artist, title)

        if not tracks:
            raise FileNotFoundError(
                f"No Deezer cover found for "
                f"{artist} - {title}.",
            )

        cover_xl = self._pick_cover(tracks)

        if not cover_xl:
            raise FileNotFoundError(
                f"No album cover available for "
                f"{artist} - {title}.",
            )

        destination = destination.expanduser().resolve()
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        urllib.request.urlretrieve(
            self._max_size_url(cover_xl),
            destination,
        )

        return destination

    #
    # Internals
    #

    @staticmethod
    def _pick_cover(tracks: list[dict[str, Any]]) -> str | None:
        """
        Prefer the album cover of the exact artist match.
        """

        for track in tracks:
            artist_name = (
                track.get("artist") or {}
            ).get("name")

            if not artist_name:
                continue

            album = track.get("album") or {}

            cover = album.get("cover_xl")

            if isinstance(cover, str):
                return cover

        return None

    @staticmethod
    def _max_size_url(cover_url: str) -> str:
        """
        Request the maximum CDN size for a Deezer cover URL.
        """

        if "/1000x1000" in cover_url:
            return cover_url.replace(
                "/1000x1000",
                f"/{_COVER_SIZE}",
            )

        return cover_url
