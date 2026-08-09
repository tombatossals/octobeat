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

        return self.metadata_for_track(track)

    def metadata_for_track(
        self,
        track: dict[str, Any],
    ) -> DeezerMetadata | None:
        """
        Return enriched metadata for a specific Deezer track.
        """

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

        track_title = track.get("title")

        return DeezerMetadata(
            artist=str(track_artist or ""),
            title=str(track_title or ""),
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

        return self.cover_url_for_track(track)

    def cover_url_for_track(
        self,
        track: dict[str, Any],
    ) -> str | None:
        """
        Return the highest-quality album cover for a Deezer track.
        """

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

    def download_cover_for_track(
        self,
        track: dict[str, Any],
        destination: Path,
    ) -> Path:
        """
        Download the album artwork of a specific Deezer track.
        """

        url = self.cover_url_for_track(
            track,
        )

        if url is None:
            raise FileNotFoundError(
                "No Deezer cover found for the selected track.",
            )

        artist = str(
            (
                track.get("artist")
                or {}
            ).get("name")
            or "unknown"
        )

        download_url(
            url,
            destination,
            description=f"Cover ({artist})",
        )

        return destination

    #
    # Candidates
    #

    def tracks(
        self,
        artist: str,
        title: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Return Deezer track candidates for an artist/title.

        Merges a strict ``artist:``/``track:`` query with a broader
        ``artist:``/``title`` query so live, acoustic, demo and remix
        versions are all surfaced. Results are filtered for relevance
        and ordered by Deezer popularity (``rank``), preferring exact
        artist matches, so the caller can present options to the user.
        """

        merged: dict[object, dict[str, Any]] = {}

        for query in (
            self.search(
                artist,
                title,
                limit=limit * 2,
            )
            + self._search_broad(
                artist,
                title,
                limit=limit * 2,
            )
        ):
            merged[
                query.get("id")
            ] = query

        candidates: list[
            tuple[dict[str, Any], str]
        ] = []

        for track in merged.values():
            kind = _candidate_kind(
                track,
                artist,
                title,
            )

            if kind is not None:
                candidates.append(
                    (track, kind)
                )

        candidates.sort(
            key=lambda item: (
                # Exact artist matches come first.
                0 if item[1] == "exact" else 1,
                # Then most popular first.
                -(int(item[0].get("rank") or 0)),
            ),
        )

        return [
            track
            for track, _kind in candidates[:limit]
        ]

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

        return self._raw_search(
            query,
            limit,
        )

    def _search_broad(
        self,
        artist: str,
        title: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        """
        Search Deezer for the artist and the plain quoted title.
        """

        query = (
            f'artist:"{artist}" '
            f'"{title}"'
        )

        return self._raw_search(
            query,
            limit,
        )

    def _raw_search(
        self,
        query: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        """
        Run a raw Deezer search query.
        """

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


# Palabras vacías que no discriminan versiones de una canción.
_STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "at",
        "for",
        "from",
        "i",
        "in",
        "is",
        "it",
        "me",
        "of",
        "on",
        "or",
        "the",
        "to",
        "with",
        "you",
    }
)


def _title_words(
    text: str,
) -> set[str]:
    """
    Return the significant words of a title.
    """

    return {
        word
        for word in text.lower().split()
        if word not in _STOP_WORDS
    }


def _candidate_kind(
    track: dict[str, Any],
    artist: str,
    title: str,
) -> str | None:
    """
    Classify a Deezer track as an ``exact`` artist match, a ``cover``
    or neither (``None``), based on title relevance.
    """

    track_artist = str(
        (
            track.get("artist")
            or {}
        ).get("name")
        or ""
    ).strip()

    track_title = str(
        track.get("title")
        or ""
    ).strip()

    artist_lower = artist.lower()
    track_artist_lower = track_artist.lower()

    title_lower = title.lower().strip()
    track_title_lower = track_title.lower()

    exact = (
        track_artist_lower == artist_lower
    )

    cover = (
        artist_lower in track_artist_lower
        or track_artist_lower in artist_lower
    )

    if not exact and not cover:
        return None

    substring = (
        title_lower in track_title_lower
        or track_title_lower in title_lower
    )

    overlap = len(
        _title_words(title)
        & _title_words(track_title)
    )

    if not (substring or overlap >= 2):
        return None

    return "exact" if exact else "cover"
