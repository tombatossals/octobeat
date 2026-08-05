from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from octobeat.ui.progress import download_url

_SEARCH_URL = "https://api.deezer.com/search"
_ALBUM_URL = "https://api.deezer.com/album"

# El CDN de Deezer sirve hasta 1200x1200. La URL cover_xl viene a
# 1000x1000; la pedimos a 1200x1200 sustituyendo el sufijo.
_COVER_SIZE = "1200x1200"


@dataclass(frozen=True)
class DeezerMetadata:
    """
    Metadata enriched from Deezer for a recording.
    """

    artist: str

    title: str

    album: str | None = None

    year: int | None = None

    genres: list[str] = field(
        default_factory=list,
    )

    tags: list[str] = field(
        default_factory=list,
    )


class DeezerProvider:
    """
    Enrichment provider backed by the public Deezer API.

    Resolves a recording into rich catalogue metadata (album, year,
    genres, tags) and provides the square album artwork.
    """

    def __init__(self) -> None:
        self._track: dict[str, Any] | None = None
        self._album: dict[str, Any] | None = None

    #
    # Metadata
    #

    def metadata(
        self,
        artist: str,
        title: str,
    ) -> DeezerMetadata | None:
        """
        Return enriched metadata for the given recording.
        """

        track = self._best_track(
            artist,
            title,
        )

        if track is None:
            return None

        album_info = (
            track.get("album")
            or {}
        )

        album_details = (
            self._album_details(track)
            or album_info
        )

        genres = [
            str(genre.get("name"))
            for genre in (
                album_details.get("genres")
                or {}
            ).get("data")
            or []
            if genre.get("name")
        ]

        release_date = (
            album_details.get("release_date")
            or album_info.get("release_date")
        )

        track_artist = (
            track.get("artist")
            or {}
        ).get("name")

        return DeezerMetadata(
            artist=str(track_artist or artist),
            title=str(
                track.get("title")
                or title
            ),
            album=(
                str(
                    album_details.get("title")
                    or album_info.get("title")
                )
                or None
            ),
            year=_parse_year(release_date),
            genres=genres,
            tags=[
                genre.lower()
                for genre in genres
            ],
        )

    #
    # Cover artwork
    #

    def cover_url(
        self,
        artist: str,
        title: str,
    ) -> str | None:
        """
        Return the URL of the highest-quality album cover.
        """

        track = self._best_track(
            artist,
            title,
        )

        if track is None:
            return None

        cover = (
            track.get("album")
            or {}
        ).get("cover_xl")

        if not isinstance(cover, str):
            return None

        return self._max_size_url(cover)

    def download_cover(
        self,
        artist: str,
        title: str,
        destination: Path,
    ) -> Path:
        """
        Download the album artwork to `destination`.
        """

        url = self.cover_url(
            artist,
            title,
        )

        if url is None:
            raise FileNotFoundError(
                f"No Deezer cover found for "
                f"{artist} - {title}.",
            )

        download_url(
            url,
            destination,
            description=f"Cover ({artist})",
        )

        return destination

    #
    # API
    #

    def search(
        self,
        artist: str,
        title: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Search Deezer for the best-matching tracks.
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

        payload = self._get_json(url)

        return list(
            payload.get("data")
            or []
        )

    #
    # Internals
    #

    def _best_track(
        self,
        artist: str,
        title: str,
    ) -> dict[str, Any] | None:
        """
        Return the best-matching track, cached per instance.
        """

        if self._track is not None:
            return self._track

        self._track = self._pick_track(
            self.search(
                artist,
                title,
            ),
            artist,
        )

        return self._track

    def _album_details(
        self,
        track: dict[str, Any],
    ) -> dict[str, Any] | None:
        """
        Fetch the album document, cached per instance.

        The album document is the only source of genres on the
        public Deezer API.
        """

        album_id = (
            track.get("album")
            or {}
        ).get("id")

        if not album_id:
            return None

        if (
            self._album is not None
            and self._album.get("id") == album_id
        ):
            return self._album

        try:
            self._album = self._get_json(
                f"{_ALBUM_URL}/{album_id}",
            )
        except Exception:
            self._album = None

        return self._album

    @staticmethod
    def _pick_track(
        tracks: list[dict[str, Any]],
        artist: str,
    ) -> dict[str, Any] | None:
        """
        Prefer an exact artist match over the first result.
        """

        if not tracks:
            return None

        exact = [
            track
            for track in tracks
            if str(
                (
                    track.get("artist")
                    or {}
                ).get("name")
                or ""
            ).lower()
            == artist.lower()
        ]

        return (
            exact[0]
            if exact
            else tracks[0]
        )

    @staticmethod
    def _get_json(
        url: str,
    ) -> dict[str, Any]:
        with urllib.request.urlopen(url) as response:
            payload = json.loads(
                response.read().decode(
                    "utf-8",
                )
            )

        if not isinstance(payload, dict):
            raise ValueError(
                "Invalid Deezer response.",
            )

        return payload

    @staticmethod
    def _max_size_url(
        cover_url: str,
    ) -> str:
        """
        Request the maximum CDN size for a Deezer cover URL.
        """

        if "/1000x1000" in cover_url:
            return cover_url.replace(
                "/1000x1000",
                f"/{_COVER_SIZE}",
            )

        return cover_url


def _parse_year(
    release_date: object,
) -> int | None:
    """
    Extract the year from an ISO release date.
    """

    if not isinstance(
        release_date,
        str,
    ):
        return None

    match = re.match(
        r"(\d{4})",
        release_date,
    )

    if match is None:
        return None

    return int(match.group(1))
